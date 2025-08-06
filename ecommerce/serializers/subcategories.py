from rest_framework import serializers

from ecommerce.models import ProductSubCategory
from ecommerce.serializers.categories import CategoryDetailSerializer


class SubCategoryListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing subcategories.

    This serializer provides essential information for subcategory listings,
    optimized for performance and minimal data transfer.
    """

    category = CategoryDetailSerializer(read_only=True)

    class Meta:
        model = ProductSubCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "created_at",
            "updated_at",
        ]


class SubCategoryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed subcategory view.

    This serializer provides comprehensive information about a subcategory,
    including parent category details.
    """

    category = CategoryDetailSerializer(read_only=True)

    class Meta:
        model = ProductSubCategory
        fields = [
            "id",
            "name",
            "description",
            "slug",
            "category",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "created_at",
            "updated_at",
        ]
