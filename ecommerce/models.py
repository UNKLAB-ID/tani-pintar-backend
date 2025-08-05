import uuid

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class CategoryQuerySet(models.QuerySet):
    """Custom QuerySet for Category model with useful filtering methods."""

    def active(self):
        """Return only active categories."""
        return self.filter(is_active=True)

    def inactive(self):
        """Return only inactive categories."""
        return self.filter(is_active=False)

    def by_name(self, name):
        """Filter categories by name (case insensitive)."""
        return self.filter(name__icontains=name)


class CategoryManager(models.Manager):
    """Custom manager for Category model."""

    def get_queryset(self):
        """Return CategoryQuerySet instead of default QuerySet."""
        return CategoryQuerySet(self.model, using=self._db)

    def active(self):
        """Get only active categories."""
        return self.get_queryset().active()

    def inactive(self):
        """Get only inactive categories."""
        return self.get_queryset().inactive()


class Category(models.Model):
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
    # Hierarchical structure
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        help_text="Parent category for hierarchical structure",
    )
    # SEO and metadata
    meta_title = models.CharField(
        max_length=160,
        blank=True,
        help_text="SEO meta title (recommended: 50-60 characters)",
    )
    meta_description = models.TextField(
        max_length=320,
        blank=True,
        help_text="SEO meta description (recommended: 150-160 characters)",
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
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Sort order for displaying categories",
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
    # Custom manager
    objects = CategoryManager()

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_featured"]),
            models.Index(fields=["sort_order"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        """String representation of the category."""
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        """
        Override save method to auto-generate slug from name.
        This ensures that every category has a unique, SEO-friendly slug
        that can be used in URLs.
        """
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            # Ensure slug uniqueness
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        # Set meta_title from name if not provided
        if not self.meta_title:
            self.meta_title = self.name
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Get the absolute URL for this category."""
        return reverse("ecommerce:category-detail", kwargs={"slug": self.slug})

    def get_full_path(self):
        """Get the full hierarchical path of the category."""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name

    def get_children(self):
        """Get all direct children of this category."""
        return self.children.active()

    def get_descendants(self):
        """Get all descendants (children, grandchildren, etc.) of this category."""
        descendants = []
        for child in self.get_children():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

    def get_ancestors(self):
        """Get all ancestors (parent, grandparent, etc.) of this category."""
        ancestors = []
        parent = self.parent
        while parent:
            ancestors.append(parent)
            parent = parent.parent
        return ancestors

    def is_root(self):
        """Check if this category is a root category (has no parent)."""
        return self.parent is None

    def is_leaf(self):
        """Check if this category is a leaf category (has no children)."""
        return not self.children.exists()

    def get_level(self):
        """Get the hierarchical level of this category (0 for root)."""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level
