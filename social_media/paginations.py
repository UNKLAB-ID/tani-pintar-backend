from rest_framework.pagination import CursorPagination


class PostCursorPagination(CursorPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 50
    ordering = "-created_at"
    cursor_query_param = "cursor"
    page_size_query_description = "Number of results to return per page"
    cursor_query_description = "The pagination cursor value"


class PostCommentCursorPagination(CursorPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 50
    ordering = "created_at"
    page_size_query_description = "Number of results to return per page"
    cursor_query_description = "The pagination cursor value"
