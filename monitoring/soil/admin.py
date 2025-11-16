from django.contrib import admin
from .models import SoilQualityStation, SoilQualityRecord


@admin.register(SoilQualityStation)
class SoilQualityStationAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude")
    search_fields = ("name",)


@admin.register(SoilQualityRecord)
class SoilQualityRecordAdmin(admin.ModelAdmin):
    list_display = (
        "station",
        "timestamp",
        "heavy_metals",
        "pesticides",
        "ph",
    )
    list_filter = ("station", "timestamp")
    search_fields = ("station__name",)
