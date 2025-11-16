from django.contrib import admin
from .models import AirQualityStation, AirQualityRecord


@admin.register(AirQualityStation)
class AirQualityStationAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude")
    search_fields = ("name",)


@admin.register(AirQualityRecord)
class AirQualityRecordAdmin(admin.ModelAdmin):
    list_display = (
        "station",
        "timestamp",
        "pm25",
        "pm10",
        "co",
        "no2",
        "o3",
    )
    list_filter = ("station", "timestamp")
    search_fields = ("station__name",)
