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

    # --- 🔥 новий параметр в API --- 
    window = int(request.GET.get("window", 30))  # 30 днів за замовчуванням

    last_point = (
        RecordModel.objects.filter(station=station)
        .order_by("-timestamp")
        .first()
    )

    if not last_point:
        return JsonResponse({"station": station.name, "history": []})

    start_date = last_point.timestamp - timedelta(days=window)

    records = (
        RecordModel.objects.filter(station=station, timestamp__gte=start_date)
        .order_by("timestamp")
    )

    window = int(request.GET.get("window", 0))

    records = RecordModel.objects.filter(station=station).order_by("timestamp")

    if window > 0:
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=window)
        records = records.filter(timestamp__gte=cutoff)

    data = []
    for r in records:
        entry = {"timestamp": r.timestamp}
        for field in RecordModel._meta.get_fields():
            if field.name not in ["id", "station", "timestamp", "risk_label"]:
                try:
                    val = getattr(r, field.name)
                    if isinstance(val, (int, float)):
                        entry[field.name] = val
                except:
                    pass
        data.append(entry)

    return JsonResponse({"station": station.name, "history": data})

# ==============================================================
#  FORECAST API (LSTM)
# ==============================================================

def api_forecast(request, category, station_id):
    model_map = {
        "air": (AirQualityStation, AirQualityRecord, ["pm25"]),
        "water": (WaterQualityStation, WaterQualityRecord, ["nitrates"]),
        "soil": (SoilQualityStation, SoilQualityRecord, ["heavy_metals"]),
        "radiation": (RadiationStation, RadiationRecord, ["ambient_dose_rate"]),
    }

    if category not in model_map:
        return JsonResponse({"error": "Unknown category"}, status=400)

    StationModel, RecordModel, fields = model_map[category]
    station = get_object_or_404(StationModel, id=station_id)

    # --- новий параметр ---
    days = int(request.GET.get("days", 7))  # 7 днів за замовчуванням
    steps = days * 24  # щогодинний прогноз

    values = (
        RecordModel.objects.filter(station=station)
        .order_by("timestamp")
        .values_list(fields[0], flat=True)
    )

    values = np.array(values).reshape(-1, 1)

    if len(values) < 60:
        return JsonResponse({"error": "Недостатньо даних"}, status=400)

    # load scaler + model
    scaler = load_scaler(category)
    model = load_lstm_model(category)

    scaled = scaler.transform(values)

    window = scaled[-60:].reshape(1, 60, 1)

    preds = []
    last_ts = (
        RecordModel.objects.filter(station=station)
        .order_by("timestamp")
        .last()
        .timestamp
    )

    timestamps = []

    for i in range(steps):
        p = model.predict(window, verbose=0)
        preds.append(p[0][0])

        # update sliding window
        window = np.append(window[:, 1:, :], [[p]], axis=1)

        timestamps.append(last_ts + timedelta(hours=i + 1))

    preds = scaler.inverse_transform(np.array(preds).reshape(-1, 1)).flatten()

    return JsonResponse({
        "param": fields[0],
        "timestamps": timestamps,
        "values": preds.tolist(),
    })


