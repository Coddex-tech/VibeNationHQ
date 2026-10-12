from rest_framework import serializers

from ..services.phone import PhoneServiceError
from ..services.phone import normalize_phone_number


class EmailVerificationSerializer(serializers.Serializer):
    """
    Validate an email verification token.
    """

    token = serializers.CharField(
        write_only=True,
        trim_whitespace=True,
    )

    def validate_token(self, value):
        """
        Ensure a verification token was provided.
        """

        if not value:
            raise serializers.ValidationError(
                "Verification token is required."
            )

        return value
    

class ResendVerificationSerializer(serializers.Serializer):
    """
    Validate a request to resend an email verification message.
    """

    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip().lower()


class PhoneVerificationRequestSerializer(
    serializers.Serializer,
):
    phone_number = serializers.CharField(
        max_length=20,
    )

    country_code = serializers.CharField(
        max_length=2,
    )

    def validate(self, attrs):
        try:
            attrs["phone_number"] = normalize_phone_number(
                attrs["phone_number"],
                attrs["country_code"],
            )
        except PhoneServiceError as exc:
            raise serializers.ValidationError(
                {
                    "phone_number": str(exc),
                }
            )

        attrs["country_code"] = (
            attrs["country_code"].strip().upper()
        )

        return attrs


class PhoneVerificationConfirmSerializer(
    serializers.Serializer,
):
    phone_number = serializers.CharField(
        max_length=20,
    )

    country_code = serializers.CharField(
        max_length=2,
    )

    code = serializers.CharField(
        min_length=6,
        max_length=6,
    )

    def validate(self, attrs):
        try:
            attrs["phone_number"] = normalize_phone_number(
                attrs["phone_number"],
                attrs["country_code"],
            )
        except PhoneServiceError as exc:
            raise serializers.ValidationError(
                {
                    "phone_number": str(exc),
                }
            )

        attrs["country_code"] = (
            attrs["country_code"].strip().upper()
        )

        return attrs

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                "Verification code must contain only digits."
            )

        return value


class PhoneChangeRequestSerializer(
    serializers.Serializer,
):
    current_password = serializers.CharField(
        write_only=True,
    )

    phone_number = serializers.CharField(
        max_length=20,
    )

    country_code = serializers.CharField(
        max_length=2,
    )

    def validate(self, attrs):
        try:
            attrs["phone_number"] = normalize_phone_number(
                attrs["phone_number"],
                attrs["country_code"],
            )
        except PhoneServiceError as exc:
            raise serializers.ValidationError(
                {
                    "phone_number": str(exc),
                }
            )

        attrs["country_code"] = (
            attrs["country_code"].strip().upper()
        )

        return attrs


class PhoneChangeConfirmSerializer(
    serializers.Serializer,
):
    phone_number = serializers.CharField(
        max_length=20,
    )

    country_code = serializers.CharField(
        max_length=2,
    )

    code = serializers.CharField(
        min_length=6,
        max_length=6,
    )

    def validate(self, attrs):
        try:
            attrs["phone_number"] = normalize_phone_number(
                attrs["phone_number"],
                attrs["country_code"],
            )
        except PhoneServiceError as exc:
            raise serializers.ValidationError(
                {
                    "phone_number": str(exc),
                }
            )

        attrs["country_code"] = (
            attrs["country_code"].strip().upper()
        )

        return attrs

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                "Verification code must contain only digits."
            )

        return value