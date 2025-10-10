from django.contrib import admin
from django.core.validators import EMPTY_VALUES
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import AutocompleteSelectMultipleFilter
from unfold.contrib.filters.admin import DropdownFilter
from unfold.decorators import display

from vendors.models import Vendor


# Custom Filters
# ------------------------------------------------------------------------------
class VendorTypeDropdownFilter(DropdownFilter):
    title = _("Type")
    parameter_name = "vendor_type"

    def lookups(self, request, model_admin):
        return Vendor.TYPE_CHOICES

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            return queryset.filter(vendor_type=self.value())

        return queryset


class VendorReviewStatusDropdownFilter(DropdownFilter):
    title = _("Review Status")
    parameter_name = "vendor_review_status"

    def lookups(self, request, model_admin):
        return Vendor.REVIEW_STATUS_CHOICES

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            return queryset.filter(review_status=self.value())

        return queryset


@admin.register(Vendor)
class VendorAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = [
        "name",
        "display_vendor_type",
        "user",
        "phone_number",
        "display_review_status",
        "province",
        "city",
        "district",
        "created_at",
    ]
    list_filter = (
        VendorTypeDropdownFilter,
        VendorReviewStatusDropdownFilter,
        ["province", AutocompleteSelectMultipleFilter],
        ["city", AutocompleteSelectMultipleFilter],
        ["district", AutocompleteSelectMultipleFilter],
    )
    list_filter_submit = True
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
    ordering = ["-created_at"]

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

    # List View Custom Field
    # ------------------------------------------------------------------------------
    @display(
        description=_("Review Status"),
        label={
            Vendor.STATUS_PENDING: "warning",
            Vendor.STATUS_APPROVED: "success",
            Vendor.STATUS_REJECTED: "danger",
            Vendor.STATUS_RESUBMISSION: "",
        },
    )
    def display_review_status(self, obj):
        return obj.review_status

    @display(
        description=_("Vendor Type"),
        label={
            Vendor.TYPE_INDIVIDUAL: "info",
            Vendor.TYPE_COMPANY: "success",
        },
    )
    def display_vendor_type(self, obj):
        return obj.vendor_type

    # Permission
    # ------------------------------------------------------------------------------

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
