# Product Vendor Permission Requirements

## Overview
The product creation and modification endpoints now require users to have an **approved vendor profile** to perform write operations.

## Permission Details

### IsVendorOrReadOnly Permission
- **Location**: `ecommerce/permissions.py`
- **Applied to**: ProductListCreateView and ProductDetailView
- **Requirements**:
  - Read operations (GET): Allowed for all users
  - Write operations (POST, PUT, PATCH, DELETE): Requires approved vendor status

### Vendor Status Requirements
For a user to create or modify products, they must have:
1. A `Vendor` record in the vendors app
2. The vendor's `review_status` must be `"Approved"`

### API Responses
- **403 Forbidden**: User is authenticated but doesn't have approved vendor status
- **401 Unauthorized**: User is not authenticated
- **200/201**: Operation successful (user has approved vendor status)

## Implementation Details

### Permission Class (`ecommerce/permissions.py`)
```python
class IsVendorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow read operations for all users
        if request.method in permissions.READONLY_METHODS:
            return True

        # Require authenticated user with approved vendor for write operations
        return (request.user.is_authenticated and
                self._has_approved_vendor(request.user))

    def _has_approved_vendor(self, user):
        try:
            vendor = Vendor.objects.get(user=user)
        except Vendor.DoesNotExist:
            return False
        else:
            return vendor.review_status == Vendor.APPROVED
```

### Applied to Views
- `ProductListCreateView`: Vendor permission for POST (create)
- `ProductDetailView`: Vendor permission for PUT/PATCH/DELETE (update/delete)

### User Journey
1. User registers and gets authenticated
2. User creates a vendor profile through the vendors app
3. Admin reviews and approves the vendor profile
4. User can now create and modify products
5. If vendor status changes back to pending/rejected, user loses product creation permissions

## Migration Impact
- Existing products remain unaffected
- Existing users without vendor profiles can no longer create new products
- Existing users with pending vendor profiles cannot create products until approved
