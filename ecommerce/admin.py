from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import ProductCategory
from .models import ProductSubCategory


@admin.register(ProductCategory)
class CategoryAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for ProductCategory model.
    This admin interface provides comprehensive management of categories
    with hierarchical display, SEO fields, and bulk actions.
    """

    list_display = [
        "name",
        "slug",
        "is_active",
        "is_featured",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "is_active",
        "is_featured",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "name",
        "description",
        "slug",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]
    ordering = ["name"]


@admin.register(ProductSubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for ProductSubCategory model.
    This admin interface provides comprehensive management of subcategories
    with category relationships and display options.
    """

    list_display = [
        "name",
        "category",
        "slug",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "is_active",
        "category",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "name",
        "description",
        "slug",
        "category__name",
    ]
    prepopulated_fields = {
        "slug": ("name",),
    }
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "category_info",
    ]
    autocomplete_fields = ["category"]
    ordering = ["category__name", "name"]
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                    "category",
                ),
            },
        ),
        (
            "Category Information",
            {
                "fields": ("category_info",),
                "classes": ("collapse",),
            },
        ),
        (
            "Display Settings",
            {
                "fields": ("is_active",),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "id",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def get_queryset(self, request):
        """Optimize queries with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related("category")

    @admin.display(description="Category Information")
    def category_info(self, obj):
        """Display category information as clickable link."""
        if obj.category:
            url = reverse(
                "admin:ecommerce_productcategory_change",
                args=[obj.category.id],
            )
            return format_html(
                '<a href="{}">{}</a><br>' "<small>Featured: {} | Active: {}</small>",  # noqa: ISC001
                url,
                obj.category.name,
                "Yes" if obj.category.is_featured else "No",
                "Yes" if obj.category.is_active else "No",
            )
        return "No category assigned"
