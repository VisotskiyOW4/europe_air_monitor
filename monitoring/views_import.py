import csv
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime

from monitoring.air.models import AirQualityStation, AirQualityRecord
from monitoring.water.models import WaterQualityStation, WaterQualityRecord
from monitoring.soil.models import SoilQualityStation, SoilQualityRecord
from monitoring.radiation.models import RadiationStation, RadiationRecord


def detect_monitoring_type(headers):
    headers = [h.lower().strip() for h in headers]

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
            return render(request, "monitoring/upload_csv.html",
                          {"message": "Файл не вибрано!"})

        decoded = file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded)

        monitoring_type = detect_monitoring_type(reader.fieldnames)

        if monitoring_type is None:
            return render(request, "monitoring/upload_csv.html",
                          {"message": "Не вдалося визначити тип моніторингу."})

        count = 0

        for row in reader:

            # --- очищення та перевірка загальних полів ---
            name = (row.get("name") or row.get("station") or "").strip()
            if not name:
                continue  # пропускаємо некоректний рядок

            try:
                lat = float(str(row.get("latitude")).strip())
                lon = float(str(row.get("longitude")).strip())
            except:
                continue  # пропуск якщо координати не читаються

            # timestamp
            ts = str(row.get("timestamp")).strip()
            try:
                timestamp = datetime.fromisoformat(ts)
            except:
                timestamp = timezone.now()

            # ============================================
            # AIR
            # ============================================
            if monitoring_type == "air":
                st, created = AirQualityStation.objects.get_or_create(
                    name=name,
                    defaults={"latitude": lat, "longitude": lon}
                )

                # оновлення координат якщо станція існувала
                if not created:
                    st.latitude, st.longitude = lat, lon
                    st.save()

                AirQualityRecord.objects.create(
                    station=st,
                    pm25=float(row.get("pm25")),
                    pm10=float(row.get("pm10")),
                    co=float(row.get("co")),
                    no2=float(row.get("no2")),
                    o3=float(row.get("o3")),
                    timestamp=timestamp
                )

            # ============================================
            # WATER
            # ============================================
            elif monitoring_type == "water":
                st, created = WaterQualityStation.objects.get_or_create(
                    name=name,
                    defaults={"latitude": lat, "longitude": lon}
                )
                if not created:
                    st.latitude, st.longitude = lat, lon
                    st.save()

                WaterQualityRecord.objects.create(
                    station=st,
                    ph=float(row.get("ph")),
                    nitrates=float(row.get("nitrates")),
                    conductivity=float(row.get("conductivity")),
                    timestamp=timestamp
                )

            # ============================================
            # SOIL
            # ============================================
            elif monitoring_type == "soil":
                st, created = SoilQualityStation.objects.get_or_create(
                    name=name,
                    defaults={"latitude": lat, "longitude": lon}
                )
                if not created:
                    st.latitude, st.longitude = lat, lon
                    st.save()

                SoilQualityRecord.objects.create(
                    station=st,
                    heavy_metals=float(row.get("heavy_metals")),
                    pesticides=float(row.get("pesticides")),
                    ph=float(row.get("ph")),
                    timestamp=timestamp
                )

            # ============================================
            # RADIATION
            # ============================================
            elif monitoring_type == "radiation":
                st, created = RadiationStation.objects.get_or_create(
                    name=name,
                    defaults={"latitude": lat, "longitude": lon}
                )
                if not created:
                    st.latitude, st.longitude = lat, lon
                    st.save()

                RadiationRecord.objects.create(
                    station=st,
                    gamma=float(row.get("gamma")),
                    beta=float(row.get("beta")),
                    alpha=float(row.get("alpha")),
                    ambient_dose_rate=float(row.get("ambient_dose_rate")),
                    timestamp=timestamp
                )

            count += 1

        message = f"Файл імпортовано. Додано {count} записів ({monitoring_type})."

    return render(request, "monitoring/upload_csv.html", {"message": message})
