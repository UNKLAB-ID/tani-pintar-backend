from django.contrib import admin
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
                "fields": (
                    "business_number",
                    "business_nib_file",
                    "npwp_number",
                    "npwp_file",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Location Information",
            {
                "fields": (
                    "province",
                    "city",
                    "district",
                    "address_detail",
                    "postal_code",
                    "latitude",
                    "longitude",
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
