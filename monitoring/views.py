from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils.dateparse import parse_date
from .models import AirQualityStation, AirQualityRecord
from .forms import CSVUploadForm
import csv
from io import TextIOWrapper
from datetime import datetime

def map_view(request):
    return render(request, 'monitoring/map.html', {})

def stations_data(request):
    day_str = request.GET.get('day')
    # За замовчуванням пустий запит
    records = AirQualityRecord.objects.none()

    if day_str:
        day = parse_date(day_str)
        if day:
            # Фільтруємо по конкретній даті
            records = AirQualityRecord.objects.filter(timestamp__date=day)

    data = []
    for r in records:
        aqi = calculate_aqi(r.pm25, r.pm10, r.co, r.no2, r.o3)
        data.append({
            'station': r.station.name,
            'timestamp': r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'pm25': r.pm25,
            'pm10': r.pm10,
            'co': r.co,
            'no2': r.no2,
            'o3': r.o3,
            'latitude': r.station.latitude,
            'longitude': r.station.longitude,
            'aqi': aqi
        })

    return JsonResponse(data, safe=False)

def calculate_aqi(pm25, pm10, co, no2, o3):
    values = [v for v in [pm25, pm10, co, no2, o3] if v is not None]
    if not values:
        return 100
    base = 100
    avg = sum(values) / len(values)
    aqi = base - int(avg * 2)
    if aqi < 1:
        aqi = 1
    elif aqi > 100:
        aqi = 100
    return aqi

def city_data(request):
    city_name = request.GET.get('city')
    data = []
    if city_name:
        station = AirQualityStation.objects.filter(name=city_name).first()
        if station:
            records = station.records.all().order_by('timestamp')
            for r in records:
                aqi = calculate_aqi(r.pm25, r.pm10, r.co, r.no2, r.o3)
                data.append({
                    'timestamp': r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    'aqi': aqi
                })
    return JsonResponse(data, safe=False)

def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            file_data = TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.DictReader(file_data)

            for row in reader:
                station_name = row['station']
                latitude_str = row.get('latitude', '')
                longitude_str = row.get('longitude', '')
                timestamp_str = row['timestamp']
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

                latitude = float(latitude_str) if latitude_str else None
                longitude = float(longitude_str) if longitude_str else None

                station, created = AirQualityStation.objects.get_or_create(
                    name=station_name,
                    defaults={'latitude': latitude, 'longitude': longitude}
                )
                if not created:
                    if latitude is not None:
                        station.latitude = latitude
                    if longitude is not None:
                        station.longitude = longitude
                    station.save()

                pm25 = float(row['pm25']) if row['pm25'] else None
                pm10 = float(row['pm10']) if row['pm10'] else None
                co = float(row['co']) if row['co'] else None
                no2 = float(row['no2']) if row['no2'] else None
                o3 = float(row['o3']) if row['o3'] else None

                AirQualityRecord.objects.create(
                    station=station,
                    timestamp=timestamp,
                    pm25=pm25,
                    pm10=pm10,
                    co=co,
                    no2=no2,
                    o3=o3
                )

            messages.success(request, "CSV data imported successfully!")
            return redirect('map_view')
    else:
        form = CSVUploadForm()

    return render(request, 'monitoring/upload_csv.html', {'form': form})
