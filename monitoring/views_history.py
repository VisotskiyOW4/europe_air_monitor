# monitoring/views_history.py
from datetime import timedelta

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from sklearn.ensemble import RandomForestRegressor

from monitoring.air.models import AirQualityStation, AirQualityRecord
from monitoring.water.models import WaterQualityStation, WaterQualityRecord
from monitoring.soil.models import SoilQualityStation, SoilQualityRecord
from monitoring.radiation.models import RadiationStation, RadiationRecord


# type -> (StationModel, RecordModel, target_field)
MODEL_MAP = {
    "air": (AirQualityStation, AirQualityRecord, "pm25"),
    "water": (WaterQualityStation, WaterQualityRecord, "nitrates"),
    "soil": (SoilQualityStation, SoilQualityRecord, "pesticides"),
    "radiation": (RadiationStation, RadiationRecord, "ambient_dose_rate"),
}


def api_history(request, type, station_id):
    """
    Повертає історію цільового параметра:
    {
        "param": "pm25",
        "timestamps": [...],
        "values": [...]
    }
    """
    if type not in MODEL_MAP:
        return JsonResponse({"error": "Unknown type"}, status=400)

    StationModel, RecordModel, field_name = MODEL_MAP[type]

    station = get_object_or_404(StationModel, pk=station_id)
    records = RecordModel.objects.filter(station=station).order_by("timestamp")

    timestamps = []
    values = []

    for r in records:
        v = getattr(r, field_name, None)
        if v is None:
            continue
        timestamps.append(r.timestamp.isoformat())
        values.append(float(v))

    return JsonResponse({
        "param": field_name,
        "timestamps": timestamps,
        "values": values,
    })


def api_forecast(request, type, station_id):
    """
    Прогноз того ж параметра на 24 години вперед RandomForestRegressor.
    Формат відповіді такий самий:
    {
        "param": "pm25",
        "timestamps": [...future...],
        "values": [...]
    }
    """
    if type not in MODEL_MAP:
        return JsonResponse({"error": "Unknown type"}, status=400)

    StationModel, RecordModel, field_name = MODEL_MAP[type]

    station = get_object_or_404(StationModel, pk=station_id)
    records = list(
        RecordModel.objects.filter(station=station).order_by("timestamp")
    )

    y = []
    for r in records:
        v = getattr(r, field_name, None)
        if v is None:
            continue
        y.append(float(v))

    # замало даних – повертаємо пустий прогноз
    if len(y) < 5:
        return JsonResponse({
            "param": field_name,
            "timestamps": [],
            "values": [],
        })

    X = [[i] for i in range(len(y))]

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
    )
    model.fit(X, y)

    horizon = 24  # 24 години вперед

    last_index = len(y) - 1
    future_indices = [[last_index + i] for i in range(1, horizon + 1)]
    y_pred = model.predict(future_indices)

    last_ts = records[-1].timestamp
    future_timestamps = [
        (last_ts + timedelta(hours=i)).isoformat()
        for i in range(1, horizon + 1)
    ]

    return JsonResponse({
        "param": field_name,
        "timestamps": future_timestamps,
        "values": [round(float(v), 3) for v in y_pred],
    })
