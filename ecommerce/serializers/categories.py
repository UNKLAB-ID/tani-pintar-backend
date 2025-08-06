from rest_framework import serializers

from ecommerce.models import ProductCategory


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing categories.

    This serializer provides essential information for category listings,
    optimized for performance and minimal data transfer.
    """

    subcategories = serializers.SerializerMethodField()

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

    def get_subcategories(self, obj):
        """Get all active subcategories of this category."""
        # Import here to avoid circular import
        from .subcategories import SubCategoryGetDetailSerializer

        subcategories = obj.subcategories.filter(is_active=True).order_by("name")
        return SubCategoryGetDetailSerializer(
            subcategories,
            many=True,
            context=self.context,
        ).data


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

    def get_subcategories(self, obj):
        """Get all active subcategories of this category."""
        # Import here to avoid circular import
        from .subcategories import SubCategoryGetDetailSerializer

        subcategories = obj.subcategories.filter(is_active=True).order_by("name")
        return SubCategoryGetDetailSerializer(
            subcategories,
            many=True,
            context=self.context,
        ).data


class CategorySimpleSerializer(serializers.ModelSerializer):
    """
    Serializer for simple category representation.

    This serializer provides minimal information about a category,
    suitable for nested representations.
    """

    class Meta:
        model = ProductCategory
        fields = [
            "id",
            "name",
            "slug",
        ]
        read_only_fields = [
            "id",
            "slug",
        ]
