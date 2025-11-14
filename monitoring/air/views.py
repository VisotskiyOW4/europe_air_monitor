from django.shortcuts import render
from django.http import JsonResponse
from .models import AirQualityStation, AirQualityRecord

def map_view(request):
    return render(request, "monitoring/map.html")

def stations_data(request):
    stations = AirQualityStation.objects.all()
    data = []

    for s in stations:
        last_record = AirQualityRecord.objects.filter(station=s).order_by('-timestamp').first()

        if last_record:
            data.append({
                'name': s.name,
                'latitude': s.latitude,
                'longitude': s.longitude,
                'pm25': last_record.pm25,
                'pm10': last_record.pm10,
                'co': last_record.co,
                'no2': last_record.no2,
                'o3': last_record.o3,
                'timestamp': last_record.timestamp.strftime("%Y-%m-%d %H:%M"),
                'aqi': last_record.calculate_aqi() if hasattr(last_record, "calculate_aqi") else None
            })

    return JsonResponse(data, safe=False)
