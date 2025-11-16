from django.contrib import admin
from .models import RadiationStation, RadiationRecord


@admin.register(RadiationStation)
class RadiationStationAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude")
    search_fields = ("name",)


@admin.register(RadiationRecord)
class RadiationRecordAdmin(admin.ModelAdmin):
    list_display = (
        "station",
        "timestamp",
        "gamma",
        "beta",
        "alpha",
        "ambient_dose_rate",
    )
    list_filter = ("station", "timestamp")
    search_fields = ("station__name",)
