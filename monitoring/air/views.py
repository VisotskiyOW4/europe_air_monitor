from django.http import JsonResponse
from .models import AirQualityStation, AirQualityRecord

def air_data(request):
    """Повертає дані про якість повітря у форматі JSON"""
    records = AirQualityRecord.objects.select_related('station').order_by('-timestamp')[:500]
    data = [
        {
            'name': r.station.name,
            'latitude': r.station.latitude,
            'longitude': r.station.longitude,
            'pm25': r.pm25,
            'pm10': r.pm10,
            'co': r.co,
            'no2': r.no2,
            'o3': r.o3,
            'aqi': r.aqi_fuzzy,
            'status': r.aqi_label,
            'timestamp': r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for r in records
    ]
    return JsonResponse(data, safe=False)
