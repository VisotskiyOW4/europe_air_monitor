import csv
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime

from monitoring.air.models import AirQualityStation, AirQualityRecord
from monitoring.water.models import WaterQualityStation, WaterQualityRecord
from monitoring.soil.models import SoilQualityStation, SoilQualityRecord
from monitoring.radiation.models import RadiationStation, RadiationRecord

from monitoring.utils.fuzzy_logic import (
    calc_air_risk, calc_water_risk, calc_soil_risk, calc_radiation_risk
)


def detect_monitoring_type(headers):
    headers = [h.lower() for h in headers]

    if "pm25" in headers or "pm10" in headers:
        return "air"
    if "ph" in headers and "nitrates" in headers:
        return "water"
    if "heavy_metals" in headers or "pesticides" in headers:
        return "soil"
    if "gamma" in headers or "beta" in headers:
        return "radiation"
    return None


def upload_csv(request):
    message = ""

    if request.method == "POST":
        file = request.FILES.get("csv_file")

        if not file:
            message = "Файл не вибрано!"
            return render(request, "upload_csv.html", {"message": message})

        decoded = file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded)

        monitoring_type = detect_monitoring_type(reader.fieldnames)

        if monitoring_type is None:
            return render(request, "upload_csv.html", {"message": "Не вдалося визначити тип моніторингу."})

        count = 0

        for row in reader:
            name = row.get("station") or row.get("name")
            lat = row.get("latitude")
            lon = row.get("longitude")
            timestamp = row.get("timestamp")

            # Перетворення часу
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except:
                timestamp = timezone.now()

            if monitoring_type == "air":
                st, _ = AirQualityStation.objects.get_or_create(
                    name=name, latitude=lat, longitude=lon
                )
                rec = AirQualityRecord.objects.create(
                    station=st,
                    pm25=row.get("pm25"),
                    pm10=row.get("pm10"),
                    co=row.get("co"),
                    no2=row.get("no2"),
                    o3=row.get("o3"),
                    timestamp=timestamp
                )
                rec.risk_label = calc_air_risk(rec)
                rec.save()

            elif monitoring_type == "water":
                st, _ = WaterQualityStation.objects.get_or_create(
                    name=name, latitude=lat, longitude=lon
                )
                rec = WaterQualityRecord.objects.create(
                    station=st,
                    ph=row.get("ph"),
                    nitrates=row.get("nitrates"),
                    conductivity=row.get("conductivity"),
                    timestamp=timestamp
                )
                rec.risk_label = calc_water_risk(rec)
                rec.save()

            elif monitoring_type == "soil":
                st, _ = SoilQualityStation.objects.get_or_create(
                    name=name, latitude=lat, longitude=lon
                )
                rec = SoilQualityRecord.objects.create(
                    station=st,
                    heavy_metals=row.get("heavy_metals"),
                    pesticides=row.get("pesticides"),
                    ph=row.get("ph"),
                    timestamp=timestamp
                )
                rec.risk_label = calc_soil_risk(rec)
                rec.save()

            elif monitoring_type == "radiation":
                st, _ = RadiationStation.objects.get_or_create(
                    name=name, latitude=lat, longitude=lon
                )
                rec = RadiationRecord.objects.create(
                    station=st,
                    gamma=row.get("gamma"),
                    beta=row.get("beta"),
                    alpha=row.get("alpha"),
                    ambient_dose_rate=row.get("ambient_dose_rate"),
                    timestamp=timestamp
                )
                rec.risk_label = calc_radiation_risk(rec)
                rec.save()

            count += 1

        message = f"Файл успішно імпортовано. Додано {count} записів ({monitoring_type})."

    return render(request, "monitoring/upload_csv.html", {"message": message})

