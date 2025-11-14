from django.urls import path
from .views import soil_map, soil_data

urlpatterns = [
    path('', soil_map, name='soil_map'),
    path('data/', soil_data, name='soil_data'),
]
