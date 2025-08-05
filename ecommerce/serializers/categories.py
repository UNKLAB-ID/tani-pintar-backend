from rest_framework import serializers

from ecommerce.models import ProductCategory
from ecommerce.serializers.subcategories import SubCategoryListSerializer


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing categories.

    This serializer provides essential information for category listings,
    optimized for performance and minimal data transfer.
    """

    subcategories = SubCategoryListSerializer(many=True, read_only=True)

    class Meta:
        model = ProductCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "subcategories",
            "is_active",
            "is_featured",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "subcategories",
            "created_at",
            "updated_at",
        ]


class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed category view.

    This serializer provides comprehensive information about a category,
    including subcategories and SEO metadata.
    """

    subcategories = SubCategoryListSerializer(many=True, read_only=True)

    class Meta:
        model = ProductCategory
        fields = [
            "id",
            "name",
            "description",
            "slug",
            "is_active",
            "is_featured",
            "subcategories",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "subcategories",
            "created_at",
            "updated_at",
        ]
