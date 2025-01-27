from django.urls import path

from . import views
from .views import PostCommentListView
from .views import PostListView
from .views import RetrieveUpdateDestroyPostView

urlpatterns = [
    path("posts/", PostListView.as_view(), name="post"),
    path("posts/<slug:slug>", RetrieveUpdateDestroyPostView.as_view(), name="post"),
    path(
        "posts/<str:post_slug>/comments/",
        PostCommentListView.as_view(),
        name="post-comments",
    ),
    path("", views.index, name="index"),
]

app_name = "social_media"
