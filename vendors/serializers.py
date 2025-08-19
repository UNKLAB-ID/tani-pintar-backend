from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from location.serializers import CitySerializer
from location.serializers import DistrictSerializer
from location.serializers import ProvinceSerializer
from vendors.models import Vendor


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
    user = serializers.StringRelatedField(read_only=True)

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
            "business_nib",
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


class VendorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "name",
            "vendor_type",
            "phone_number",
            "address",
            "logo",
            "full_name",
            "id_card_photo",
            "business_name",
            "business_number",
            "business_nib",
            "npwp",
            "province",
            "city",
            "district",
            "latitude",
            "longitude",
            "address_detail",
            "postal_code",
        ]

    def validate(self, attrs):  # noqa: C901
        vendor_type = attrs.get("vendor_type")

        if vendor_type == Vendor.TYPE_INDIVIDUAL:
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

        elif vendor_type == Vendor.TYPE_COMPANY:
            if not attrs.get("business_name"):
                raise serializers.ValidationError(
                    {"business_name": "Business name is required for company vendors."},
                )
            if not attrs.get("business_number"):
                raise serializers.ValidationError(
                    {
                        "business_number": "Business number is required for company vendors.",  # noqa: E501
                    },
                )
            if not attrs.get("business_nib"):
                raise serializers.ValidationError(
                    {
                        "business_nib": "Business NIB document is required for company vendors.",  # noqa: E501
                    },
                )
            if not attrs.get("npwp"):
                raise serializers.ValidationError(
                    {"npwp": "NPWP is required for company vendors."},
                )

        # Validate location hierarchy
        city = attrs.get("city")
        province = attrs.get("province")
        district = attrs.get("district")

        if city and province and city.province != province:
            raise serializers.ValidationError(
                {"city": "City must belong to the selected province."},
            )

        if district and city and district.city != city:
            raise serializers.ValidationError(
                {"district": "District must belong to the selected city."},
            )

        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        try:
            vendor = Vendor.objects.create(**validated_data)
            vendor.full_clean()
            return vendor  # noqa: TRY300
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)  # noqa: B904


class VendorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "name",
            "phone_number",
            "address",
            "logo",
            "full_name",
            "id_card_photo",
            "business_name",
            "business_number",
            "business_nib",
            "npwp",
            "province",
            "city",
            "district",
            "latitude",
            "longitude",
            "address_detail",
            "postal_code",
        ]

    def validate(self, attrs):  # noqa: C901
        instance = self.instance
        vendor_type = instance.vendor_type

        if vendor_type == Vendor.TYPE_INDIVIDUAL:
            full_name = attrs.get("full_name", instance.full_name)
            id_card_photo = attrs.get("id_card_photo", instance.id_card_photo)

            if not full_name:
                raise serializers.ValidationError(
                    {"full_name": "Full name is required for individual vendors."},
                )
            if not id_card_photo:
                raise serializers.ValidationError(
                    {
                        "id_card_photo": "ID card photo is required for individual vendors.",  # noqa: E501
                    },
                )

        elif vendor_type == Vendor.TYPE_COMPANY:
            business_name = attrs.get("business_name", instance.business_name)
            business_number = attrs.get("business_number", instance.business_number)
            business_nib = attrs.get("business_nib", instance.business_nib)
            npwp = attrs.get("npwp", instance.npwp)

            if not business_name:
                raise serializers.ValidationError(
                    {"business_name": "Business name is required for company vendors."},
                )
            if not business_number:
                raise serializers.ValidationError(
                    {
                        "business_number": "Business number is required for company vendors.",  # noqa: E501
                    },
                )
            if not business_nib:
                raise serializers.ValidationError(
                    {
                        "business_nib": "Business NIB document is required for company vendors.",  # noqa: E501
                    },
                )
            if not npwp:
                raise serializers.ValidationError(
                    {"npwp": "NPWP is required for company vendors."},
                )

        # Validate location hierarchy
        city = attrs.get("city", instance.city)
        province = attrs.get("province", instance.province)
        district = attrs.get("district", instance.district)

        if city and province and city.province != province:
            raise serializers.ValidationError(
                {"city": "City must belong to the selected province."},
            )

        if district and city and district.city != city:
            raise serializers.ValidationError(
                {"district": "District must belong to the selected city."},
            )

        return attrs

    def update(self, instance, validated_data):
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.full_clean()
            instance.save()
            return instance  # noqa: TRY300
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)  # noqa: B904
