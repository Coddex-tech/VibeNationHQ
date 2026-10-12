from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...authentications import VibeNationSessionAuthentication
from ...serializers.password import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)
from ...services.password import (
    change_password,
    request_password_reset,
    reset_password,
)
from ...throttles import PasswordResetRequestThrottle


class ChangePasswordView(APIView):
    authentication_classes = [
        VibeNationSessionAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        change_password(
            user=request.user,
            new_password=serializer.validated_data[
                "new_password"
            ],
            current_session_id=request.auth.id,
        )

        return Response(
            {
                "message": (
                    "Password changed successfully."
                )
            },
            status=status.HTTP_200_OK,
        )


class ForgotPasswordView(APIView):
    authentication_classes = []
    permission_classes = [
        AllowAny,
    ]
    throttle_classes = [
        PasswordResetRequestThrottle,
    ]

    def post(self, request):
        serializer = ForgotPasswordSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        request_password_reset(
            email=serializer.validated_data["email"],
        )

        return Response(
            {
                "message": (
                    "If an account exists for this email, "
                    "a password reset link has been sent."
                )
            },
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = [
        AllowAny,
    ]

    def post(self, request):
        serializer = ResetPasswordSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        reset_password(
            raw_token=serializer.validated_data[
                "token"
            ],
            new_password=serializer.validated_data[
                "new_password"
            ],
        )

        return Response(
            {
                "message": (
                    "Password reset successfully."
                )
            },
            status=status.HTTP_200_OK,
        )