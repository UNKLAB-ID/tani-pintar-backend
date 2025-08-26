from django.contrib import admin

from .models import Cart
from .models import Product
from .models import ProductCategory
from .models import ProductImage
from .models import ProductPrice
from .models import ProductSubCategory
from .models import UnitOfMeasure


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
    min_num = 0
    fields = ["image", "caption"]
    ordering = ["created_at"]


class ProductPriceInline(admin.TabularInline):
    """
    Inline admin for ProductPrice model.
    Allows managing product prices directly from the Product admin.
    """

    model = ProductPrice
    extra = 1
    fields = ["unit_of_measure", "price", "is_active"]


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
        "available_stock",
        "status",
        "approval_status",
        "created_at",
    ]
    list_filter = [
        "status",
        "approval_status",
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
        "slug",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = ["user"]

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
                    "image",
                ),
            },
        ),
        (
            "Inventory & Status",
            {
                "fields": (
                    "available_stock",
                    "status",
                ),
            },
        ),
        (
            "Admin Controls",
            {
                "fields": ("approval_status",),
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

    inlines = [ProductImageInline, ProductPriceInline]

    actions = ["approve_products", "reject_products"]

    @admin.action(
        description="Approve selected products",
    )
    def approve_products(self, request, queryset):
        """Bulk action to approve selected products."""
        updated = queryset.update(approval_status=Product.APPROVAL_APPROVED)
        self.message_user(
            request,
            f"{updated} product(s) have been approved.",
        )

    @admin.action(
        description="Reject selected products",
    )
    def reject_products(self, request, queryset):
        """Bulk action to reject selected products."""
        updated = queryset.update(approval_status=Product.APPROVAL_REJECTED)
        self.message_user(
            request,
            f"{updated} product(s) have been rejected.",
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
        "created_at",
    ]
    list_filter = [
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


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Admin interface for Cart model.
    Allows full CRUD operations for managing user cart items.
    """

    list_display = [
        "user",
        "product",
        "quantity",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "user__username",
        "user__email",
        "product__name",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = ["user", "product"]


@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    """
    Admin interface for UnitOfMeasure model.
    Manages master data for units of measurement.
    """

    list_display = [
        "name",
        "abbreviation",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "is_active",
        "created_at",
    ]
    search_fields = [
        "name",
        "abbreviation",
        "description",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    """
    Admin interface for ProductPrice model.
    Manages product pricing with UOM.
    """

    list_display = [
        "product",
        "unit_of_measure",
        "price",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "is_active",
        "unit_of_measure",
        "created_at",
    ]
    search_fields = [
        "product__name",
        "unit_of_measure__name",
        "unit_of_measure__abbreviation",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = ["product", "unit_of_measure"]
