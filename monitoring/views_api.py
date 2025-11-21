from django.http import JsonResponse
from django.shortcuts import get_object_or_404

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


def api_global(request):
    # Отримуємо ?date=YYYY-MM-DD
    selected_date = request.GET.get("date", None)

    result = {
        "air": [],
        "water": [],
        "soil": [],
        "radiation": []
    }

    # Універсальна функція фільтрації по даті
    def get_record_or_last(model, station):
        qs = model.objects.filter(station=station)

        if selected_date:
            rec = qs.filter(timestamp__date=selected_date).order_by('-timestamp').first()
            if rec:
                return rec

        # Якщо немає записів за дату — повертаємо останній
        return qs.order_by('-timestamp').first()

    # =========================================
    # AIR QUALITY
    # =========================================
    for s in AirQualityStation.objects.all():
        r = get_record_or_last(AirQualityRecord, s)
        if r:
            data = {
                "pm25": r.pm25,
                "pm10": r.pm10,
                "co": r.co,
                "no2": r.no2,
                "o3": r.o3,
            }
            fuzzy = calc_air_risk(data)
            result["air"].append({
                "id": s.id,
                "name": s.name,
                "lat": s.latitude,
                "lon": s.longitude,
                **data,
                "risk_score": fuzzy["risk_score"],
                "risk_label": fuzzy["risk_label"],
                "timestamp": r.timestamp,
            })

    # =========================================
    # WATER QUALITY
    # =========================================
    for s in WaterQualityStation.objects.all():
        r = get_record_or_last(WaterQualityRecord, s)
        if r:
            data = {
                "ph": r.ph,
                "nitrates": r.nitrates,
                "conductivity": r.conductivity,
            }
            fuzzy = calc_water_risk(data)
            result["water"].append({
                "id": s.id,
                "name": s.name,
                "lat": s.latitude,
                "lon": s.longitude,
                **data,
                "risk_score": fuzzy["risk_score"],
                "risk_label": fuzzy["risk_label"],
                "timestamp": r.timestamp,
            })

    # =========================================
    # SOIL QUALITY
    # =========================================
    for s in SoilQualityStation.objects.all():
        r = get_record_or_last(SoilQualityRecord, s)
        if r:
            data = {
                "heavy_metals": r.heavy_metals,
                "pesticides": r.pesticides,
                "ph": r.ph,
            }
            fuzzy = calc_soil_risk(data)
            result["soil"].append({
                "id": s.id,
                "name": s.name,
                "lat": s.latitude,
                "lon": s.longitude,
                **data,
                "risk_score": fuzzy["risk_score"],
                "risk_label": fuzzy["risk_label"],
                "timestamp": r.timestamp,
            })

    # =========================================
    # RADIATION MONITORING
    # =========================================
    for s in RadiationStation.objects.all():
        r = get_record_or_last(RadiationRecord, s)
        if r:
            data = {
                "gamma": r.gamma,
                "beta": r.beta,
                "alpha": r.alpha,
                "ambient_dose_rate": r.ambient_dose_rate
            }
            fuzzy = calc_radiation_risk(data)
            result["radiation"].append({
                "id": s.id,
                "name": s.name,
                "lat": s.latitude,
                "lon": s.longitude,
                **data,
                "risk_score": fuzzy["risk_score"],
                "risk_label": fuzzy["risk_label"],
                "timestamp": r.timestamp,
            })

    return JsonResponse(result, safe=False)


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

    # ВАЖЛИВО: видаляємо лишні пробіли
    station_name = station_name.strip()

    # Пошук станції
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

    return JsonResponse({"station": station_name, "history": data})

