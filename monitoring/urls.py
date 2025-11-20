# monitoring/urls.py
from django.urls import path, include
from django.views.generic import TemplateView

from monitoring.views_api import api_global
from monitoring.views_history import api_history, api_forecast
from .views_import import upload_csv

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="monitoring/global_map.html"),
        name="global_map",
    ),

    path("api/global/", api_global, name="api_global"),

    # історія параметра
    path("api/history/<str:type>/<int:station_id>/", api_history, name="api_history"),
    # прогноз параметра
    path("api/forecast/<str:type>/<int:station_id>/", api_forecast, name="api_forecast"),

    path("upload/", upload_csv, name="upload_csv"),

    path("air/", include("monitoring.air.urls")),
    path("water/", include("monitoring.water.urls")),
    path("soil/", include("monitoring.soil.urls")),
    path("radiation/", include("monitoring.radiation.urls")),
]
