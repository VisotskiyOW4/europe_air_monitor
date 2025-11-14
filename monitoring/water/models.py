from django.db import models


class WaterQualityStation(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class WaterQualityRecord(models.Model):
    station = models.ForeignKey(WaterQualityStation, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()

    ph = models.FloatField()
    nitrates = models.FloatField()
    conductivity = models.FloatField()

    risk_label = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.station.name} – {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
