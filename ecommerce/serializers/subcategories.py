from rest_framework import serializers

from ecommerce.models import ProductSubCategory


class SubCategoryListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing subcategories.

    This serializer provides essential information for subcategory listings,
    optimized for performance and minimal data transfer.
    """

    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = ProductSubCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "category_name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "category_name",
            "created_at",
            "updated_at",
        ]


class SubCategoryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed subcategory view.

    This serializer provides comprehensive information about a subcategory,
    including parent category details.
    """

    category_data = serializers.SerializerMethodField()

    class Meta:
        model = ProductSubCategory
        fields = [
            "id",
            "name",
            "description",
            "slug",
            "category",
            "category_data",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "category_data",
            "created_at",
            "updated_at",
        ]

    def get_category_data(self, obj):
        """Get parent category data."""
        if obj.category:
            return {
                "id": str(obj.category.id),
                "name": obj.category.name,
                "slug": obj.category.slug,
                "description": obj.category.description,
                "is_featured": obj.category.is_featured,
            }
        return None
