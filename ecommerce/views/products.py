from django.db import models
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ecommerce.models import Product
from ecommerce.models import ProductImage
from ecommerce.serializers.products import ProductImageSerializer
from ecommerce.serializers.products import ProductListSerializer
from ecommerce.serializers.products import ProductSerializer


class ProductViewSet(ModelViewSet):
    """
    ViewSet for Product model providing full CRUD operations.
    Features:
    - Create, Read, Update, Delete products
    - Filter by category and approval status
    - Search by name and description
    - Upload multiple images (min 1, max 10)
    - Separate serializers for list and detail views
    """

    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "status"]
    search_fields = ["name", "description"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return ProductListSerializer
        return ProductSerializer

    def get_queryset(self):
        """
        Get queryset with appropriate filtering based on user.
        Public list only shows approved products.
        Authenticated users can see their own products regardless of approval.
        """
        queryset = super().get_queryset()

        # Optimize queries
        queryset = queryset.select_related("user", "category").prefetch_related(
            "images",
        )

        # Filter based on user authentication and action
        if self.action == "list":
            # For list view, show only approved products to non-owners
            if self.request.user.is_authenticated:
                # Show user's own products + approved products from others
                queryset = queryset.filter(
                    Q(user=self.request.user) | Q(is_approve=True),
                ).distinct()
            else:
                # Anonymous users only see approved products
                queryset = queryset.filter(is_approve=True)
        elif self.action in ["retrieve", "update", "partial_update", "destroy"]:
            # For detail actions, users can only access their own products or approved ones  # noqa: E501
            if self.request.user.is_authenticated:
                queryset = queryset.filter(
                    Q(user=self.request.user) | Q(is_approve=True),
                ).distinct()
            else:
                queryset = queryset.filter(is_approve=True)

        # Additional filtering by category_id query parameter
        category_id = self.request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    def perform_create(self, serializer):
        """Set the user when creating a product."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Ensure users can only update their own products."""
        # Check if user owns the product
        if serializer.instance.user != self.request.user:
            return Response(
                {"detail": "You can only update your own products."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer.save()
        return None

    def perform_destroy(self, instance):
        """Ensure users can only delete their own products."""
        if instance.user != self.request.user:
            return Response(
                {"detail": "You can only delete your own products."},
                status=status.HTTP_403_FORBIDDEN,
            )
        instance.delete()
        return None

    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def public_list(self, request):
        """
        Public endpoint that only returns approved products.
        This endpoint is accessible without authentication.
        """
        queryset = self.get_queryset().filter(is_approve=True)

        # Apply search filtering
        search_query = request.query_params.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query),
            )

        # Apply category filtering
        category_id = request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(
                page,
                many=True,
                context={"request": request},
            )
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def add_images(self, request, pk=None):
        """
        Add additional images to an existing product.
        Validates that total images don't exceed 10.
        """
        product = self.get_object()

        # Check if user owns the product
        if product.user != request.user:
            return Response(
                {"detail": "You can only add images to your own products."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get uploaded images
        images = request.FILES.getlist("images")
        if not images:
            return Response(
                {"detail": "No images provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check total image count
        current_count = product.images.count()
        if current_count + len(images) > 10:  # noqa: PLR2004
            return Response(
                {
                    "detail": f"Cannot add {len(images)} images. Maximum 10 images allowed per product.",  # noqa: E501
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create new images
        max_sort_order = (
            product.images.aggregate(
                max_order=models.Max("sort_order"),
            )["max_order"]
            or 0
        )

        created_images = []
        for index, image in enumerate(images):
            product_image = ProductImage.objects.create(
                product=product,
                image=image,
                sort_order=max_sort_order + index + 1,
                is_primary=False,
            )
            created_images.append(product_image)

        serializer = ProductImageSerializer(
            created_images,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["delete"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def remove_image(self, request, pk=None):
        """
        Remove a specific image from a product.
        Ensures at least 1 image remains.
        """
        product = self.get_object()

        # Check if user owns the product
        if product.user != request.user:
            return Response(
                {"detail": "You can only remove images from your own products."},
                status=status.HTTP_403_FORBIDDEN,
            )

        image_id = request.data.get("image_id")
        if not image_id:
            return Response(
                {"detail": "image_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            image = ProductImage.objects.get(id=image_id, product=product)
        except ProductImage.DoesNotExist:
            return Response(
                {"detail": "Image not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if this is the last image
        if product.images.count() <= 1:
            return Response(
                {
                    "detail": "Cannot remove the last image. At least 1 image is required.",  # noqa: E501
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def my_products(self, request):
        """
        Get current user's products regardless of approval status.
        """
        queryset = self.get_queryset().filter(user=request.user)

        # Apply search filtering
        search_query = request.query_params.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query),
            )

        # Apply category filtering
        category_id = request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(
                page,
                many=True,
                context={"request": request},
            )
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)
