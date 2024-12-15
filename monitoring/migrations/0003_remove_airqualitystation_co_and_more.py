# Generated by Django 5.0.6 on 2024-12-15 20:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0002_alter_airqualitystation_latitude_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='airqualitystation',
            name='co',
        ),
        migrations.RemoveField(
            model_name='airqualitystation',
            name='no2',
        ),
        migrations.RemoveField(
            model_name='airqualitystation',
            name='o3',
        ),
        migrations.RemoveField(
            model_name='airqualitystation',
            name='pm10',
        ),
        migrations.RemoveField(
            model_name='airqualitystation',
            name='pm25',
        ),
        migrations.CreateModel(
            name='AirQualityRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('pm25', models.FloatField(blank=True, null=True)),
                ('pm10', models.FloatField(blank=True, null=True)),
                ('co', models.FloatField(blank=True, null=True)),
                ('no2', models.FloatField(blank=True, null=True)),
                ('o3', models.FloatField(blank=True, null=True)),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='records', to='monitoring.airqualitystation')),
            ],
        ),
    ]