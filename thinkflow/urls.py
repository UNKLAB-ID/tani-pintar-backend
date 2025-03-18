from django.urls import path

from .views import PlantDiseaseAnalyzerView
from .views import index

urlpatterns = [
    path(
        "plant-disease/analyzer/",
        PlantDiseaseAnalyzerView.as_view(),
        name="plant-disease-analyzer",
    ),
    path("", index, name="index"),
]

app_name = "thinkflow"
