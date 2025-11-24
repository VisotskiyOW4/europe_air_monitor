from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from datetime import timedelta
import numpy as np
import joblib
from monitoring.ml.ml_utils import (
    load_lstm_model,
    prepare_lstm_data,
)
from monitoring.ml.scalers import load_scaler

from monitoring.air.models import AirQualityStation, AirQualityRecord
from monitoring.water.models import WaterQualityStation, WaterQualityRecord
from monitoring.soil.models import SoilQualityStation, SoilQualityRecord
from monitoring.radiation.models import RadiationStation, RadiationRecord

from monitoring.utils.forecast import lstm_forecast

from monitoring.utils.fuzzy_logic import (
    calc_air_risk,
    calc_water_risk,
    calc_soil_risk,
    calc_radiation_risk,
)

from monitoring.utils.forecast_ml import (
    forecast_air,
    forecast_water,
    forecast_soil,
    forecast_radiation,
)

# ==============================================================
#  GLOBAL DATA API + DATE FILTER
# ==============================================================

def api_global(request):

    selected_date = request.GET.get("date", None)

    result = {"air": [], "water": [], "soil": [], "radiation": []}

    # Універсальна функція пошуку запису по даті/або останнього
    from datetime import datetime

    def get_record_by_date(model, station, selected_date):
        qs = model.objects.filter(station=station)

        from datetime import datetime

        if selected_date:
            d = None

            # формат YYYY-MM-DD
            try:
                d = datetime.strptime(selected_date, "%Y-%m-%d").date()
            except:
                pass

            # формат DD.MM.YYYY
            if d is None:
                try:
                    d = datetime.strptime(selected_date, "%d.%m.%Y").date()
                except:
                    pass

            if d:
                rec = qs.filter(timestamp__date=d).order_by('-timestamp').first()
                if rec:
                    return rec

        return qs.order_by('-timestamp').first()

    # Універсальна функція додавання в результат
    def add_data(category, station, record, fields, fuzzy_func):
        data = {f: getattr(record, f) for f in fields}
        fuzzy = fuzzy_func(data)
        result[category].append({
            "id": station.id,
            "name": station.name,
            "lat": station.latitude,
            "lon": station.longitude,
            **data,
            "risk_score": fuzzy["risk_score"],
            "risk_label": fuzzy["risk_label"],
            "timestamp": record.timestamp,
        })

    # AIR
    for s in AirQualityStation.objects.all():
        r = get_record_by_date(AirQualityRecord, s, selected_date)
        if r:
            add_data("air", s, r, ["pm25", "pm10", "co", "no2", "o3"], calc_air_risk)

    # WATER
    for s in WaterQualityStation.objects.all():
        r = get_record_by_date(WaterQualityRecord, s, selected_date)
        if r:
            add_data("water", s, r, ["ph", "nitrates", "conductivity"], calc_water_risk)

    # SOIL
    for s in SoilQualityStation.objects.all():
        r = get_record_by_date(SoilQualityRecord, s, selected_date)
        if r:
            add_data("soil", s, r, ["heavy_metals", "pesticides", "ph"], calc_soil_risk)

    # RADIATION
    for s in RadiationStation.objects.all():
        r = get_record_by_date(RadiationRecord, s, selected_date)
        if r:
            add_data("radiation", s, r,
                     ["gamma", "beta", "alpha", "ambient_dose_rate"],
                     calc_radiation_risk)

    return JsonResponse(result)


# ==============================================================
#  HISTORY DATA API (для графіку)
# ==============================================================

def api_history(request, category, station_id):
    model_map = {
        "air": (AirQualityStation, AirQualityRecord),
        "water": (WaterQualityStation, WaterQualityRecord),
        "soil": (SoilQualityStation, SoilQualityRecord),
        "radiation": (RadiationStation, RadiationRecord),
    }

    if category not in model_map:
        return JsonResponse({"error": "Unknown category"}, status=400)

    StationModel, RecordModel = model_map[category]
    station = get_object_or_404(StationModel, id=station_id)

    records = RecordModel.objects.filter(station=station).order_by("timestamp")

    data = []
    for r in records:
        entry = {"timestamp": r.timestamp}
        for field in RecordModel._meta.get_fields():
            if field.name not in ["id", "station", "timestamp", "risk_label"]:
                try:
                    value = getattr(r, field.name)
                    if isinstance(value, (int, float)):
                        entry[field.name] = value
                except:
                    pass
        data.append(entry)

    return JsonResponse({"station": station.name, "history": data})


