from django.urls import path

from .views.cart import CartDetailView
from .views.cart import CartItemDetailView
from .views.cart import CartItemListCreateView
from .views.cart import CartListView
from .views.categories import CategoryDetailView
from .views.categories import CategoryListView
from .views.products import ProductDetailView
from .views.products import ProductListCreateView
from .views.subcategories import SubCategoryDetailView
from .views.subcategories import SubCategoryListView

urlpatterns = [
    # Cart URLs
    path("cart/", CartListView.as_view(), name="cart"),
    path("cart/<uuid:pk>/", CartDetailView.as_view(), name="cart-detail"),
    path("cart-items/", CartItemListCreateView.as_view(), name="cart-items"),
    path(
        "cart-items/<uuid:pk>/",
        CartItemDetailView.as_view(),
        name="cart-item-detail",
    ),
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
        ProductListCreateView.as_view(),
        name="product-list-create",
    ),
    path(
        "products/<uuid:pk>/",
        ProductDetailView.as_view(),
        name="product-detail",
    ),
]

app_name = "ecommerce"
