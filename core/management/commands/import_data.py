from django.core.management.base import BaseCommand
from monitoring.air.models import AirQualityStation, AirQualityRecord
from monitoring.water.models import WaterQualityStation, WaterQualityRecord
from monitoring.soil.models import SoilQualityStation, SoilQualityRecord
from monitoring.radiation.models import RadiationStation, RadiationRecord

import csv
import os
from datetime import datetime


class Command(BaseCommand):
    help = "Import data from CSV files into all monitoring subsystems"

    def handle(self, *args, **kwargs):
        base_dir = "monitoring/data"

        for file_name in os.listdir(base_dir):
            file_path = os.path.join(base_dir, file_name)

            if not file_name.endswith(".csv"):
                continue

            self.stdout.write(self.style.WARNING(f"Importing {file_name}..."))

            with open(file_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)

                # ---------------- AIR DATA ----------------
                if file_name == "air.csv":
                    for row in reader:
                        station, created = AirQualityStation.objects.get_or_create(
                            name=row["name"],
                            defaults={
                                "latitude": float(row["latitude"]),
                                "longitude": float(row["longitude"]),
                            },
                        )

                        AirQualityRecord.objects.create(
                            station=station,
                            timestamp=datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M"),
                            pm25=float(row["pm25"]),
                            pm10=float(row["pm10"]),
                            co=float(row["co"]),
                            no2=float(row["no2"]),
                            o3=float(row["o3"]),
                        )

                # ---------------- RADIATION DATA ----------------
                elif file_name == "radiation.csv":
                    for row in reader:
                        station, created = RadiationStation.objects.get_or_create(
                            name=row["name"],
                            defaults={
                                "latitude": float(row["latitude"]),
                                "longitude": float(row["longitude"]),
                            },
                        )

                        RadiationRecord.objects.create(
                            station=station,
                            timestamp=datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M"),
                            gamma=float(row["gamma"]),
                            beta=float(row["beta"]),
                            alpha=float(row["alpha"]),
                            ambient_dose_rate=float(row["ambient_dose_rate"]),
                        )

                # ---------------- SOIL DATA ----------------
                elif file_name == "soil.csv":
                    for row in reader:
                        station, created = SoilQualityStation.objects.get_or_create(
                            name=row["name"],
                            defaults={
                                "latitude": float(row["latitude"]),
                                "longitude": float(row["longitude"]),
                            },
                        )

                        SoilQualityRecord.objects.create(
                            station=station,
                            timestamp=datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M"),
                            heavy_metals=float(row["heavy_metals"]),
                            pesticides=float(row["pesticides"]),
                            ph=float(row["ph"]),
                        )

                # ---------------- WATER DATA ----------------
                elif file_name == "water.csv":
                    for row in reader:
                        station, created = WaterQualityStation.objects.get_or_create(
                            name=row["name"],
                            defaults={
                                "latitude": float(row["latitude"]),
                                "longitude": float(row["longitude"]),
                            },
                        )

                        WaterQualityRecord.objects.create(
                            station=station,
                            timestamp=datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M"),
                            ph=float(row["ph"]),
                            nitrates=float(row["nitrates"]),
                            conductivity=float(row["conductivity"]),
                        )

            self.stdout.write(self.style.SUCCESS(f"✓ Imported {file_name}"))

        self.stdout.write(self.style.SUCCESS("All data imported successfully."))
