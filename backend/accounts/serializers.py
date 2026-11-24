from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):

    createdAt = serializers.DateTimeField(
        source="created_at",
        read_only=True
    )

    class Meta:
        model = User

        fields = [
            "id",
            "name",
            "email",
            "role",
            "createdAt"
        ]

        read_only_fields = [
            "id",
            "role",
            "createdAt"
        ]

import re


class RegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=64
    )

    class Meta:
        model = User

        fields = [
            "name",
            "email",
            "password"
        ]

    def validate_name(self, value):

        value = value.strip()

        if len(value) < 2 or len(value) > 50:
            raise serializers.ValidationError(
                "Name must contain 2 to 50 characters."
            )

        return value

    def validate_email(self, value):

        value = value.strip().lower()

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def validate_password(self, value):

        if not re.search(r"[A-Za-z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one letter."
            )

        if not re.search(r"\d", value):
            raise serializers.ValidationError(
                "Password must contain at least one digit."
            )

        return value

    def create(self, validated_data):

        return User.objects.create_user(
            **validated_data
        )

class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )

    def validate_email(self, value):
        return value.strip().lower()