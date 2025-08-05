from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny

from ecommerce.models import ProductCategory
from ecommerce.serializers import CategoryDetailSerializer
from ecommerce.serializers import CategoryListSerializer


class CategoryListView(generics.ListAPIView):
    """
    List all active categories.
    This view provides a list of all active categories with basic information.
    Supports filtering, searching, and ordering.
    Permissions:
        - Public access (no authentication required)
    Filtering:
        - is_featured: Filter by featured status (true/false)
        - parent: Filter by parent category ID
        - parent__isnull: Filter root categories (true) or child categories (false)
    Search:
        - name: Search in category name
        - description: Search in category description
        - meta_title: Search in SEO meta title
    Ordering:
        - sort_order: Custom sort order
        - name: Alphabetical order
        - created_at: Creation date
        - Default: sort_order, name
    """

    queryset = ProductCategory.objects.filter(is_active=True)
    serializer_class = CategoryListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # Filtering
    filterset_fields = {
        "is_featured": ["exact"],
    }
    # Search
    search_fields = [
        "name",
    ]
    # Ordering
    ordering_fields = [
        "name",
        "created_at",
        "updated_at",
    ]
    ordering = ["name"]

    def get_queryset(self):
        """
        Override to provide optimized queryset with prefetch related.
        """
        queryset = super().get_queryset()
        # Prefetch children for better performance
        return queryset.prefetch_related(
            "children",
        )


class CategoryDetailView(generics.RetrieveAPIView):
    """
    Retrieve detailed information about a specific category.
    This view provides comprehensive information about a category,
    including hierarchical relationships, children, and ancestors.
    Permissions:
        - Public access (no authentication required)
    URL Parameters:
        - slug: The category slug
    Response includes:
        - Basic category information
        - Parent category data
        - List of direct children
        - List of ancestors (breadcrumb path)
        - Hierarchical metadata (level, is_root, is_leaf)
        - SEO metadata
    """

    queryset = ProductCategory.objects.filter(is_active=True)
    serializer_class = CategoryDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        """
        Override to provide optimized queryset with prefetch related.
        """
        queryset = super().get_queryset()
        # Prefetch related data for better performance
        return queryset.prefetch_related(
            "children",
            "parent",
        )
