from django.shortcuts import render
from django.http import JsonResponse
from .models import SoilQualityStation, SoilQualityRecord

def soil_map(request):
    return render(request, "monitoring/soil_map.html")

def soil_data(request):
    stations = SoilQualityStation.objects.all()
    data = []

    for s in stations:
        last_record = SoilQualityRecord.objects.filter(station=s).order_by('-timestamp').first()

        if last_record:
            data.append({
                "name": s.name,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "heavy_metals": last_record.heavy_metals,
                "pesticides": last_record.pesticides,
                "ph": last_record.ph,
                "timestamp": last_record.timestamp.strftime("%Y-%m-%d %H:%M"),
            })

    return JsonResponse(data, safe=False)
