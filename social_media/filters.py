import django_filters
from django_filters.rest_framework import FilterSet

from .models import Post


class PostFilter(FilterSet):
    """`
    Filter class for Post model to filter by user_id and profile_id.
    """

    user_id = django_filters.NumberFilter(
        field_name="user__id",
        lookup_expr="exact",
        help_text="Filter posts by user ID",
    )

    profile_id = django_filters.NumberFilter(
        label="Profile ID",
        field_name="user__profile__id",
        lookup_expr="exact",
        help_text="Filter posts by profile ID",
    )

    class Meta:
        model = Post
        fields = [
            "user_id",
            "profile_id",
        ]
