from django.http import JsonResponse

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
                "name": s.name,
                "lat": s.latitude,
                "lon": s.longitude,
                **data,
                "risk_score": fuzzy["risk_score"],
                "risk_label": fuzzy["risk_label"],
                "timestamp": last.timestamp,
            })

    return JsonResponse(result, safe=False)
