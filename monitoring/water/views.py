from django.shortcuts import render
from django.http import JsonResponse
from .models import WaterQualityStation, WaterQualityRecord

def water_map(request):
    return render(request, "monitoring/water.html")

def water_data(request):
    stations = WaterQualityStation.objects.all()
    data = []

    for s in stations:
        rec = WaterQualityRecord.objects.filter(station=s).order_by("-timestamp").first()
        if rec:
            data.append({
                "name": s.name,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "ph": rec.ph,
                "nitrates": rec.nitrates,
                "conductivity": rec.conductivity,
                "timestamp": rec.timestamp.strftime("%Y-%m-%d %H:%M")
            })

    return JsonResponse(data, safe=False)
