from rest_framework import serializers

from ecommerce.models import ProductPrice
from ecommerce.models import UnitOfMeasure


class UnitOfMeasureListSerializer(serializers.ModelSerializer):
    """
    Serializer for UnitOfMeasure list view.
    Used for listing units of measure.
    """

    class Meta:
        model = UnitOfMeasure
        fields = [
            "id",
            "name",
        ]
        read_only_fields = fields


class UnitOfMeasureDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for UnitOfMeasure model.
    Used for nested representations in other serializers.
    """

    class Meta:
        model = UnitOfMeasure
        fields = ["id", "name"]
        read_only_fields = fields


class ProductPriceListSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductPrice list view.
    Includes nested UOM information.
    """

    unit_of_measure = UnitOfMeasureDetailSerializer(read_only=True)

    class Meta:
        model = ProductPrice
        fields = [
            "id",
            "unit_of_measure",
            "price",
        ]
        read_only_fields = fields


class CreateProductPriceSerializer(serializers.ModelSerializer):
    """
    Serializer for creating ProductPrice entries.
    """

    unit_of_measure_id = serializers.UUIDField()

    class Meta:
        model = ProductPrice
        fields = ["unit_of_measure_id", "price"]

    def validate_unit_of_measure_id(self, value):
        """Validate that the UOM exists."""
        try:
            UnitOfMeasure.objects.get(id=value)
        except UnitOfMeasure.DoesNotExist as exc:
            msg = "Unit of measure with this ID does not exist."
            raise serializers.ValidationError(msg) from exc
        return value

    def validate_price(self, value):
        """Validate that price is positive."""
        if value <= 0:
            msg = "Price must be greater than 0."
            raise serializers.ValidationError(msg)
        return value

    def create(self, validated_data):
        """Create ProductPrice with the validated UOM."""
        unit_of_measure_id = validated_data.pop("unit_of_measure_id")
        unit_of_measure = UnitOfMeasure.objects.get(id=unit_of_measure_id)
        validated_data["unit_of_measure"] = unit_of_measure
        return super().create(validated_data)


class UpdateProductPriceSerializer(serializers.ModelSerializer):
    """
    Serializer for updating ProductPrice entries.
    """

    class Meta:
        model = ProductPrice
        fields = ["price"]

    def validate_price(self, value):
        """Validate that price is positive."""
        if value <= 0:
            msg = "Price must be greater than 0."
            raise serializers.ValidationError(msg)
        return value
