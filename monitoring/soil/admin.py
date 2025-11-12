from django.contrib import admin
from .models import SoilQualityStation, SoilQualityRecord

@admin.register(SoilQualityStation)
class SoilQualityStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'country', 'latitude', 'longitude')
    search_fields = ('name', 'area', 'country')
    list_filter = ('country',)

@admin.register(SoilQualityRecord)
class SoilQualityRecordAdmin(admin.ModelAdmin):
    list_display = ('station', 'timestamp', 'heavy_metals', 'pesticides', 'moisture', 'fertility_index', 'risk_label')
    search_fields = ('station__name',)
    list_filter = ('risk_label', 'station__country')
    date_hierarchy = 'timestamp'
