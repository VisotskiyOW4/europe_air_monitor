from django.http import JsonResponse
from .models import SoilQualityStation, SoilQualityRecord

def soil_data(request):
    records = SoilQualityRecord.objects.select_related('station').order_by('-timestamp')[:500]
    data = [
        {
            'name': r.station.name,
            'latitude': r.station.latitude,
            'longitude': r.station.longitude,
            'heavy_metals': r.heavy_metals,
            'pesticides': r.pesticides,
            'moisture': r.moisture,
            'fertility_index': r.fertility_index,
            'risk': r.risk_label,
            'timestamp': r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for r in records
    ]
    return JsonResponse(data, safe=False)
