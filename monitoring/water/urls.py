from django.urls import path
from .views import water_map, water_data

urlpatterns = [
    path("", water_map),
    path("data/", water_data),
]
