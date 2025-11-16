from django.contrib import admin
from django.urls import path, include
from monitoring.views import global_map

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', global_map, name='global_map'),
    path('', include('monitoring.urls')),

    path('air/', include('monitoring.air.urls')),
    path('water/', include('monitoring.water.urls')),
    path('soil/', include('monitoring.soil.urls')),
    path('radiation/', include('monitoring.radiation.urls')),
]