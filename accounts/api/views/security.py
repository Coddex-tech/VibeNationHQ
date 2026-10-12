from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...authentications import (
    VibeNationSessionAuthentication,
)
from ...serializers.security import (
    ChangeEmailSerializer,
    VerifyEmailChangeSerializer,
)
from ...services.security import (
    EmailChangeError,
    confirm_email_change,
    request_email_change,
)


class ChangeEmailView(APIView):
    authentication_classes = [
        VibeNationSessionAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = ChangeEmailSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            request_email_change(
                user=request.user,
                current_password=serializer.validated_data[
                    "current_password"
                ],
                new_email=serializer.validated_data[
                    "new_email"
                ],
            )

        except EmailChangeError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": (
                    "A verification link has been sent "
                    "to your new email address."
                ),
            },
            status=status.HTTP_200_OK,
        )


class VerifyEmailChangeView(APIView):
    authentication_classes = []

    permission_classes = []

    def post(self, request):
        serializer = VerifyEmailChangeSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            user = confirm_email_change(
                raw_token=serializer.validated_data[
                    "token"
                ],
            )

        except EmailChangeError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": (
                    "Email address changed successfully."
                ),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                },
            },
            status=status.HTTP_200_OK,
        )