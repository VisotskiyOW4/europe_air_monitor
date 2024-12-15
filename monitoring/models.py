from django.db import models

class AirQualityStation(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class AirQualityRecord(models.Model):
    station = models.ForeignKey(AirQualityStation, on_delete=models.CASCADE, related_name='records')
    timestamp = models.DateTimeField()
    pm25 = models.FloatField(null=True, blank=True)
    pm10 = models.FloatField(null=True, blank=True)
    co = models.FloatField(null=True, blank=True)
    no2 = models.FloatField(null=True, blank=True)
    o3 = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.station.name} - {self.timestamp}"
