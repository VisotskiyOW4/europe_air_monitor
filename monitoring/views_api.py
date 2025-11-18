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
    result = {
        "air": [],
        "water": [],
        "soil": [],
        "radiation": []
    }

    # -------------------------------
    # AIR QUALITY
    # -------------------------------
    for s in AirQualityStation.objects.all():
        last = AirQualityRecord.objects.filter(station=s).order_by('-timestamp').first()

        if last:
            data = {
                "pm25": last.pm25,
                "pm10": last.pm10,
                "co": last.co,
                "no2": last.no2,
                "o3": last.o3,
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
                "timestamp": last.timestamp,
            })

    # -------------------------------
    # WATER QUALITY
    # -------------------------------
    for s in WaterQualityStation.objects.all():
        last = WaterQualityRecord.objects.filter(station=s).order_by('-timestamp').first()

        if last:
            data = {
                "ph": last.ph,
                "nitrates": last.nitrates,
                "conductivity": last.conductivity,
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
                "timestamp": last.timestamp,
            })

    # -------------------------------
    # SOIL QUALITY
    # -------------------------------
    for s in SoilQualityStation.objects.all():
        last = SoilQualityRecord.objects.filter(station=s).order_by('-timestamp').first()

        if last:
            data = {
                "heavy_metals": last.heavy_metals,
                "pesticides": last.pesticides,
                "ph": last.ph,
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
                "timestamp": last.timestamp,
            })

    # -------------------------------
    # RADIATION MONITORING
    # -------------------------------
    for s in RadiationStation.objects.all():
        last = RadiationRecord.objects.filter(station=s).order_by('-timestamp').first()

        if last:
            data = {
                "gamma": last.gamma,
                "beta": last.beta,
                "alpha": last.alpha,
                "ambient_dose_rate": last.ambient_dose_rate
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
                "timestamp": last.timestamp,
            })

    return JsonResponse(result, safe=False)


def api_history(request, category, station_name):
    # Мапа моделей та функцій нечіткої логіки
    model_map = {
        "air": (
            AirQualityStation,
            AirQualityRecord,
            calc_air_risk,
            ["pm25", "pm10", "co", "no2", "o3"]
        ),
        "water": (
            WaterQualityStation,
            WaterQualityRecord,
            calc_water_risk,
            ["ph", "nitrates", "conductivity"]
        ),
        "soil": (
            SoilQualityStation,
            SoilQualityRecord,
            calc_soil_risk,
            ["heavy_metals", "pesticides", "ph"]
        ),
        "radiation": (
            RadiationStation,
            RadiationRecord,
            calc_radiation_risk,
            ["gamma", "beta", "alpha", "ambient_dose_rate"]
        ),
    }

    if category not in model_map:
        return JsonResponse({"error": "Unknown category"}, status=400)

    StationModel, RecordModel, fuzzy_fn, field_list = model_map[category]

    # Знаходимо станцію
    station = get_object_or_404(StationModel, name=station_name)

    # Отримуємо всі записи
    records = RecordModel.objects.filter(station=station).order_by("timestamp")

    history = []

    for r in records:
        # --- Формуємо дані для fuzzy logic ---
        fuzzy_input = {}

        for param in field_list:
            fuzzy_input[param] = getattr(r, param)

        fuzzy = fuzzy_fn(fuzzy_input)

        entry = {
            "timestamp": r.timestamp,
            **{param: getattr(r, param) for param in field_list},
            "risk_score": fuzzy["risk_score"],
            "risk_label": fuzzy["risk_label"]
        }

        history.append(entry)

    return JsonResponse({
        "station": station_name,
        "category": category,
        "history": history
    })
