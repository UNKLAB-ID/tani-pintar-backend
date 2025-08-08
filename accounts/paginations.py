from rest_framework.pagination import CursorPagination


class FollowCursorPagination(CursorPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    ordering = "-id"  # Order by Profile ID, newest first
