from django.urls import path

from .views import ListCreatePostView
from .views import PostCommentLikeCreateView
from .views import PostCommentLikeDestroyView
from .views import PostCommentListView
from .views import PostCommentUpdateView
from .views import PostLikeCreateView
from .views import PostLikeDestroyView
from .views import RetrieveUpdateDestroyPostView

urlpatterns = [
    path("posts/", ListCreatePostView.as_view(), name="posts"),
    path("posts/<slug:slug>/", RetrieveUpdateDestroyPostView.as_view(), name="post"),
    path("posts/<slug:slug>/like/", PostLikeCreateView.as_view(), name="post-like"),
    path(
        "posts/<slug:slug>/unlike/",
        PostLikeDestroyView.as_view(),
        name="post-unlike",
    ),
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
    path(
        "posts/<str:post_slug>/comments/<int:comment_id>/like/",
        PostCommentLikeCreateView.as_view(),
        name="post-comment-like",
    ),
    path(
        "posts/<str:post_slug>/comments/<int:comment_id>/unlike/",
        PostCommentLikeDestroyView.as_view(),
        name="post-comment-unlike",
    ),
]

app_name = "social_media"
