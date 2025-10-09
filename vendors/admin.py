from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from vendors.models import Vendor


@admin.register(Vendor)
class VendorAdmin(ModelAdmin):
    list_display = [
        "name",
        "vendor_type",
        "user",
        "phone_number",
        "review_status",
        "province",
        "city",
        "created_at",
    ]
    list_filter = ["vendor_type", "review_status", "province", "city", "created_at"]
    search_fields = [
        "name",
        "user__email",
        "user__username",
        "phone_number",
        "full_name",
        "business_number",
        "province__name",
        "city__name",
        "district__name",
    ]
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = ["user", "province", "city", "district"]

    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": (
                    ("user", "name"),
                    ("vendor_type", "phone_number"),
                    ("review_notes", "review_status"),
                    ("created_at", "updated_at"),
                ),
                "classes": ["tab"],
            },
        ),
        (
            _("Location & Address"),
            {
                "fields": (
                    ("province", "city"),
                    "district",
                    ("address_detail", "postal_code"),
                    ("latitude", "longitude"),
                ),
                "classes": ["tab"],
            },
        ),
        (
            _("Personal Vendor"),
            {
                "fields": (
                    "full_name",
                    ("id_card_photo", "logo"),
                ),
                "classes": ["tab"],
            },
        ),
        (
            _("Company Vendor"),
            {
                "fields": (
                    ("business_number", "npwp_number"),
                    ("business_nib_file", "npwp_file"),
                ),
                "classes": ["tab"],
            },
        ),
    )

    def has_delete_permission(self, request, obj=None):
        if obj and obj.review_status in [
            Vendor.STATUS_APPROVED,
            Vendor.STATUS_REJECTED,
            Vendor.STATUS_RESUBMISSION,
        ]:
            return False

        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj and obj.review_status in [
            Vendor.STATUS_APPROVED,
            Vendor.STATUS_REJECTED,
            Vendor.STATUS_RESUBMISSION,
        ]:
            return False

        return super().has_change_permission(request, obj)
