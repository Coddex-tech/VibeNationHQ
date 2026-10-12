from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers

from ..services.password import verify_password_reset_token

User = get_user_model()


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )

    new_password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        user = self.context["request"].user

        current_password = attrs["current_password"]
        new_password = attrs["new_password"]
        new_password_confirm = attrs["new_password_confirm"]

        if not user.check_password(current_password):
            raise serializers.ValidationError(
                {
                    "current_password": (
                        "Your current password is incorrect."
                    )
                }
            )

        if new_password != new_password_confirm:
            raise serializers.ValidationError(
                {
                    "new_password_confirm": (
                        "Passwords do not match."
                    )
                }
            )

        if current_password == new_password:
            raise serializers.ValidationError(
                {
                    "new_password": (
                        "Your new password must be different "
                        "from your current password."
                    )
                }
            )

        try:
            validate_password(
                new_password,
                user=user,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                {
                    "new_password": list(exc.messages)
                }
            )
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip().lower()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )

    new_password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        token = attrs["token"]
        new_password = attrs["new_password"]
        new_password_confirm = attrs[
            "new_password_confirm"
        ]

        try:
            reset_token = verify_password_reset_token(
                raw_token=token,
            )
        except ValueError as exc:
            raise serializers.ValidationError(
                {
                    "token": str(exc),
                }
            )

        if new_password != new_password_confirm:
            raise serializers.ValidationError(
                {
                    "new_password_confirm": (
                        "Passwords do not match."
                    )
                }
            )

        user = reset_token.user

        try:
            validate_password(
                new_password,
                user=user,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                {
                    "new_password": list(
                        exc.messages
                    )
                }
            )

        attrs["reset_token"] = reset_token

        return attrs