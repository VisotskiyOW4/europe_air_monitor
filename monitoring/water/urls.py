from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.water_data, name='water_data'),
]
