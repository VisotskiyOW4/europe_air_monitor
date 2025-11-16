from django.urls import path
from .views import air_map, air_data

urlpatterns = [
    path("", air_map),
    path("data/", air_data),
]
