from django.urls import path
from .views import radiation_map, radiation_data

urlpatterns = [
    path('', radiation_map, name='radiation_map'),
    path('data/', radiation_data, name='radiation_data'),
]
