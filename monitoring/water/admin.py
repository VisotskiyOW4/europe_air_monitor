from django.contrib import admin
from .models import WaterQualityStation, WaterQualityRecord


@admin.register(WaterQualityStation)
class WaterQualityStationAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude")
    search_fields = ("name",)


@admin.register(WaterQualityRecord)
class WaterQualityRecordAdmin(admin.ModelAdmin):
    list_display = (
        "station",
        "timestamp",
        "ph",
        "nitrates",
        "conductivity",
    )
    list_filter = ("station", "timestamp")
    search_fields = ("station__name",)
