from django.http import JsonResponse
from .models import WaterQualityStation, WaterQualityRecord

def water_data(request):
    records = WaterQualityRecord.objects.select_related('station').order_by('-timestamp')[:500]
    data = [
        {
            'name': r.station.name,
            'latitude': r.station.latitude,
            'longitude': r.station.longitude,
            'ph': r.ph,
            'nitrates': r.nitrates,
            'turbidity': r.turbidity,
            'temperature': r.temperature,
            'index': r.pollution_index,
            'status': r.status_label,
            'timestamp': r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for r in records
    ]
    return JsonResponse(data, safe=False)
