from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline

from .models import Post
from .models import PostComment
from .models import PostCommentLike
from .models import PostImage
from .models import PostLike
from .models import PostSaved
from .models import PostView
from .models import Report


class PostImageInline(TabularInline):
    model = PostImage
    extra = 0
    fields = ("image",)


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = (
        "slug",
        "user",
        "content_summary",
        "is_potentially_harmful",
        "images_count",
        "likes_count",
        "comments_count",
        "views_count",
        "shared_count",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("user",)
    inlines = [PostImageInline]
    search_fields = ("user__username", "content")
    readonly_fields = ("slug", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    ordering = ("-created_at",)

    def content_summary(self, obj):
        return obj.content[:50]

    def images_count(self, obj):
        return obj.postimage_set.count()

    def views_count(self, obj):
        return obj.views.count()

    def likes_count(self, obj):
        return obj.likes.count()

    def comments_count(self, obj):
        return obj.comments.count()

    def shared_count(self, obj):
        return obj.shared_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user")


@admin.register(PostImage)
class PostImageAdmin(ModelAdmin):
    list_display = ("id", "post", "created_at")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("post")


@admin.register(PostComment)
class PostCommentAdmin(ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    search_fields = ("user__username", "post__content", "content")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "post")


@admin.register(PostView)
class PostViewAdmin(ModelAdmin):
    list_display = ("post", "user")


@admin.register(PostLike)
class PostLikeAdmin(ModelAdmin):
    list_display = ("user", "post", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "post__content")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user", "post")
    ordering = ("-created_at",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "post")


@admin.register(PostCommentLike)
class PostCommentLikeAdmin(ModelAdmin):
    """
    Admin interface for managing PostCommentLike instances.

    Provides a comprehensive interface for viewing and managing comment likes
    with optimized queries and useful display fields for administrators.

    Features:
    - Display user, comment, and creation timestamp
    - Search by username and comment content
    - Filter by creation date
    - Optimized queries with select_related
    - Autocomplete fields for better UX
    """

    list_display = ("user", "comment_summary", "post_title", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "comment__content", "comment__post__content")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user", "comment")
    ordering = ("-created_at",)

    @admin.display(
        description="Comment",
    )
    def comment_summary(self, obj):
        """
        Display a truncated version of the comment content.

        Args:
            obj: PostCommentLike instance

        Returns:
            str: First 50 characters of the comment content
        """
        return (
            obj.comment.content[:50] + "..."
            if len(obj.comment.content) > 50  # noqa: PLR2004
            else obj.comment.content
        )

    @admin.display(
        description="Post",
    )
    def post_title(self, obj):
        """
        Display the post content that contains the liked comment.

        Args:
            obj: PostCommentLike instance

        Returns:
            str: First 30 characters of the post content
        """
        post_content = obj.comment.post.content
        return post_content[:30] + "..." if len(post_content) > 30 else post_content  # noqa: PLR2004

    def get_queryset(self, request):
        """
        Optimize queryset with select_related for better performance.

        Args:
            request: HTTP request object

        Returns:
            QuerySet: Optimized queryset with related objects prefetched
        """
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "comment", "comment__post")


@admin.register(PostSaved)
class PostSavedAdmin(ModelAdmin):
    list_display = ("user", "post", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "post__content")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user", "post")
    ordering = ("-created_at",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "post")


@admin.register(Report)
class ReportAdmin(ModelAdmin):
    """
    Admin interface for managing reports.

    This admin interface provides comprehensive management of user reports,
    allowing moderators to review, approve, and track reports efficiently.
    """

    list_display = (
        "id",
        "post_link",
        "reporter",
        "post_author",
        "reason_display",
        "is_approved",
        "approved_by",
        "created_at",
        "restrict_user",
        "block_user",
    )

    list_filter = (
        "reason",
        "is_approved",
        "restrict_user",
        "block_user",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "post__user__username",
        "post__content",
        "detail_reason",
        "approved_by",
    )

    readonly_fields = (
        "created_at",
        "created_by",
        "updated_at",
    )

    autocomplete_fields = ("user", "post")

    ordering = ("-created_at",)

    fieldsets = (
        (
            "Report Information",
            {
                "fields": (
                    "post",
                    "user",
                    "reason",
                    "detail_reason",
                ),
            },
        ),
        (
            "User Actions",
            {
                "fields": (
                    "restrict_user",
                    "block_user",
                ),
            },
        ),
        (
            "Moderation",
            {
                "fields": (
                    "is_approved",
                    "approved_by",
                    "updated_by",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "created_by",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def get_queryset(self, request):
        """Optimize queries with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "post", "post__user")

    @admin.display(
        description="Post",
        ordering="post__slug",
    )
    def post_link(self, obj):
        """Create a clickable link to the reported post."""
        from django.urls import reverse
        from django.utils.html import format_html

        url = reverse("admin:social_media_post_change", args=[obj.post.pk])
        return format_html('<a href="{}">{}</a>', url, obj.post.slug)

    @admin.display(
        description="Reporter",
        ordering="user__username",
    )
    def reporter(self, obj):
        """Display the username of the reporter."""
        return obj.user.username

    @admin.display(
        description="Post Author",
        ordering="post__user__username",
    )
    def post_author(self, obj):
        """Display the username of the post author."""
        return obj.post.user.username

    @admin.display(
        description="Reason",
        ordering="reason",
    )
    def reason_display(self, obj):
        """Display the human-readable reason."""
        return obj.get_reason_display()

    def save_model(self, request, obj, form, change):
        """Auto-set updated_by when saving."""
        if change:  # Only for updates, not creation
            obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)

    actions = ["approve_reports", "unapprove_reports"]

    @admin.action(
        description="Approve selected reports",
    )
    def approve_reports(self, request, queryset):
        """Bulk approve selected reports."""
        updated = queryset.update(
            is_approved=True,
            approved_by=request.user.username,
            updated_by=request.user.username,
        )
        self.message_user(
            request,
            f"{updated} report(s) were successfully approved.",
        )

    @admin.action(
        description="Unapprove selected reports",
    )
    def unapprove_reports(self, request, queryset):
        """Bulk unapprove selected reports."""
        updated = queryset.update(
            is_approved=False,
            approved_by="",
            updated_by=request.user.username,
        )
        self.message_user(
            request,
            f"{updated} report(s) were successfully unapproved.",
        )
