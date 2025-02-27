from django.urls import path

from . import views
from .views import ListCreatePostView
from .views import PostCommentListView
from .views import RetrieveUpdateDestroyPostView

urlpatterns = [
    path("posts/", ListCreatePostView.as_view(), name="post"),
    path("posts/<slug:slug>", RetrieveUpdateDestroyPostView.as_view(), name="post"),
    path(
        "posts/<str:post_slug>/comments/",
        PostCommentListView.as_view(),
        name="post-comments",
    ),
    path("", views.index, name="index"),
]

app_name = "social_media"
