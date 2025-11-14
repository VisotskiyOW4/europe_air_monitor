from django.urls import path, include

urlpatterns = [
    path('air/', include('monitoring.air.urls')),
    path('water/', include('monitoring.water.urls')),
    path('soil/', include('monitoring.soil.urls')),
    path('radiation/', include('monitoring.radiation.urls')),
]
