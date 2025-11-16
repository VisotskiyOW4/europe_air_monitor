from django.urls import path
from .views import radiation_map, radiation_data

urlpatterns = [
    path("", radiation_map),
    path("data/", radiation_data),
]
