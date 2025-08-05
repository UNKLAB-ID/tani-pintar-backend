from rest_framework import serializers

from ecommerce.models import Category


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing categories.

    This serializer provides essential information for category listings,
    optimized for performance and minimal data transfer.
    """

    children_count = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source="parent.name", read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "parent_name",
            "is_active",
            "is_featured",
            "sort_order",
            "children_count",
            "level",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "children_count",
            "level",
            "created_at",
            "updated_at",
        ]

    def get_children_count(self, obj):
        """Get the number of direct children for this category."""
        return obj.children.active().count()

    def get_level(self, obj):
        """Get the hierarchical level of this category."""
        return obj.get_level()


class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed category view.
    This serializer provides comprehensive information about a category,
    including hierarchical relationships and SEO metadata.
    """

    children = serializers.SerializerMethodField()
    ancestors = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    is_root = serializers.SerializerMethodField()
    is_leaf = serializers.SerializerMethodField()
    parent_data = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "slug",
            "parent_data",
            "meta_title",
            "meta_description",
            "is_active",
            "is_featured",
            "sort_order",
            "children",
            "ancestors",
            "full_path",
            "level",
            "is_root",
            "is_leaf",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "children",
            "ancestors",
            "full_path",
            "level",
            "is_root",
            "is_leaf",
            "created_at",
            "updated_at",
        ]

    def get_children(self, obj):
        """Get all direct children of this category."""
        children = obj.get_children()
        return CategoryListSerializer(children, many=True, context=self.context).data

    def get_ancestors(self, obj):
        """Get all ancestors of this category."""
        ancestors = obj.get_ancestors()
        return [
            {
                "id": str(ancestor.id),
                "name": ancestor.name,
                "slug": ancestor.slug,
            }
            for ancestor in ancestors
        ]

    def get_full_path(self, obj):
        """Get the full hierarchical path of the category."""
        return obj.get_full_path()

    def get_level(self, obj):
        """Get the hierarchical level of this category."""
        return obj.get_level()

    def get_is_root(self, obj):
        """Check if this category is a root category."""
        return obj.is_root()

    def get_is_leaf(self, obj):
        """Check if this category is a leaf category."""
        return obj.is_leaf()

    def get_parent_data(self, obj):
        """Get parent category data if exists."""
        if obj.parent:
            return {
                "id": str(obj.parent.id),
                "name": obj.parent.name,
                "slug": obj.parent.slug,
            }
        return None
