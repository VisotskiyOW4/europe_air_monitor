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

    # ---------- AIR ----------
    for s in AirQualityStation.objects.all():
        last = AirQualityRecord.objects.filter(station=s).order_by('-timestamp').first()
        if last:
            risk_index, risk_label = calc_air_risk(
                pm25=last.pm25,
                pm10=last.pm10,
                co=last.co,
                no2=last.no2,
                o3=last.o3,
            )

            result["air"].append({
                "name": s.name,
                "lat": s.latitude,
                "lon": s.longitude,
                "pm25": last.pm25,
                "pm10": last.pm10,
                "co": last.co,
                "no2": last.no2,
                "o3": last.o3,
                "timestamp": last.timestamp.strftime("%Y-%m-%d %H:%M"),
                "risk_index": round(risk_index, 3),
                "risk_label": risk_label,
            })

    # ---------- WATER ----------
    for s in WaterQualityStation.objects.all():
        last = WaterQualityRecord.objects.filter(station=s).order_by('-timestamp').first()
        if last:
            risk_index, risk_label = calc_water_risk(
                ph=last.ph,
                nitrates=last.nitrates,
                conductivity=last.conductivity,
            )

            result["water"].append({
                "name": s.name,
                "lat": s.latitude,
                "lon": s.longitude,
                "ph": last.ph,
                "nitrates": last.nitrates,
                "conductivity": last.conductivity,
                "timestamp": last.timestamp.strftime("%Y-%m-%d %H:%M"),
                "risk_index": round(risk_index, 3),
                "risk_label": risk_label,
            })

    # ---------- SOIL ----------
    for s in SoilQualityStation.objects.all():
        last = SoilQualityRecord.objects.filter(station=s).order_by('-timestamp').first()
        if last:
            risk_index, risk_label = calc_soil_risk(
                heavy_metals=last.heavy_metals,
                pesticides=last.pesticides,
                ph=last.ph,
            )

            result["soil"].append({
                "name": s.name,
                "lat": s.latitude,
                "lon": s.longitude,
                "heavy_metals": last.heavy_metals,
                "pesticides": last.pesticides,
                "ph": last.ph,
                "timestamp": last.timestamp.strftime("%Y-%m-%d %H:%M"),
                "risk_index": round(risk_index, 3),
                "risk_label": risk_label,
            })

    # ---------- RADIATION ----------
    for s in RadiationStation.objects.all():
        last = RadiationRecord.objects.filter(station=s).order_by('-timestamp').first()
        if last:
            risk_index, risk_label = calc_radiation_risk(
                gamma=last.gamma,
                beta=last.beta,
                alpha=last.alpha,
                ambient_dose_rate=last.ambient_dose_rate,
            )

            result["radiation"].append({
                "name": s.name,
                "lat": s.latitude,
                "lon": s.longitude,
                "gamma": last.gamma,
                "beta": last.beta,
                "alpha": last.alpha,
                "ambient_dose_rate": last.ambient_dose_rate,
                "timestamp": last.timestamp.strftime("%Y-%m-%d %H:%M"),
                "risk_index": round(risk_index, 3),
                "risk_label": risk_label,
            })

    return JsonResponse(result, safe=False)
