from django.db import transaction
from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from core.users.models import User

from .models import Profile
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

            Profile.objects.create(
                user=user,
                full_name=serializer.validated_data.get("name"),
                email=serializer.validated_data.get("email"),
                phone_number=serializer.validated_data.get("phone_number"),
                id_card_file=serializer.validated_data.get("id_card_file"),
            )

        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED,
        )
