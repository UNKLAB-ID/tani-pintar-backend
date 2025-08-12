from django.urls import path

from .views.categories import CategoryDetailView
from .views.categories import CategoryListView
from .views.products import ProductViewSet
from .views.subcategories import SubCategoryDetailView
from .views.subcategories import SubCategoryListView

urlpatterns = [
    # Category URLs
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path(
        "categories/<slug:slug>/",
        CategoryDetailView.as_view(),
        name="category-detail",
    ),
    # SubCategory URLs
    path("subcategories/", SubCategoryListView.as_view(), name="subcategory-list"),
    path(
        "subcategories/<slug:slug>/",
        SubCategoryDetailView.as_view(),
        name="subcategory-detail",
    ),
    # Product URLs
    path(
        "products/",
        ProductViewSet.as_view({"get": "list", "post": "create"}),
        name="product-list",
    ),
    path(
        "products/<uuid:pk>/",
        ProductViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            },
        ),
        name="product-detail",
    ),
]

app_name = "ecommerce"
