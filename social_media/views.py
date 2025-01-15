from django.http import HttpResponse
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Post
from .serializers import PostSerializer


class PostPageNumberPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 50


def index(request):
    return HttpResponse(":)")


class PostListView(ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.select_related("user").prefetch_related(
        "postimage_set",
        "comments",
        "likes",
    )
    pagination_class = PostPageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ["content", "user__username"]
