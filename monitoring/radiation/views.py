from django.shortcuts import render
from django.http import JsonResponse
from .models import RadiationStation, RadiationRecord

def radiation_map(request):
    return render(request, "monitoring/radiation_map.html")

def radiation_data(request):
    stations = RadiationStation.objects.all()
    data = []

    for s in stations:
        last_record = RadiationRecord.objects.filter(station=s).order_by('-timestamp').first()

        if last_record:
            data.append({
                "name": s.name,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "gamma": last_record.gamma,
                "beta": last_record.beta,
                "alpha": last_record.alpha,
                "ambient_dose_rate": last_record.ambient_dose_rate,
                "timestamp": last_record.timestamp.strftime("%Y-%m-%d %H:%M")
            })

    return JsonResponse(data, safe=False)
