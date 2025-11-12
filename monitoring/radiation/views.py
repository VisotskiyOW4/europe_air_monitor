from django.http import JsonResponse
from .models import RadiationStation, RadiationRecord

def radiation_data(request):
    records = RadiationRecord.objects.select_related('station').order_by('-timestamp')[:500]
    data = [
        {
            'name': r.station.name,
            'latitude': r.station.latitude,
            'longitude': r.station.longitude,
            'gamma': r.gamma,
            'beta': r.beta,
            'alpha': r.alpha,
            'dose_rate': r.dose_rate,
            'risk': r.risk_label,
            'timestamp': r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for r in records
    ]
    return JsonResponse(data, safe=False)
