from django.db import transaction
from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from core.users.models import User

from .models import Profile
from .models import VerificationCode
from .serializers import ConfirmLoginSerializer
from .serializers import ConfirmRegistrationSerializer
from .serializers import LoginSerializer
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


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = Profile.objects.filter(
            email=serializer.validated_data.get("email"),
        ).last()
        profile.generate_login_code()

        return Response({"message": "Login code sent successfully"})


class ConfirmRegistrationView(UpdateAPIView):
    serializer_class = ConfirmRegistrationSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(username=serializer.validated_data.get("email"))

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

        token = RefreshToken.for_user(user)
        return Response(
            {
                "message": "User activated successfully",
                "data": {"access": str(token.access_token), "refresh": str(token)},
            },
            status=status.HTTP_200_OK,
        )


class ConfirmLoginView(GenericAPIView):
    serializer_class = ConfirmLoginSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(username=serializer.validated_data.get("email"))

        token = RefreshToken.for_user(user)
        return Response(
            {"access": str(token.access_token), "refresh": str(token)},
            status=status.HTTP_200_OK,
        )


class RefreshTokenView(APIView):
    """
    Takes a refresh token and returns new access and refresh tokens
    """

    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Verify and create new tokens
            token = RefreshToken(refresh_token)
            data = {
                "access": str(token.access_token),
                "refresh": str(token),
            }

            return Response(data, status=status.HTTP_200_OK)

        except TokenError:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
