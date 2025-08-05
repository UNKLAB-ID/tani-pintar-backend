from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for Category model.
    This admin interface provides comprehensive management of categories
    with hierarchical display, SEO fields, and bulk actions.
    """

    list_display = [
        "name_with_hierarchy",
        "slug",
        "is_active",
        "is_featured",
        "sort_order",
        "children_count",
        "level",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "is_active",
        "is_featured",
        "parent",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "name",
        "description",
        "slug",
        "meta_title",
        "meta_description",
    ]
    prepopulated_fields = {
        "slug": ("name",),
    }
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "level_display",
        "full_path_display",
        "children_count",
        "ancestors_display",
    ]
    autocomplete_fields = ["parent"]
    ordering = ["sort_order", "name"]
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                    "parent",
                ),
            },
        ),
        (
            "Hierarchy Information",
            {
                "fields": (
                    "level_display",
                    "full_path_display",
                    "ancestors_display",
                    "children_count",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "SEO Settings",
            {
                "fields": (
                    "meta_title",
                    "meta_description",
                ),
            },
        ),
        (
            "Display Settings",
            {
                "fields": (
                    "is_active",
                    "is_featured",
                    "sort_order",
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
    actions = [
        "make_active",
        "make_inactive",
        "make_featured",
        "make_unfeatured",
    ]

    def get_queryset(self, request):
        """Optimize queries with select_related and prefetch_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related("parent").prefetch_related("children")

    @admin.display(description="Category", ordering="name")
    def name_with_hierarchy(self, obj):
        """Display category name with visual hierarchy indication."""
        level = obj.get_level()
        indent = "└── " * level if level > 0 else ""
        color = ("green" if obj.is_featured else "black") if obj.is_active else "red"
        return format_html(
            '<span style="color: {};">{}{}</span>',
            color,
            indent,
            obj.name,
        )

    @admin.display(description="Level")
    def level(self, obj):
        """Display the hierarchical level of the category."""
        return obj.get_level()

    @admin.display(description="Children Count")
    def children_count(self, obj):
        """Display the number of direct children."""
        count = obj.children.count()
        if count > 0:
            url = reverse("admin:ecommerce_category_changelist")
            return format_html(
                '<a href="{}?parent__id__exact={}">{} children</a>',
                url,
                obj.id,
                count,
            )
        return "0"

    @admin.display(description="Level")
    def level_display(self, obj):
        """Display the hierarchical level for readonly field."""
        return obj.get_level()

    @admin.display(description="Full Path")
    def full_path_display(self, obj):
        """Display the full hierarchical path for readonly field."""
        return obj.get_full_path()

    @admin.display(description="Ancestors")
    def ancestors_display(self, obj):
        """Display ancestors as clickable links."""
        ancestors = obj.get_ancestors()
        if not ancestors:
            return "None (Root category)"
        links = []
        for ancestor in reversed(ancestors):  # Show from root to parent
            url = reverse("admin:ecommerce_category_change", args=[ancestor.id])
            links.append(format_html('<a href="{}">{}</a>', url, ancestor.name))
        return format_html(" > ".join(links))

    @admin.action(description="Mark selected categories as active")
    def make_active(self, request, queryset):
        """Bulk action to activate categories."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"{updated} category(ies) were successfully marked as active.",
        )

    @admin.action(description="Mark selected categories as inactive")
    def make_inactive(self, request, queryset):
        """Bulk action to deactivate categories."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"{updated} category(ies) were successfully marked as inactive.",
        )

    @admin.action(description="Mark selected categories as featured")
    def make_featured(self, request, queryset):
        """Bulk action to feature categories."""
        updated = queryset.update(is_featured=True)
        self.message_user(
            request,
            f"{updated} category(ies) were successfully marked as featured.",
        )

    @admin.action(description="Mark selected categories as unfeatured")
    def make_unfeatured(self, request, queryset):
        """Bulk action to unfeature categories."""
        updated = queryset.update(is_featured=False)
        self.message_user(
            request,
            f"{updated} category(ies) were successfully marked as unfeatured.",
        )
