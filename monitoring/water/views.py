from django.shortcuts import render
from django.http import JsonResponse
from .models import WaterQualityStation, WaterQualityRecord

def water_map(request):
    return render(request, "monitoring/water_map.html")  # створимо пізніше

def water_data(request):
    stations = WaterQualityStation.objects.all()
    data = []

    for s in stations:
        last_record = WaterQualityRecord.objects.filter(station=s).order_by('-timestamp').first()

        if last_record:
            data.append({
                "name": s.name,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "ph": last_record.ph,
                "nitrates": last_record.nitrates,
                "conductivity": last_record.conductivity,
                "timestamp": last_record.timestamp.strftime("%Y-%m-%d %H:%M")
            })

    return JsonResponse(data, safe=False)
