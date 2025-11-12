from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.soil_data, name='soil_data'),
]
