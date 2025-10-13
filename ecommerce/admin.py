from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline
from unfold.contrib.filters.admin import AutocompleteSelectMultipleFilter
from unfold.decorators import display

from .models import Cart
from .models import Product
from .models import ProductCategory
from .models import ProductImage
from .models import ProductPrice
from .models import ProductSubCategory
from .models import UnitOfMeasure

# Inlines
# ------------------------------------------------------------------------------


class ProductImageInline(TabularInline):
    """
    Inline admin interface for ProductImage model.
    This allows managing product images directly from the Product admin page.
    """

    model = ProductImage
    fields = ["image", "caption"]
    ordering = ["created_at"]
    tab = True
    verbose_name = "Image"
    verbose_name_plural = "Images"


class ProductPriceInline(TabularInline):
    """
    Inline admin for ProductPrice model.
    Allows managing product prices directly from the Product admin.
    """

    model = ProductPrice
    tab = True
    fields = ["unit_of_measure", "price"]
    verbose_name = "Price"
    verbose_name_plural = "Prices"


@admin.register(ProductCategory)
class CategoryAdmin(SimpleHistoryAdmin, ModelAdmin):
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
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                ),
            },
        ),
        (
            "Status & Settings",
            {
                "fields": (
                    "is_active",
                    "is_featured",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "id",
                    ("created_at", "updated_at"),
                ),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(ProductSubCategory)
class SubCategoryAdmin(SimpleHistoryAdmin, ModelAdmin):
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
        ["category", AutocompleteSelectMultipleFilter],
        "created_at",
        "updated_at",
    ]
    list_filter_submit = True
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
    compressed_fields = True
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


# Product Admin
# ------------------------------------------------------------------------------


@admin.register(Product)
class ProductAdmin(SimpleHistoryAdmin, ModelAdmin):
    """
    Enhanced admin interface for Product model.
    This admin interface provides comprehensive management of products
    with inline image management, bulk actions, and approval system.
    """

    list_display = [
        "name",
        "user",
        "display_category",
        "available_stock",
        "display_status",
        "display_approval_status",
        "created_at",
    ]
    list_filter = [
        ["user", AutocompleteSelectMultipleFilter],
        ["category", AutocompleteSelectMultipleFilter],
        "status",
        "approval_status",
    ]
    list_filter_submit = True
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
    autocomplete_fields = ["user", "category"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    ("name", "approval_status"),
                    ("user", "category"),
                    "description",
                    "image",
                    "slug",
                ),
            },
        ),
        (
            "Inventory & Status",
            {
                "fields": (("status", "available_stock"),),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (("created_at", "updated_at"),),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [ProductImageInline, ProductPriceInline]

    actions = ["approve_products", "reject_products"]

    @display(description=_("Category"), label=True)
    def display_category(self, instance):
        return instance.category.name if instance.category else "-"

    @display(
        description=_("Status"),
        ordering="status",
        label={
            Product.STATUS_ACTIVE: "success",
            Product.STATUS_DRAFT: "warning",
            Product.STATUS_INACTIVE: "danger",
        },
    )
    def display_status(self, obj):
        return obj.status

    @display(
        description=_("Status"),
        ordering="status",
        label={
            Product.APPROVAL_APPROVED: "success",
            Product.APPROVAL_PENDING: "warning",
            Product.APPROVAL_REJECTED: "danger",
        },
    )
    def display_approval_status(self, obj):
        return obj.approval_status

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
class ProductImageAdmin(ModelAdmin):
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
        ["product", AutocompleteSelectMultipleFilter],
        "created_at",
    ]
    list_filter_submit = True
    search_fields = [
        "product__name",
        "caption",
    ]
    readonly_fields = [
        "created_at",
    ]
    autocomplete_fields = ["product"]
    ordering = ["-created_at"]


@admin.register(Cart)
class CartAdmin(ModelAdmin):
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
class UnitOfMeasureAdmin(SimpleHistoryAdmin, ModelAdmin):
    """
    Admin interface for UnitOfMeasure model.
    Manages master data for units of measurement.
    """

    list_display = [
        "name",
        "description",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "created_at",
    ]
    search_fields = [
        "name",
        "description",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]
    ordering = ["name"]
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "description",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "id",
                    ("created_at", "updated_at"),
                ),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(ProductPrice)
class ProductPriceAdmin(SimpleHistoryAdmin, ModelAdmin):
    """
    Admin interface for ProductPrice model.
    Manages product pricing with UOM.
    """

    list_display = [
        "product",
        "unit_of_measure",
        "price",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "unit_of_measure",
        "created_at",
    ]
    search_fields = [
        "product__name",
        "unit_of_measure__name",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]
    autocomplete_fields = ["product", "unit_of_measure"]
    fieldsets = (
        (
            "Pricing Information",
            {
                "fields": (
                    "product",
                    ("unit_of_measure", "price"),
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "id",
                    ("created_at", "updated_at"),
                ),
            },
        ),
    )
