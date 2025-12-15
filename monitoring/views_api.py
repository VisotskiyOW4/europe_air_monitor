from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from datetime import timedelta
import numpy as np

from monitoring.air.models import AirQualityStation, AirQualityRecord
from monitoring.water.models import WaterQualityStation, WaterQualityRecord
from monitoring.soil.models import SoilQualityStation, SoilQualityRecord
from monitoring.radiation.models import RadiationStation, RadiationRecord

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

    from datetime import datetime

    def get_record_by_date(model, station, selected_date):
        qs = model.objects.filter(station=station)

        if selected_date:
            d = None
            try:
                d = datetime.strptime(selected_date, "%Y-%m-%d").date()
            except:
                pass

            if d is None:
                try:
                    d = datetime.strptime(selected_date, "%d.%m.%Y").date()
                except:
                    pass

            if d:
                rec = qs.filter(timestamp__date=d).order_by("-timestamp").first()
                if rec:
                    return rec

        return qs.order_by("-timestamp").first()

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

    for s in AirQualityStation.objects.all():
        r = get_record_by_date(AirQualityRecord, s, selected_date)
        if r:
            add_data("air", s, r, ["pm25", "pm10", "co", "no2", "o3"], calc_air_risk)

    for s in WaterQualityStation.objects.all():
        r = get_record_by_date(WaterQualityRecord, s, selected_date)
        if r:
            add_data("water", s, r, ["ph", "nitrates", "conductivity"], calc_water_risk)

    for s in SoilQualityStation.objects.all():
        r = get_record_by_date(SoilQualityRecord, s, selected_date)
        if r:
            add_data("soil", s, r, ["heavy_metals", "pesticides", "ph"], calc_soil_risk)

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
        "air": (AirQualityStation, AirQualityRecord, "pm25"),
        "water": (WaterQualityStation, WaterQualityRecord, "nitrates"),
        "soil": (SoilQualityStation, SoilQualityRecord, "heavy_metals"),
        "radiation": (RadiationStation, RadiationRecord, "ambient_dose_rate"),
    }

    if category not in model_map:
        return JsonResponse({"error": "Unknown category"}, status=400)

    StationModel, RecordModel, field = model_map[category]
    station = get_object_or_404(StationModel, id=station_id)

    window = int(request.GET.get("window", 7))
    date_str = request.GET.get("date")

    qs = RecordModel.objects.filter(station=station)
    if not qs.exists():
        return JsonResponse({"param": field, "timestamps": [], "values": []})

    # end_date
    if date_str:
        end_date = parse_date(date_str)
        if end_date:
            qs = qs.filter(timestamp__date__lte=end_date)
        else:
            end_date = qs.latest("timestamp").timestamp.date()
    else:
        end_date = qs.latest("timestamp").timestamp.date()

    # ✅ Вікно "N днів включно"
    start_date = end_date - timedelta(days=max(window - 1, 0))

    qs = qs.filter(timestamp__date__gte=start_date).order_by("timestamp")

    return JsonResponse({
        "param": field,
        "timestamps": list(qs.values_list("timestamp", flat=True)),
        "values": list(qs.values_list(field, flat=True)),
    })


# ==============================================================
#  FORECAST API (використовує forecast_ml.py)
# ==============================================================

def api_forecast(request, category, station_id):
    model_map = {
        "air": (AirQualityStation, AirQualityRecord, "pm25"),
        "water": (WaterQualityStation, WaterQualityRecord, "nitrates"),
        "soil": (SoilQualityStation, SoilQualityRecord, "heavy_metals"),
        "radiation": (RadiationStation, RadiationRecord, "ambient_dose_rate"),
    }

    if category not in model_map:
        return JsonResponse({"error": "Unknown category"}, status=400)

    StationModel, RecordModel, field = model_map[category]
    station = get_object_or_404(StationModel, id=station_id)

    days = int(request.GET.get("days", 7))  # 3/7/30
    points_per_day = 4  # у тебе виміри кожні 6 годин => 4 точки/доба
    step_hours = 6

    qs = RecordModel.objects.filter(station=station).order_by("timestamp")

    if not qs.exists():
        return JsonResponse({"error": "Немає даних"}, status=400)

    last_ts = qs.last().timestamp

    # беремо значення параметра
    values = list(qs.values_list(field, flat=True))

    # -------------------------
    # викликаємо правильний прогноз
    # -------------------------
    if category == "air":
        preds = forecast_air(values, days, points_per_day=points_per_day)

    elif category == "water":
        preds = forecast_water(values, days, points_per_day=points_per_day)

    elif category == "radiation":
        preds = forecast_radiation(values, days, points_per_day=points_per_day)

    elif category == "soil":
        # для soil твій forecast_soil інший (по днях, не по 6 годинах)
        last = qs.last()
        last_index = qs.count() - 1
        preds = forecast_soil(
            last_heavy_metals=last.heavy_metals,
            last_pesticides=last.pesticides,
            last_index=last_index,
            days=days,
        )
        # timestamps для soil: 1 точка = 1 день
        timestamps = [last_ts + timedelta(days=i) for i in range(1, len(preds) + 1)]
        return JsonResponse({
            "param": "ph",              # якщо в soil прогнозуєш pH
            "timestamps": timestamps,
            "values": preds,
        })

    # timestamps для air/water/radiation: кожні 6 годин
    timestamps = [last_ts + timedelta(hours=step_hours * (i + 1)) for i in range(len(preds))]

    return JsonResponse({
        "param": field,
        "timestamps": timestamps,
        "values": preds,
        "meta": {
            "days": days,
            "points": len(preds),
            "step_hours": step_hours,
            "mode": "forecast_ml"
        }
    })