
from django.contrib.auth import get_user_model

from rest_framework import serializers

from accounts.validators import (
    validate_username_format,
    validate_username_availability,
)


User = get_user_model()


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an authenticated user's
    public profile information.
    """

    username = serializers.CharField(
        min_length=3,
        max_length=30,
        trim_whitespace=True,
    )

    display_name = serializers.CharField(
        max_length=100,
        allow_blank=False,
        trim_whitespace=True,
    )

    bio = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )

    profile_image = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "display_name",
            "bio",
            "profile_image",
        ]

    def validate_username(self, value):
        validate_username_format(value)

        validate_username_availability(
            value,
            exclude_user=self.instance,
        )

        return value

    def validate_display_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Display name cannot be empty."
            )

        return value
