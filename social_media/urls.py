from django.urls import path

from .views import ListCreatePostView
from .views import PostCommentListView
from .views import RetrieveUpdateDestroyPostView

urlpatterns = [
    path("posts/", ListCreatePostView.as_view(), name="posts"),
    path("posts/<slug:slug>/", RetrieveUpdateDestroyPostView.as_view(), name="post"),
    path(
        "posts/<str:post_slug>/comments/",
        PostCommentListView.as_view(),
        name="post-comments",
    ),
]

app_name = "social_media"
