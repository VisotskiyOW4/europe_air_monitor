from django.db import models

class AirQualityStation(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.city})"


class AirQualityRecord(models.Model):
    station = models.ForeignKey(AirQualityStation, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    pm25 = models.FloatField()
    pm10 = models.FloatField()
    co = models.FloatField()
    no2 = models.FloatField()
    o3 = models.FloatField()
    aqi_fuzzy = models.FloatField(null=True, blank=True)
    aqi_label = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.station.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
