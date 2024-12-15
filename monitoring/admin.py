from django.contrib import admin
from .models import AirQualityStation, AirQualityRecord

# Відображаємо AirQualityRecord у вигляді вкладених записів для кожної станції
class AirQualityRecordInline(admin.TabularInline):
    model = AirQualityRecord
    extra = 0
    # Можна вказати поля лише для читання, якщо потрібно:
    readonly_fields = ('timestamp', 'pm25', 'pm10', 'co', 'no2', 'o3')

@admin.register(AirQualityStation)
class AirQualityStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'last_update')
    search_fields = ('name',)
    ordering = ('name',)
    inlines = [AirQualityRecordInline]

# За бажанням можна зареєструвати AirQualityRecord окремо
@admin.register(AirQualityRecord)
class AirQualityRecordAdmin(admin.ModelAdmin):
    list_display = ('station', 'timestamp', 'pm25', 'pm10', 'co', 'no2', 'o3')
    search_fields = ('station__name',)
    ordering = ('station', 'timestamp')
