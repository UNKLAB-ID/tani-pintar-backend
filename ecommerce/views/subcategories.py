from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import generics
from rest_framework.permissions import AllowAny

from ecommerce.models import ProductSubCategory
from ecommerce.serializers.subcategories import SubCategoryDetailSerializer
from ecommerce.serializers.subcategories import SubCategoryListSerializer


class SubCategoryListView(generics.ListAPIView):
    """
    API endpoint for listing subcategories.

    This view provides read-only access to subcategories with filtering,
    searching, and ordering capabilities.
    """

    queryset = ProductSubCategory.objects.filter(is_active=True)
    serializer_class = SubCategoryListSerializer
    permission_classes = [AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "category",
        "is_active",
    ]
    search_fields = [
        "name",
        "description",
        "category__name",
    ]
    ordering_fields = [
        "name",
        "sort_order",
        "created_at",
        "updated_at",
    ]
    ordering = ["sort_order", "name"]


class SubCategoryDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a single subcategory.

    This view provides read-only access to a specific subcategory
    with detailed information.
    """

    queryset = ProductSubCategory.objects.filter(is_active=True)
    serializer_class = SubCategoryDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"
