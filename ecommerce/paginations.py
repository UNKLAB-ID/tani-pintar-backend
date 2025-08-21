from rest_framework.pagination import CursorPagination


class CartCursorPagination(CursorPagination):
    """
    Cursor pagination for cart items.
    Orders by creation date, newest first.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    ordering = "-created_at"  # Order by creation date, newest first


class ProductCursorPagination(CursorPagination):
    """
    Cursor pagination for products.
    Orders by creation date, newest first.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    ordering = "-created_at"  # Order by creation date, newest first
