from django.shortcuts import render
from django.http import JsonResponse
from .models import RadiationStation, RadiationRecord

def radiation_map(request):
    return render(request, "monitoring/radiation.html")

def radiation_data(request):
    stations = RadiationStation.objects.all()
    data = []

    for s in stations:
        rec = RadiationRecord.objects.filter(station=s).order_by("-timestamp").first()
        if rec:
            data.append({
                "name": s.name,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "gamma": rec.gamma,
                "beta": rec.beta,
                "alpha": rec.alpha,
                "ambient_dose_rate": rec.ambient_dose_rate,
                "timestamp": rec.timestamp.strftime("%Y-%m-%d %H:%M")
            })

    return JsonResponse(data, safe=False)
