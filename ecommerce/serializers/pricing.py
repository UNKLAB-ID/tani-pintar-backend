from rest_framework import serializers

from ecommerce.models import ProductPrice
from ecommerce.models import UnitOfMeasure


class UnitOfMeasureSerializer(serializers.ModelSerializer):
    """
    Serializer for UnitOfMeasure model.
    Used for both list and detail views.
    """

    class Meta:
        model = UnitOfMeasure
        fields = [
            "id",
            "name",
            "abbreviation",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UnitOfMeasureSimpleSerializer(serializers.ModelSerializer):
    """
    Simple serializer for UnitOfMeasure model.
    Used for nested representations in other serializers.
    """

    class Meta:
        model = UnitOfMeasure
        fields = ["id", "name", "abbreviation"]
        read_only_fields = fields


class ProductPriceSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductPrice model.
    Includes nested UOM information.
    """

    unit_of_measure = UnitOfMeasureSimpleSerializer(read_only=True)

    class Meta:
        model = ProductPrice
        fields = [
            "id",
            "unit_of_measure",
            "price",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CreateProductPriceSerializer(serializers.ModelSerializer):
    """
    Serializer for creating ProductPrice entries.
    """

    class Meta:
        model = ProductPrice
        fields = ["unit_of_measure", "price", "is_active"]

    def validate_price(self, value):
        """Validate that price is positive."""
        if value <= 0:
            msg = "Price must be greater than 0."
            raise serializers.ValidationError(msg)
        return value


class UpdateProductPriceSerializer(serializers.ModelSerializer):
    """
    Serializer for updating ProductPrice entries.
    """

    class Meta:
        model = ProductPrice
        fields = ["price", "is_active"]

    def validate_price(self, value):
        """Validate that price is positive."""
        if value <= 0:
            msg = "Price must be greater than 0."
            raise serializers.ValidationError(msg)
        return value
