from django.http import JsonResponse
from monitoring.air.models import AirQualityRecord, AirQualityStation
from monitoring.water.models import WaterQualityRecord, WaterQualityStation
from monitoring.soil.models import SoilQualityRecord, SoilQualityStation
from monitoring.radiation.models import RadiationRecord, RadiationStation

MODEL_MAP = {
    "air": (AirQualityStation, AirQualityRecord),
    "water": (WaterQualityStation, WaterQualityRecord),
    "soil": (SoilQualityStation, SoilQualityRecord),
    "radiation": (RadiationStation, RadiationRecord),
}

def api_history(request, type, station_id):
    if type not in MODEL_MAP:
        return JsonResponse({"error": "invalid type"}, status=400)

    Station, Record = MODEL_MAP[type]

    records = Record.objects.filter(station_id=station_id).order_by("timestamp")

    if not records.exists():
        return JsonResponse({"timestamps": [], "values": []})

    # вибираємо перший параметр (ok)
    sample_record = records.first()
    keys = [f.name for f in sample_record._meta.fields if f.name not in ("id", "timestamp", "station")]

    param = keys[0]

    timestamps = [r.timestamp.strftime("%Y-%m-%d %H:%M") for r in records]
    values = [getattr(r, param) for r in records]

    return JsonResponse({
        "param": param,
        "timestamps": timestamps,
        "values": values
    })
