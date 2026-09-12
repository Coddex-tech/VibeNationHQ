from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import get_user_model

from ...throttles import ResendVerificationThrottle

from ...serializers.verification import (
    EmailVerificationSerializer,
    ResendVerificationSerializer,
)
from ...services.verification import (
    resend_email_verification,
    verify_email_token,
)


User = get_user_model()

class EmailVerificationView(APIView):
    """
    Verify a user's email address and activate the account.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = EmailVerificationSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            user = verify_email_token(
                raw_token=serializer.validated_data["token"]
            )
        except ValueError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "Email verified successfully.",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "is_active": user.is_active,
                },
            },
            status=status.HTTP_200_OK,
        )


class ResendVerificationView(APIView):
    """
    Request another email verification message.
    """

    authentication_classes = []
    permission_classes = []
    throttle_classes = [ResendVerificationThrottle]

    def post(self, request):
        serializer = ResendVerificationSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True
        )

        email = serializer.validated_data["email"]

        user = (
            User.objects.filter(
                email__iexact=email,
                is_active=False,
            )
            .first()
        )

        if user is not None:
            try:
                resend_email_verification(
                    user=user
                )
            except ValueError:
                pass

        return Response(
            {
                "message": (
                    "If an account with that email address "
                    "needs verification, a verification email "
                    "will be sent."
                )
            },
            status=status.HTTP_200_OK,
        )