from django.db import models


class RadiationStation(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class RadiationRecord(models.Model):
    station = models.ForeignKey(RadiationStation, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()

    gamma = models.FloatField()
    beta = models.FloatField()
    alpha = models.FloatField()
    ambient_dose_rate = models.FloatField()


    def __str__(self):
        return f"{self.station.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
