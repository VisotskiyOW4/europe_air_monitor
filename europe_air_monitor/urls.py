from django.contrib import admin
from django.urls import path, include
from monitoring.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),

    # Головна сторінка
    path('', dashboard, name='dashboard'),

    # Підсистеми
    path('air/', include('monitoring.air.urls')),
    path('water/', include('monitoring.water.urls')),
    path('soil/', include('monitoring.soil.urls')),
    path('radiation/', include('monitoring.radiation.urls')),
]