# ==============================================================
#  FORECAST API (LSTM)
# ==============================================================

def api_forecast(request, category, station_id):
    """
    API прогнозу на основі натренованих моделей
    Підтримує параметр days: ?days=3,7,30
    """

    # Зчитуємо параметр "days"
    try:
        days = int(request.GET.get("days", 3))
        if days not in [3, 7, 30]:
            return HttpResponseBadRequest("Invalid 'days' parameter")
    except:
        return HttpResponseBadRequest("Invalid 'days' parameter")

    # Відповідність категорій та моделей
    model_map = {
        "air": {
            "station": AirQualityStation,
            "record": AirQualityRecord,
            "fields": ["pm25", "pm10"],
            "model": "air_lstm"
        },
        "water": {
            "station": WaterQualityStation,
            "record": WaterQualityRecord,
            "fields": ["ph", "nitrates"],
            "model": "water_gru"
        },
        "soil": {
            "station": SoilQualityStation,
            "record": SoilQualityRecord,
            "fields": ["heavy_metals", "pesticides"],
            "model": "soil_rf"
        },
        "radiation": {
            "station": RadiationStation,
            "record": RadiationRecord,
            "fields": ["ambient_dose_rate"],
            "model": "radiation_lstm"
        }
    }

    if category not in model_map:
        return JsonResponse({"error": "Unknown category"}, status=400)

    cfg = model_map[category]

    # Отримуємо станцію та її записи
    StationModel = cfg["station"]
    RecordModel = cfg["record"]
    fields = cfg["fields"]

    station = get_object_or_404(StationModel, id=station_id)
    records = RecordModel.objects.filter(station=station).order_by("timestamp")

    if not records.exists():
        return JsonResponse({"error": "No data for station"}, status=404)

    # ------------------------------------------------------------
    # Завантаження моделі та scaler
    # ------------------------------------------------------------
    model_name = cfg["model"]
    model_path = f"monitoring/ml/models/{category}/{model_name}.keras"
    scaler_path = f"monitoring/ml/models/{category}/{model_name}_scaler.pkl"

    try:
        model = load_lstm_model(model_path) if "lstm" in model_name else joblib.load(model_path)
    except Exception as e:
        return JsonResponse({"error": f"Cannot load model: {e}"} , status=500)

    try:
        scaler = load_scaler(scaler_path)
    except:
        scaler = None

    # ------------------------------------------------------------
    # Формуємо вектор останніх значень
    # ------------------------------------------------------------
    values = np.array([[float(getattr(r, f)) for f in fields] for r in records])

    # Масштабування
    if scaler:
        values_scaled = scaler.transform(values)
    else:
        values_scaled = values

    # ------------------------------------------------------------
    # Прогноз
    # ------------------------------------------------------------
    if "rf" in model_name:  
        # Random Forest (soil)
        last_vec = values_scaled[-1]
        forecasts = []
        for i in range(days):
            pred = model.predict([last_vec])[0]
            last_vec = pred  
            forecasts.append(pred.tolist())

    else:
        # LSTM / GRU
        X = prepare_lstm_data(values_scaled, seq_len=30)
        X_last = X[-1].reshape(1, X.shape[1], X.shape[2])

        preds = model.predict(X_last)[0]  # прогноз довжини N
        forecasts = []

        for i in range(days):
            idx = min(i, len(preds) - 1)
            forecasts.append(preds[idx].tolist())

    # ------------------------------------------------------------
    # Денормалізація
    # ------------------------------------------------------------
    if scaler:
        forecasts_unscaled = scaler.inverse_transform(forecasts).tolist()
    else:
        forecasts_unscaled = forecasts

    # ------------------------------------------------------------
    # Генеруємо майбутні timestamps
    # ------------------------------------------------------------
    last_ts = records.last().timestamp
    timestamps = [(last_ts + timedelta(days=i+1)).isoformat() for i in range(days)]

    return JsonResponse({
        "station": station.name,
        "fields": fields,
        "timestamps": timestamps,
        "values": forecasts_unscaled
    })

