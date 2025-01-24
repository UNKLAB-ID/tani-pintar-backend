from django.contrib import admin

from .models import Post
from .models import PostComment
from .models import PostImage
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
        "images_count",
        "likes_count",
        "comments_count",
        "views_count",
        "shared_count",
        "created_at",
        "updated_at",
    )
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
        return queryset.select_related("user").prefetch_related("likes")


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
