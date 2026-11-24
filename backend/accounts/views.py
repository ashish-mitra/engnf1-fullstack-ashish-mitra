from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.tokens import AccessToken

from .serializers import (
    UserSerializer,
    RegistrationSerializer,
    LoginSerializer
)


class RegisterView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = RegistrationSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            {
                "user": UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(
            request,
            email=email,
            password=password
        )

        if user is None:
            return Response(
                {
                    "error": {
                        "code": "UNAUTHENTICATED",
                        "message": "Invalid email or password."
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = AccessToken.for_user(user)

        return Response(
            {
                "token": str(token),
                "user": UserSerializer(user).data
            },
            status=status.HTTP_200_OK
        )


class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response(
            {
                "user": UserSerializer(request.user).data
            },
            status=status.HTTP_200_OK
        )