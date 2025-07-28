from django.urls import path

from .views import ListCreatePostView
from .views import PostCommentListView
from .views import PostCommentUpdateView
from .views import RetrieveUpdateDestroyPostView

urlpatterns = [
    path("posts/", ListCreatePostView.as_view(), name="posts"),
    path("posts/<slug:slug>/", RetrieveUpdateDestroyPostView.as_view(), name="post"),
    path(
        "posts/<str:post_slug>/comments/",
        PostCommentListView.as_view(),
        name="post-comments",
    ),
    path(
        "posts/<str:post_slug>/comments/<int:comment_id>/",
        PostCommentUpdateView.as_view(),
        name="post-comment-update",
    ),
]

app_name = "social_media"
