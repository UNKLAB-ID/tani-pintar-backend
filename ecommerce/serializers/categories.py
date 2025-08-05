from rest_framework import serializers

from ecommerce.models import ProductCategory


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing categories.

    This serializer provides essential information for category listings,
    optimized for performance and minimal data transfer.
    """

    subcategories_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "subcategories_count",
            "is_active",
            "is_featured",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "subcategories_count",
            "created_at",
            "updated_at",
        ]

    def get_subcategories_count(self, obj):
        """Get the number of subcategories for this category."""
        return obj.subcategories.active().count()


class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed category view.

    This serializer provides comprehensive information about a category,
    including subcategories and SEO metadata.
    """

    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            "id",
            "name",
            "description",
            "slug",
            "meta_title",
            "meta_description",
            "is_active",
            "is_featured",
            "sort_order",
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

    def get_subcategories(self, obj):
        """Get all active subcategories of this category."""
        # Import here to avoid circular import
        from .subcategories import SubCategoryListSerializer

        subcategories = obj.subcategories.active().order_by("sort_order", "name")
        return SubCategoryListSerializer(
            subcategories,
            many=True,
            context=self.context,
        ).data
