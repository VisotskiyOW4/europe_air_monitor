from django.contrib import admin
from .models import RadiationStation, RadiationRecord

@admin.register(RadiationStation)
class RadiationStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone', 'country', 'latitude', 'longitude')
    search_fields = ('name', 'zone', 'country')
    list_filter = ('country',)

@admin.register(RadiationRecord)
class RadiationRecordAdmin(admin.ModelAdmin):
    list_display = ('station', 'timestamp', 'gamma', 'beta', 'alpha', 'dose_rate', 'risk_fuzzy', 'risk_label')
    search_fields = ('station__name',)
    list_filter = ('risk_label', 'station__country')
    date_hierarchy = 'timestamp'
