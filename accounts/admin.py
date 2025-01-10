from django.contrib import admin

from .models import LoginCode
from .models import Profile
from .models import VerificationCode


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "phone_number",
        "profile_type",
        "id_card_validation_status",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("full_name", "email", "phone_number")


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at", "expired_at")
    search_fields = ("user__name", "code")


@admin.register(LoginCode)
class LoginCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at", "expired_at")
    search_fields = ("user__name", "code")
