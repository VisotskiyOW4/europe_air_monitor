from django.shortcuts import render
from django.http import JsonResponse
from .models import SoilQualityStation, SoilQualityRecord

def soil_map(request):
    return render(request, "monitoring/soil.html")

def soil_data(request):
    stations = SoilQualityStation.objects.all()
    data = []

    for s in stations:
        rec = SoilQualityRecord.objects.filter(station=s).order_by("-timestamp").first()
        if rec:
            data.append({
                "name": s.name,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "heavy_metals": rec.heavy_metals,
                "pesticides": rec.pesticides,
                "ph": rec.ph,
                "timestamp": rec.timestamp.strftime("%Y-%m-%d %H:%M")
            })

    return JsonResponse(data, safe=False)
