from django.contrib import admin

from .models import Post
from .models import PostComment
from .models import PostCommentLike
from .models import PostImage
from .models import PostLike
from .models import PostSaved
from .models import PostView


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 0
    fields = ("image",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
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
class PostImageAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "created_at")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("post")


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    search_fields = ("user__username", "post__content", "content")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "post")


@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ("post", "user")


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
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
class PostCommentLikeAdmin(admin.ModelAdmin):
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
class PostSavedAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "post__content")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user", "post")
    ordering = ("-created_at",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "post")
