from django.urls import path

from .views.categories import CategoryDetailView
from .views.categories import CategoryListView
from .views.subcategories import SubCategoryDetailView
from .views.subcategories import SubCategoryListView

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path(
        "categories/<slug:slug>/",
        CategoryDetailView.as_view(),
        name="category-detail",
    ),
    path("subcategories/", SubCategoryListView.as_view(), name="subcategory-list"),
    path(
        "subcategories/<slug:slug>/",
        SubCategoryDetailView.as_view(),
        name="subcategory-detail",
    ),
]

app_name = "ecommerce"
