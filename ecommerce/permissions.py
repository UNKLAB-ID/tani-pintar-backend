from rest_framework import permissions

from vendors.models import Vendor


class IsVendorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow vendors to create/edit products.

    Users must have a valid, approved vendor profile to create or modify products.
    Read access is allowed for all users.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if user has an approved vendor profile
        return self._has_approved_vendor(request.user)

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if user has an approved vendor profile
        if not self._has_approved_vendor(request.user):
            return False

        # For modification operations, ensure users can only modify their own products
        return obj.user == request.user

    def _has_approved_vendor(self, user):
        """Check if user has an approved vendor profile."""
        try:
            vendor = Vendor.objects.get(user=user)
        except Vendor.DoesNotExist:
            return False
        else:
            return vendor.review_status == Vendor.STATUS_APPROVED
