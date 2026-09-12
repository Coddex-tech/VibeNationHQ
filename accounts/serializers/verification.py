from rest_framework import serializers


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