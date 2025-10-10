from rest_framework.pagination import CursorPagination


class VendorCursorPagination(CursorPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    ordering = "-created_at"
    cursor_query_param = "cursor"
    page_size_query_description = "Number of results to return per page"
    cursor_query_description = "The pagination cursor value"
