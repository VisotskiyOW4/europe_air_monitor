from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.radiation_data, name='radiation_data'),
]
