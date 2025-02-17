from django.contrib import admin

from .models import Follow
from .models import LoginCode
from .models import Profile
from .models import VerificationCode


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "get_follow",
        "email",
        "phone_number",
        "profile_type",
        "id_card_validation_status",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("get_follow", "created_at", "updated_at")
    search_fields = ("full_name", "email", "phone_number")

    @admin.display(
        description="Follower/Following",
    )
    def get_follow(self, obj):
        return f"{obj.get_followers_count()}/{obj.get_following_count()}"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ["follower", "following", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at", "expired_at")
    search_fields = ("user__name", "code")


@admin.register(LoginCode)
class LoginCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at", "expired_at")
    search_fields = ("user__name", "code")
