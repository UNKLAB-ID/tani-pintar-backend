from django.contrib import admin
from unfold.admin import ModelAdmin

from vendors.models import Vendor


@admin.register(Vendor)
class VendorAdmin(ModelAdmin):
    list_display = [
        "name",
        "vendor_type",
        "user",
        "review_status",
        "created_at",
        "updated_at",
    ]
    list_filter = ["vendor_type", "review_status", "created_at"]
    search_fields = ["name", "user__email", "user__username"]
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = ["user", "province", "city", "district"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("user", "name", "vendor_type", "phone_number", "logo"),
            },
        ),
        (
            "Individual Vendor Fields",
            {
                "fields": ("full_name", "id_card_photo"),
                "classes": ("collapse",),
            },
        ),
        (
            "Company Vendor Fields",
            {
                "fields": ("business_name", "business_number", "business_nib", "npwp"),
                "classes": ("collapse",),
            },
        ),
        (
            "Location Information",
            {
                "fields": (
                    "address",
                    "province",
                    "city",
                    "district",
                    "latitude",
                    "longitude",
                    "address_detail",
                    "postal_code",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Review Information",
            {
                "fields": ("review_status", "review_notes"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
