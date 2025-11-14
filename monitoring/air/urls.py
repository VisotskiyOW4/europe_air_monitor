from django.urls import path
from .views import map_view, stations_data

urlpatterns = [
    path('', map_view, name='air_map'),
    path('data/', stations_data, name='air_data'),
]
