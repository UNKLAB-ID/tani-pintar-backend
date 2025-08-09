from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import CreateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import ProfileSerializer
from core.users.models import User

from .models import Profile
from .models import VerificationCode
from .paginations import FollowCursorPagination
from .serializers import ConfirmLoginSerializer
from .serializers import ConfirmRegistrationSerializer
from .serializers import FollowActionSerializer
from .serializers import LoginSerializer
from .serializers import ProfileFollowerAndFollowingListSerializer
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
                username=serializer.validated_data.get("phone_number"),
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

        user = User.objects.filter(
            username=serializer.validated_data.get("phone_number"),
        ).last()
        profile = Profile.objects.filter(user=user).last()
        profile.generate_login_code()

        return Response({"message": "Login code sent successfully"})


class ConfirmRegistrationView(UpdateAPIView):
    serializer_class = ConfirmRegistrationSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(username=serializer.validated_data.get("phone_number"))
        code = serializer.validated_data.get("code")

        # Allow '0000' code in DEBUG mode
        if settings.DEBUG and code == "0000":
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

        verification_code = VerificationCode.objects.filter(
            user=user,
            code=code,
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

        user = User.objects.get(username=serializer.validated_data.get("phone_number"))

        token = RefreshToken.for_user(user)
        return Response(
            {"access": str(token.access_token), "refresh": str(token)},
            status=status.HTTP_200_OK,
        )


class RefreshTokenView(APIView):
    """
    Takes a refresh token and returns new access and refresh tokens
    """

    authentication_classes = []
    permission_classes = []

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


class ProfileView(APIView):
    serializer_class = ProfileSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.select_related("user").get(user=request.user)
        except Profile.DoesNotExist:
            return Response(
                {"message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(profile, context={"request": request})
        return Response(serializer.data)


class ProfileDetailAPIView(RetrieveAPIView):
    queryset = Profile.objects.select_related("user").all()
    serializer_class = ProfileSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = []  # No permission required to get specific user profile
    lookup_field = "id"
    lookup_url_kwarg = "profile_id"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class FollowUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        """Follow a user"""
        try:
            target_user = User.objects.get(id=user_id)
            target_profile = Profile.objects.get(user=target_user)
            current_profile = Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Profile.DoesNotExist:
            return Response(
                {"error": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if already following
        if current_profile.is_following(target_profile):
            return Response(
                {"error": "Already following this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Prevent self-follow (additional check, though model constraint handles this)
        if current_profile == target_profile:
            return Response(
                {"error": "Cannot follow yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Follow the user
        current_profile.follow(target_profile)

        serializer = FollowActionSerializer(
            {
                "message": "Successfully followed user",
                "is_following": True,
                "followers_count": target_profile.get_followers_count(),
            },
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        """Unfollow a user"""
        try:
            target_user = User.objects.get(id=user_id)
            target_profile = Profile.objects.get(user=target_user)
            current_profile = Profile.objects.get(user=request.user)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Profile.DoesNotExist:
            return Response(
                {"error": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if not following
        if not current_profile.is_following(target_profile):
            return Response(
                {"error": "Not following this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Unfollow the user
        current_profile.unfollow(target_profile)

        serializer = FollowActionSerializer(
            {
                "message": "Successfully unfollowed user",
                "is_following": False,
                "followers_count": target_profile.get_followers_count(),
            },
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserFollowingListView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    serializer_class = ProfileFollowerAndFollowingListSerializer
    pagination_class = FollowCursorPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        user_id = self.kwargs.get("user_id", None)
        if user_id is None:
            msg = "user_id not found in URL kwargs."
            raise ValueError(msg)

        try:
            user = User.objects.get(id=user_id)
            profile = (
                user.profile if hasattr(user, "profile") and user.profile else None
            )

            if profile is None:
                return Profile.objects.none()
        except User.DoesNotExist:
            return Profile.objects.none()

        # Get all profiles that this user is following
        return Profile.objects.filter(
            followers__follower=profile,
        ).select_related("user")


class UserFollowersListView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    serializer_class = ProfileFollowerAndFollowingListSerializer
    pagination_class = FollowCursorPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        user_id = self.kwargs.get("user_id", None)
        if user_id is None:
            msg = "user_id not found in URL kwargs."
            raise ValueError(msg)

        try:
            user = User.objects.get(id=user_id)
            profile = (
                user.profile if hasattr(user, "profile") and user.profile else None
            )

            if profile is None:
                return Profile.objects.none()
        except User.DoesNotExist:
            return Profile.objects.none()

        # Get all profiles that follow this user
        return Profile.objects.filter(
            following__following=profile,
        ).select_related("user")
