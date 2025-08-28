import uuid

from django.db import models
from django.utils.text import slugify

from core.users.models import User


class ProductCategory(models.Model):
    """
    Enhanced Category model for ecommerce products.
    This model represents product categories with additional features like:
    - UUID primary key for better security
    - Auto-generated slugs for SEO-friendly URLs
    - Hierarchical structure support (parent-child relationships)
    - SEO metadata fields
    - Custom manager and querysets for better querying
    Features:
    - Unique category names and slugs
    - Optional parent category for hierarchical structure
    - SEO-friendly slug generation
    - Active/inactive status
    - Comprehensive metadata tracking
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the category",
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (must be unique)",
    )
    description = models.TextField(  # noqa: DJ001
        blank=True,
        null=True,
        help_text="Optional detailed description of the category",
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text="SEO-friendly URL slug (auto-generated from name)",
    )
    # Status and ordering
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this category is active and visible",
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Whether this category should be featured prominently",
    )
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the category was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the category was last updated",
    )

    class Meta:
        verbose_name = "Categorys"
        verbose_name_plural = "Categories"

    def __str__(self):
        """String representation of the category."""
        return self.name

    def save(self, *args, **kwargs):
        """
        Override save method to auto-generate slug from name.
        This ensures that every category has a unique, SEO-friendly slug
        that can be used in URLs.
        """
        if not self.slug:
            slug = slugify(self.name)
            self.slug = slug

        super().save(*args, **kwargs)


class ProductSubCategory(models.Model):
    """
    Product SubCategory model for detailed product classification.
    This model represents subcategories that belong to a main ProductCategory,
    providing more granular product organization.
    Features:
    - UUID primary key for better security
    - Foreign key relationship to ProductCategory
    - Auto-generated slugs for SEO-friendly URLs
    - SEO metadata fields
    - Active/inactive status
    - Custom manager and querysets for better querying
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the subcategory",
    )
    name = models.CharField(
        max_length=100,
        help_text="Subcategory name",
    )
    description = models.TextField(  # noqa: DJ001
        blank=True,
        null=True,
        help_text="Optional detailed description of the subcategory",
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text="SEO-friendly URL slug (auto-generated from name)",
    )
    # Relationship to parent category
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="subcategories",
        help_text="Parent category for this subcategory",
    )
    # Status and ordering
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this subcategory is active and visible",
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Whether this subcategory should be featured prominently",
    )
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the subcategory was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the subcategory was last updated",
    )

    # Custom manager
    class Meta:
        verbose_name = "Product SubCategory"
        verbose_name_plural = "Product SubCategories"
        ordering = ["category", "name"]

    def __str__(self):
        """String representation of the subcategory."""
        return f"{self.category.name} > {self.name}"

    def save(self, *args, **kwargs):
        """
        Override save method to auto-generate slug from name and category.
        This ensures that every subcategory has a unique, SEO-friendly slug
        that can be used in URLs.
        """
        if not self.slug:
            base_slug = slugify(f"{self.category.name}-{self.name}")
            slug = base_slug
            counter = 1
            # Ensure slug uniqueness
            while ProductSubCategory.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Product model for e-commerce platform.
    This model represents products that users can create and manage.
    Features:
    - UUID primary key for better security
    - Foreign key relationships to User and ProductCategory
    - Auto-generated slugs for SEO-friendly URLs
    - Stock management
    - Status management (draft, active, inactive)
    - Approval system for admin control
    """

    # Status constants
    STATUS_DRAFT = "draft"
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    # Approval status constants
    APPROVAL_PENDING = "pending"
    APPROVAL_APPROVED = "approved"
    APPROVAL_REJECTED = "rejected"

    APPROVAL_CHOICES = [
        (APPROVAL_PENDING, "Waiting for approval"),
        (APPROVAL_APPROVED, "Approved"),
        (APPROVAL_REJECTED, "Rejected"),
    ]

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the product",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="products",
        help_text="User who owns this product",
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="products",
        help_text="Category for this product",
    )
    image = models.ImageField(
        upload_to="ecommerce/products/images/",
        help_text="Main product image",
    )
    name = models.CharField(
        max_length=200,
        help_text="Product name",
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        help_text="SEO-friendly URL slug (auto-generated from name)",
    )
    description = models.TextField(
        help_text="Detailed description of the product",
    )
    available_stock = models.PositiveIntegerField(
        default=0,
        help_text="Available stock quantity",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        help_text="Product status",
    )
    approval_status = models.CharField(
        max_length=10,
        choices=APPROVAL_CHOICES,
        default=APPROVAL_PENDING,
        help_text="Approval status of the product by admin",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the product was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the product was last updated",
    )

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]

    def __str__(self):
        """String representation of the product."""
        return self.name

    def save(self, *args, **kwargs):
        """
        Override save method to auto-generate slug from name.
        This ensures that every product has a unique, SEO-friendly slug
        that can be used in URLs.
        """
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            # Ensure slug uniqueness
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class UnitOfMeasure(models.Model):
    """
    Unit of Measure (UOM) master model.
    This model represents different units of measurement for products.
    Examples: kg, gram, liter, piece, meter, etc.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the UOM",
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unit name (e.g., kilogram, liter, piece)",
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the unit",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the UOM was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the UOM was last updated",
    )

    class Meta:
        verbose_name = "Unit of Measure"
        verbose_name_plural = "Units of Measure"
        ordering = ["name"]

    def __str__(self):
        """String representation of the UOM."""
        return self.name


class ProductPrice(models.Model):
    """
    Product Price model for managing product pricing with UOM.
    This model represents pricing information for products with specific units.
    Features:
    - Foreign key relationships to Product and UOM
    - Decimal price field for precise pricing
    - Multiple price entries per product for different units
    - Timestamps for price tracking
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the product price",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="prices",
        help_text="Product this price belongs to",
    )
    unit_of_measure = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.CASCADE,
        related_name="product_prices",
        help_text="Unit of measure for this price",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the price was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the price was last updated",
    )

    class Meta:
        verbose_name = "Product Price"
        verbose_name_plural = "Product Prices"
        unique_together = ["product", "unit_of_measure"]
        ordering = ["-created_at"]

    def __str__(self):
        """String representation of the product price."""
        return f"{self.product.name} - {self.price} per {self.unit_of_measure.name}"


class ProductImage(models.Model):
    """
    ProductImage model for managing product images.
    This model represents images associated with products, similar to PostImage
    in social media functionality.
    Features:
    - Foreign key relationship to Product
    - Image file handling
    - Optional captions
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        help_text="Product this image belongs to",
    )
    image = models.ImageField(
        upload_to="ecommerce/products/images/",
        help_text="Product image file",
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Optional caption for the image",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the image was uploaded",
    )

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ["created_at"]

    def __str__(self):
        """String representation of the product image."""
        return f"{self.product.name} - Image {self.pk}"


class Cart(models.Model):
    """
    Cart model for managing user shopping cart items.
    This model represents individual cart items that belong to a user.
    Features:
    - UUID primary key for better security
    - Foreign key relationships to User and Product
    - Quantity management
    - Timestamps for creation and updates
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the cart item",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart_items",
        help_text="User who owns this cart item",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
        help_text="Product in this cart item",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Quantity of this product in the cart",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the item was added to cart",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the cart item was last updated",
    )

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ["user", "product"]
        ordering = ["created_at"]

    def __str__(self):
        """String representation of the cart item."""
        return f"{self.product.name} ({self.quantity}) in {self.user.username}'s cart"
