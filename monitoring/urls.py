from django.contrib import admin
from django.urls import include, path
from monitoring import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.map_view, name='map_view'),
    path('data/', views.stations_data, name='stations_data'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('city_data/', views.city_data, name='city_data'),
    path('pollutants_average/', views.pollutants_average, name='pollutants_average'),
    path('air/', include('monitoring.air.urls')),
    path('water/', include('monitoring.water.urls')),
    path('soil/', include('monitoring.soil.urls')),
    path('radiation/', include('monitoring.radiation.urls')),
]
