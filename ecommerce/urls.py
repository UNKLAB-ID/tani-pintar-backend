from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.categories import CategoryDetailView
from .views.categories import CategoryListView
from .views.products import ProductViewSet
from .views.subcategories import SubCategoryDetailView
from .views.subcategories import SubCategoryListView

# Create router for ViewSets
router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")

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
    # Product URLs (include router URLs)
    path("", include(router.urls)),
    # Additional custom product endpoints
    path(
        "products/public-list/",
        ProductViewSet.as_view({"get": "public_list"}),
        name="product-public-list",
    ),
    path(
        "products/my-products/",
        ProductViewSet.as_view({"get": "my_products"}),
        name="product-my-products",
    ),
    path(
        "products/<uuid:pk>/add-images/",
        ProductViewSet.as_view({"post": "add_images"}),
        name="product-add-images",
    ),
    path(
        "products/<uuid:pk>/remove-image/",
        ProductViewSet.as_view({"delete": "remove_image"}),
        name="product-remove-image",
    ),
]

app_name = "ecommerce"
