from rest_framework import serializers

from core.users.serializers import UserDetailSerializer
from location.serializers import CitySerializer
from location.serializers import DistrictSerializer
from location.serializers import ProvinceSerializer
from vendors.models import Vendor


class CreateIndividualVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "name",
            "vendor_type",
            "phone_number",
            "full_name",
            "id_card_photo",
            "logo",
            "province",
            "city",
            "district",
            "latitude",
            "longitude",
            "address_detail",
            "postal_code",
        ]
        extra_kwargs = {
            "vendor_type": {"default": Vendor.TYPE_INDIVIDUAL},
        }

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        validated_data["vendor_type"] = Vendor.TYPE_INDIVIDUAL
        return super().create(validated_data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.get("vendor_type") == Vendor.TYPE_INDIVIDUAL:
            if not attrs.get("full_name"):
                raise serializers.ValidationError(
                    {"full_name": "Full name is required for individual vendors."},
                )
            if not attrs.get("id_card_photo"):
                raise serializers.ValidationError(
                    {
                        "id_card_photo": "ID card photo is required for individual vendors.",  # noqa: E501
                    },
                )
        return attrs


class CreateCompanyVendorSerializer(serializers.ModelSerializer):
    business_nib = serializers.FileField(source="business_nib_file", write_only=True)
    npwp = serializers.CharField(source="npwp_number", write_only=True)
    npwp_file = serializers.FileField(write_only=True)
    business_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Vendor
        fields = [
            "name",
            "vendor_type",
            "phone_number",
            "business_name",
            "business_number",
            "business_nib",
            "npwp",
            "npwp_file",
            "logo",
            "province",
            "city",
            "district",
            "latitude",
            "longitude",
            "address_detail",
            "postal_code",
        ]
        extra_kwargs = {
            "vendor_type": {"default": Vendor.TYPE_COMPANY},
        }

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        validated_data["vendor_type"] = Vendor.TYPE_COMPANY
        return super().create(validated_data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.get("vendor_type") == Vendor.TYPE_COMPANY:
            if not attrs.get("business_number"):
                raise serializers.ValidationError(
                    {
                        "business_number": "Business number is required for company vendors.",  # noqa: E501
                    },
                )
            if not attrs.get("business_nib_file"):
                raise serializers.ValidationError(
                    {"business_nib": "NIB file is required for company vendors."},
                )
            if not attrs.get("npwp_number"):
                raise serializers.ValidationError(
                    {"npwp": "NPWP number is required for company vendors."},
                )
            if not attrs.get("npwp_file"):
                raise serializers.ValidationError(
                    {"npwp_file": "NPWP file is required for company vendors."},
                )
        return attrs


class UpdateIndividualVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "name",
            "phone_number",
            "full_name",
            "id_card_photo",
            "logo",
            "province",
            "city",
            "district",
            "latitude",
            "longitude",
            "address_detail",
            "postal_code",
        ]
        extra_kwargs = {
            "full_name": {"required": False},
            "id_card_photo": {"required": False},
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instance = self.instance
        if instance and instance.vendor_type == Vendor.TYPE_INDIVIDUAL:
            # Check if we're trying to clear required fields
            if (
                "full_name" in attrs
                and not attrs["full_name"]
                and not instance.full_name
            ):
                raise serializers.ValidationError(
                    {"full_name": "Full name is required for individual vendors."},
                )
            if (
                "id_card_photo" in attrs
                and not attrs["id_card_photo"]
                and not instance.id_card_photo
            ):
                raise serializers.ValidationError(
                    {
                        "id_card_photo": "ID card photo is required for individual vendors.",  # noqa: E501
                    },
                )
        return attrs


class UpdateCompanyVendorSerializer(serializers.ModelSerializer):
    business_nib = serializers.FileField(source="business_nib_file", required=False)
    npwp = serializers.CharField(source="npwp_number", required=False)
    npwp_file = serializers.FileField(required=False)
    business_name = serializers.CharField(required=False)

    class Meta:
        model = Vendor
        fields = [
            "name",
            "phone_number",
            "business_name",
            "business_number",
            "business_nib",
            "npwp",
            "npwp_file",
            "logo",
            "province",
            "city",
            "district",
            "latitude",
            "longitude",
            "address_detail",
            "postal_code",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instance = self.instance
        if instance and instance.vendor_type == Vendor.TYPE_COMPANY:
            # Check if we're trying to clear required fields
            if (
                "business_number" in attrs
                and not attrs["business_number"]
                and not instance.business_number
            ):
                raise serializers.ValidationError(
                    {
                        "business_number": "Business number is required for company vendors.",  # noqa: E501
                    },
                )
            if (
                "business_nib_file" in attrs
                and not attrs["business_nib_file"]
                and not instance.business_nib_file
            ):
                raise serializers.ValidationError(
                    {"business_nib": "NIB file is required for company vendors."},
                )
            if (
                "npwp_number" in attrs
                and not attrs["npwp_number"]
                and not instance.npwp_number
            ):
                raise serializers.ValidationError(
                    {"npwp": "NPWP number is required for company vendors."},
                )
            if (
                "npwp_file" in attrs
                and not attrs["npwp_file"]
                and not instance.npwp_file
            ):
                raise serializers.ValidationError(
                    {"npwp_file": "NPWP file is required for company vendors."},
                )
        return attrs


class VendorListSerializer(serializers.ModelSerializer):
    vendor_type_display = serializers.CharField(
        source="get_vendor_type_display",
        read_only=True,
    )
    review_status_display = serializers.CharField(
        source="get_review_status_display",
        read_only=True,
    )
    province = ProvinceSerializer(read_only=True)
    city = CitySerializer(read_only=True)

    class Meta:
        model = Vendor
        fields = [
            "id",
            "name",
            "vendor_type",
            "vendor_type_display",
            "review_status",
            "review_status_display",
            "province",
            "city",
            "logo",
            "created_at",
        ]


class VendorDetailSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    vendor_type_display = serializers.CharField(
        source="get_vendor_type_display",
        read_only=True,
    )
    review_status_display = serializers.CharField(
        source="get_review_status_display",
        read_only=True,
    )
    province = ProvinceSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    district = DistrictSerializer(read_only=True)

    # Add fields that might not exist in model but are expected in tests
    address = serializers.SerializerMethodField()
    business_name = serializers.SerializerMethodField()
    npwp = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = [
            "id",
            "user",
            "name",
            "vendor_type",
            "vendor_type_display",
            "phone_number",
            "address",
            "logo",
            "full_name",
            "id_card_photo",
            "business_name",
            "business_number",
            "business_nib_file",
            "npwp",
            "province",
            "city",
            "district",
            "latitude",
            "longitude",
            "address_detail",
            "postal_code",
            "review_status",
            "review_status_display",
            "review_notes",
            "created_at",
            "updated_at",
        ]

    def get_address(self, obj):
        return getattr(obj, "address", obj.address_detail or "")

    def get_business_name(self, obj):
        return getattr(obj, "business_name", "")

    def get_npwp(self, obj):
        return getattr(obj, "npwp_number", "")
