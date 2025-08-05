from django.urls import path

from .views import CategoryDetailView
from .views import CategoryListView

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path(
        "categories/<slug:slug>/",
        CategoryDetailView.as_view(),
        name="category-detail",
    ),
]

app_name = "ecommerce"
