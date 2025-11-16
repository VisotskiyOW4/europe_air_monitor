from django.shortcuts import render
from django.http import JsonResponse
from .models import AirQualityStation, AirQualityRecord

def air_map(request):
    return render(request, "monitoring/air.html")

def air_data(request):
    stations = AirQualityStation.objects.all()
    data = []

    for s in stations:
        rec = AirQualityRecord.objects.filter(station=s).order_by("-timestamp").first()
        if rec:
            data.append({
                "name": s.name,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "pm25": rec.pm25,
                "pm10": rec.pm10,
                "co": rec.co,
                "no2": rec.no2,
                "o3": rec.o3,
                "timestamp": rec.timestamp.strftime("%Y-%m-%d %H:%M")
            })

    return JsonResponse(data, safe=False)
