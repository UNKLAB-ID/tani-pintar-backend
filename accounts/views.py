from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from core.users.models import User

from .models import Profile
from .models import VerificationCode
from .serializers import ConfirmRegistrationSerializer
from .serializers import RegisterSerializer


def index(request):
    return HttpResponse("accounts")


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    authentication_classes = []
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = User.objects.create_user(
                name=serializer.validated_data.get("name"),
                email=serializer.validated_data.get("email"),
                username=serializer.validated_data.get("email"),
                password=serializer.validated_data.get("password"),
                is_active=False,
            )

            profile = Profile.objects.create(
                user=user,
                full_name=serializer.validated_data.get("name"),
                email=serializer.validated_data.get("email"),
                phone_number=serializer.validated_data.get("phone_number"),
                id_card_file=serializer.validated_data.get("id_card_file"),
            )
            profile.generate_verification_code()

        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED,
        )


class ConfirmRegistrationView(UpdateAPIView):
    serializer_class = ConfirmRegistrationSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(username=serializer.validated_data.get("email"))

        # Bypass verification code for development
        if settings.DEBUG and serializer.validated_data.get("code") == "0000":
            user.is_active = True
            user.save()

            return Response(
                {"message": "User activated successfully"},
                status=status.HTTP_200_OK,
            )

        verification_code = VerificationCode.objects.filter(
            user=user,
            code=serializer.validated_data.get("code"),
        ).last()

        if not verification_code or verification_code.is_expired:
            return Response(
                {"message": "Invalid code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save()

        return Response(
            {"message": "User activated successfully"},
            status=status.HTTP_200_OK,
        )
