from django.urls import path

from .views import ListCreatePostView
from .views import PostCommentLikeCreateView
from .views import PostCommentLikeDestroyView
from .views import PostCommentListView
from .views import PostCommentRepliesView
from .views import PostCommentUpdateView
from .views import PostLikeCreateView
from .views import PostLikeDestroyView
from .views import PostSaveCreateView
from .views import PostSaveDestroyView
from .views import RetrieveUpdateDestroyPostView
from .views import ApproveReportView
from .views import CreateReportView
from .views import PostReportView
from .views import ReportDetailView
from .views import ReportListView

urlpatterns = [
    path("posts/", ListCreatePostView.as_view(), name="posts"),
    path(
        "posts/<slug:slug>/",
        RetrieveUpdateDestroyPostView.as_view(),
        name="post-detail",
    ),
    path("posts/<slug:slug>/like/", PostLikeCreateView.as_view(), name="post-like"),
    path(
        "posts/<slug:slug>/unlike/",
        PostLikeDestroyView.as_view(),
        name="post-unlike",
    ),
    path("posts/<slug:slug>/save/", PostSaveCreateView.as_view(), name="post-save"),
    path(
        "posts/<slug:slug>/unsave/",
        PostSaveDestroyView.as_view(),
        name="post-unsave",
    ),
    path(
        "posts/<slug:slug>/report/",
        PostReportView.as_view(),
        name="post-report",
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
        "posts/<str:post_slug>/comments/<int:comment_id>/replies/",
        PostCommentRepliesView.as_view(),
        name="post-comment-replies",
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
    # Report endpoints
    path("reports/", CreateReportView.as_view(), name="report-create"),
    path("reports/list/", ReportListView.as_view(), name="report-list"),
    path("reports/<int:id>/", ReportDetailView.as_view(), name="report-detail"),
    path(
        "reports/<int:id>/approve/",
        ApproveReportView.as_view(),
        name="report-approve",
    ),
]

app_name = "social_media"
