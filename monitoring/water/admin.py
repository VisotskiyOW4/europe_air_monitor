from django.contrib import admin
from .models import WaterQualityStation, WaterQualityRecord

@admin.register(WaterQualityStation)
class WaterQualityStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'river', 'country', 'latitude', 'longitude')
    search_fields = ('name', 'river', 'country')
    list_filter = ('country',)

@admin.register(WaterQualityRecord)
class WaterQualityRecordAdmin(admin.ModelAdmin):
    list_display = ('station', 'timestamp', 'ph', 'nitrates', 'turbidity', 'temperature', 'pollution_index', 'status_label')
    search_fields = ('station__name',)
    list_filter = ('status_label', 'station__country')
    date_hierarchy = 'timestamp'
