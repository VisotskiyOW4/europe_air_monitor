from django.urls import path, include
from django.views.generic import TemplateView
from monitoring.views_api import api_global

urlpatterns = [
    path("", TemplateView.as_view(template_name="monitoring/global_map.html"), name="global_map"),
    path("api/global/", api_global, name="api_global"),
    
    path("air/", include("monitoring.air.urls")),
    path("water/", include("monitoring.water.urls")),
    path("soil/", include("monitoring.soil.urls")),
    path("radiation/", include("monitoring.radiation.urls")),
]
