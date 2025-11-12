from django.contrib import admin
from .models import AirQualityStation, AirQualityRecord

@admin.register(AirQualityStation)
class AirQualityStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'latitude', 'longitude')
    search_fields = ('name', 'city', 'country')
    list_filter = ('country',)

@admin.register(AirQualityRecord)
class AirQualityRecordAdmin(admin.ModelAdmin):
    list_display = ('station', 'timestamp', 'pm25', 'pm10', 'co', 'no2', 'o3', 'aqi_fuzzy', 'aqi_label')
    search_fields = ('station__name',)
    list_filter = ('station__country', 'aqi_label')
    date_hierarchy = 'timestamp'
