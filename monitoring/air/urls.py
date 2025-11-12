from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.air_data, name='air_data'),
]
