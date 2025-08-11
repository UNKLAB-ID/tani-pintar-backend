from django.db import models
from rest_framework import serializers

from ecommerce.models import Product
from ecommerce.models import ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductImage model.
    Handles image upload, caption, primary status, and sort order.
    """

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "caption",
            "is_primary",
            "sort_order",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model with nested ProductImage handling.
    Supports creating and updating products with multiple images.
    Validates minimum 1 and maximum 10 images per product.
    """

    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        allow_empty=False,
    )
    user = serializers.StringRelatedField(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    primary_image = serializers.SerializerMethodField()
    image_count = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id",
            "user",
            "category",
            "category_name",
            "name",
            "slug",
            "description",
            "price",
            "stock",
            "status",
            "is_approve",
            "created_at",
            "updated_at",
            "images",
            "uploaded_images",
            "primary_image",
            "image_count",
        ]
        read_only_fields = [
            "id",
            "slug",
            "is_approve",
            "created_at",
            "updated_at",
        ]

    def get_primary_image(self, obj):
        """Get the primary image URL if exists."""
        primary_image = obj.primary_image
        if primary_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(primary_image.image.url)
        return None

    def validate_price(self, value):
        """Validate that price is positive."""
        if value <= 0:
            msg = "Price must be greater than 0."
            raise serializers.ValidationError(msg)
        return value

    def validate_stock(self, value):
        """Validate that stock is non-negative."""
        if value < 0:
            msg = "Stock cannot be negative."
            raise serializers.ValidationError(msg)
        return value

    def validate(self, attrs):
        """
        Validate the entire product data including image count.
        """
        # For create operation, validate image count
        if not self.instance:  # Creating new product
            uploaded_images = attrs.get("uploaded_images", [])

            if len(uploaded_images) < 1:
                msg = "At least 1 image is required for a product."
                raise serializers.ValidationError(msg)

            if len(uploaded_images) > 10:  # noqa: PLR2004
                msg = "Maximum 10 images are allowed per product."
                raise serializers.ValidationError(msg)

        return attrs

    def create(self, validated_data):
        """
        Create product with images.
        """
        uploaded_images = validated_data.pop("uploaded_images", [])

        # Set the user from request
        request = self.context.get("request")
        if request and request.user:
            validated_data["user"] = request.user

        # Create the product
        product = Product.objects.create(**validated_data)

        # Create images from uploaded_images
        for index, image in enumerate(uploaded_images):
            ProductImage.objects.create(
                product=product,
                image=image,
                sort_order=index,
                is_primary=(index == 0),  # First image is primary
            )

        return product

    def update(self, instance, validated_data):
        """
        Update product and optionally its images.
        """
        uploaded_images = validated_data.pop("uploaded_images", None)

        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle image updates if provided
        if uploaded_images is not None:
            # Validate total image count for update
            current_image_count = instance.images.count()
            new_images_count = len(uploaded_images)
            total_images = current_image_count + new_images_count

            if total_images > 10:  # noqa: PLR2004
                msg = f"Adding {new_images_count} images would exceed the maximum of 10 images per product."  # noqa: E501
                raise serializers.ValidationError(msg)

            # Add new images from uploaded_images
            if uploaded_images:
                max_sort_order = (
                    instance.images.aggregate(
                        max_order=models.Max("sort_order"),
                    )["max_order"]
                    or 0
                )

                for index, image in enumerate(uploaded_images):
                    ProductImage.objects.create(
                        product=instance,
                        image=image,
                        sort_order=max_sort_order + index + 1,
                        is_primary=False,  # Don't auto-set as primary on update
                    )

        return instance


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product list views.
    Only includes essential fields for better performance.
    """

    user = serializers.StringRelatedField(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    primary_image = serializers.SerializerMethodField()
    image_count = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id",
            "user",
            "category",
            "category_name",
            "name",
            "slug",
            "description",
            "price",
            "stock",
            "status",
            "is_approve",
            "created_at",
            "primary_image",
            "image_count",
        ]

    def get_primary_image(self, obj):
        """Get the primary image URL if exists."""
        primary_image = obj.primary_image
        if primary_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(primary_image.image.url)
        return None
