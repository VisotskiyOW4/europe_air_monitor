import csv
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime

from monitoring.air.models import AirQualityStation, AirQualityRecord
from monitoring.water.models import WaterQualityStation, WaterQualityRecord
from monitoring.soil.models import SoilQualityStation, SoilQualityRecord
from monitoring.radiation.models import RadiationStation, RadiationRecord

# ================================
# 🔹 Функція для безпечного округлення
# ================================
def f(value):
    try:
        return round(float(str(value).strip()), 2)
    except:
        return None


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

        # 🔥 ВАЖЛИВО: цикл має бути тут — всередині POST!
        for row in reader:

            # === Очищення полів ===
            name = (row.get("name") or row.get("station") or "").strip()
            if not name:
                continue

            try:
                lat = f(row.get("latitude"))
                lon = f(row.get("longitude"))
            except:
                continue

            # === Timestamp ===
            ts = str(row.get("timestamp")).strip()

            timestamp = None
            date_formats = [
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d"
            ]

            for fmt in date_formats:
                try:
                    timestamp = datetime.strptime(ts, fmt)
                    break
                except:
                    pass

            if timestamp is None:
                timestamp = timezone.now()


            # ===============================
            # 🌫 AIR
            # ===============================
            if monitoring_type == "air":
                st, created = AirQualityStation.objects.get_or_create(
                    name=name,
                    defaults={"latitude": lat, "longitude": lon}
                )
                if not created:
                    st.latitude, st.longitude = lat, lon
                    st.save()

                AirQualityRecord.objects.create(
                    station=st,
                    pm25=f(row.get("pm25")),
                    pm10=f(row.get("pm10")),
                    co=f(row.get("co")),
                    no2=f(row.get("no2")),
                    o3=f(row.get("o3")),
                    timestamp=timestamp
                )

            # ===============================
            # 💧 WATER
            # ===============================
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
                    ph=f(row.get("ph")),
                    nitrates=f(row.get("nitrates")),
                    conductivity=f(row.get("conductivity")),
                    timestamp=timestamp
                )

            # ===============================
            # 🌱 SOIL
            # ===============================
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
                    heavy_metals=f(row.get("heavy_metals")),
                    pesticides=f(row.get("pesticides")),
                    ph=f(row.get("ph")),
                    timestamp=timestamp
                )

            # ===============================
            # ☢ RADIATION
            # ===============================
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
                    gamma=f(row.get("gamma")),
                    beta=f(row.get("beta")),
                    alpha=f(row.get("alpha")),
                    ambient_dose_rate=f(row.get("ambient_dose_rate")),
                    timestamp=timestamp
                )

            count += 1

        message = f"Файл імпортовано. Додано {count} записів ({monitoring_type}). Модель оновлено."

    return render(request, "monitoring/upload_csv.html", {"message": message})
