from django.db import models

class SoilQualityStation(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    country = models.CharField(max_length=100, null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.area})"


class SoilQualityRecord(models.Model):
    station = models.ForeignKey(SoilQualityStation, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    heavy_metals = models.FloatField()
    pesticides = models.FloatField()
    moisture = models.FloatField()
    fertility_index = models.FloatField(null=True, blank=True)
    risk_label = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.station.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
