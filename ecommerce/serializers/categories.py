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
            "subcategories",
        ]
        read_only_fields = [
            "id",
            "slug",
            "subcategories",
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
            "subcategories",
            "slug",
        ]
        read_only_fields = [
            "id",
            "slug",
            "subcategories",
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
