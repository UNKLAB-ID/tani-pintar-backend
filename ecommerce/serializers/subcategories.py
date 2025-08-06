from rest_framework import serializers

from ecommerce.models import ProductSubCategory


class SubCategoryListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing subcategories.

    This serializer provides essential information for subcategory listings,
    optimized for performance and minimal data transfer.
    """

    category = serializers.SerializerMethodField()

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
            "category_name",
            "created_at",
            "updated_at",
        ]

    def get_category(self, obj):
        """Get all active subcategories of this category."""
        # Import here to avoid circular import
        from .categories import CategorySimpleSerializer

        category = obj.category
        if category and category.is_active:
            return CategorySimpleSerializer(category, context=self.context).data
        return None


class SubCategoryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed subcategory view.

    This serializer provides comprehensive information about a subcategory,
    including parent category details.
    """

    category = serializers.SerializerMethodField()

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
            "category",
            "created_at",
            "updated_at",
        ]

    def get_category(self, obj):
        """Get all active subcategories of this category."""
        # Import here to avoid circular import
        from .categories import CategorySimpleSerializer

        category = obj.category
        if category and category.is_active:
            return CategorySimpleSerializer(category, context=self.context).data
        return None


class SubCategoryGetDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed subcategory view.

    This serializer provides comprehensive information about a subcategory,
    including parent category details.
    """

    class Meta:
        model = ProductSubCategory
        fields = [
            "id",
            "name",
            "description",
            "slug",
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
