from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Follow
from .models import LoginCode
from .models import Profile
from .models import VerificationCode


@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "phone_number",
        "profile_type",
        "id_card_validation_status",
        "get_follow_stats",
        "get_is_active",
        "created_at",
        "updated_at",
    )
    list_filter = [
        "profile_type",
        "id_card_validation_status",
        "user__is_active",
        "created_at",
    ]
    autocomplete_fields = ["country", "city"]
    readonly_fields = ("get_follow_stats", "get_is_active", "created_at", "updated_at")
    search_fields = ("full_name", "email", "phone_number", "user__username")
    date_hierarchy = "created_at"

    @admin.display(
        description="Followers/Following",
    )
    def get_follow_stats(self, obj):
        followers = obj.get_followers_count()
        following = obj.get_following_count()
        return f"{followers}/{following}"

    @admin.display(
        description="Active",
        boolean=True,
        ordering="user__is_active",
    )
    def get_is_active(self, obj):
        return obj.user.is_active

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "country", "city")


@admin.register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = [
        "get_follower_name",
        "get_following_name",
        "get_follower_type",
        "get_following_type",
        "created_at",
    ]
    list_filter = [
        "follower__profile_type",
        "following__profile_type",
        "created_at",
    ]
    search_fields = [
        "follower__full_name",
        "following__full_name",
        "follower__email",
        "following__email",
    ]
    readonly_fields = ["created_at"]
    autocomplete_fields = ["follower", "following"]
    date_hierarchy = "created_at"
    actions = ["delete_selected_follows"]

    @admin.display(description="Follower", ordering="follower__full_name")
    def get_follower_name(self, obj):
        return f"{obj.follower.full_name} ({obj.follower.email})"

    @admin.display(description="Following", ordering="following__full_name")
    def get_following_name(self, obj):
        return f"{obj.following.full_name} ({obj.following.email})"

    @admin.display(description="Follower Type", ordering="follower__profile_type")
    def get_follower_type(self, obj):
        return obj.follower.profile_type

    @admin.display(description="Following Type", ordering="following__profile_type")
    def get_following_type(self, obj):
        return obj.following.profile_type

    @admin.action(description="Delete selected follow relationships")
    def delete_selected_follows(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f"Successfully deleted {count} follow relationship(s).",
        )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "follower__user",
                "following__user",
            )
        )


@admin.register(VerificationCode)
class VerificationCodeAdmin(ModelAdmin):
    list_display = ("user", "code", "created_at", "expired_at")
    search_fields = ("user__name", "code")


@admin.register(LoginCode)
class LoginCodeAdmin(ModelAdmin):
    list_display = ("user", "code", "created_at", "expired_at")
    search_fields = ("user__name", "code")
