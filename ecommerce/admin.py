from django.contrib import admin

from .models import Product
from .models import ProductCategory
from .models import ProductImage
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


class ProductImageInline(admin.TabularInline):
    """
    Inline admin interface for ProductImage model.
    This allows managing product images directly from the Product admin page.
    """

    model = ProductImage
    extra = 1
    max_num = 10
    min_num = 1
    fields = ["image", "caption", "is_primary", "sort_order"]
    ordering = ["sort_order"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for Product model.
    This admin interface provides comprehensive management of products
    with inline image management, bulk actions, and approval system.
    """

    list_display = [
        "name",
        "user",
        "category",
        "price",
        "stock",
        "status",
        "is_approve",
        "created_at",
    ]
    list_filter = [
        "status",
        "is_approve",
        "category",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "name",
        "description",
        "user__username",
        "user__email",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    prepopulated_fields = {"slug": ("name",)}
    raw_id_fields = ["user"]

    # Only allow admin to change is_approve field
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)

        # If editing existing object, make slug readonly
        if obj:
            readonly_fields.append("slug")

        # If user is not superuser, make is_approve readonly
        if not request.user.is_superuser:
            readonly_fields.append("is_approve")
        return readonly_fields

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "user",
                    "category",
                    "name",
                    "slug",
                    "description",
                ),
            },
        ),
        (
            "Pricing & Inventory",
            {
                "fields": (
                    "price",
                    "stock",
                    "status",
                ),
            },
        ),
        (
            "Admin Controls",
            {
                "fields": ("is_approve",),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [ProductImageInline]

    actions = ["approve_products", "disapprove_products"]

    @admin.action(
        description="Approve selected products",
    )
    def approve_products(self, request, queryset):
        """Bulk action to approve selected products."""
        updated = queryset.update(is_approve=True)
        self.message_user(
            request,
            f"{updated} product(s) have been approved.",
        )

    @admin.action(
        description="Disapprove selected products",
    )
    def disapprove_products(self, request, queryset):
        """Bulk action to disapprove selected products."""
        updated = queryset.update(is_approve=False)
        self.message_user(
            request,
            f"{updated} product(s) have been disapproved.",
        )

    def get_queryset(self, request):
        """Optimize queries with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "category")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Admin interface for ProductImage model.
    This provides direct management of product images.
    """

    list_display = [
        "product",
        "caption",
        "is_primary",
        "sort_order",
        "created_at",
    ]
    list_filter = [
        "is_primary",
        "created_at",
    ]
    search_fields = [
        "product__name",
        "caption",
    ]
    readonly_fields = [
        "created_at",
    ]
    raw_id_fields = ["product"]
