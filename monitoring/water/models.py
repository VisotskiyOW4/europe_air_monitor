from django.db import models

class WaterQualityStation(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    country = models.CharField(max_length=100, null=True, blank=True)
    river = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.river})"


class WaterQualityRecord(models.Model):
    station = models.ForeignKey(WaterQualityStation, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    ph = models.FloatField()
    nitrates = models.FloatField()
    turbidity = models.FloatField()
    temperature = models.FloatField()
    pollution_index = models.FloatField(null=True, blank=True)
    status_label = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.station.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
