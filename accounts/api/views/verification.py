from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model

from ...authentications import (
    VibeNationSessionAuthentication,
)
from ...services.authentication import authenticate_web_user
from ...throttles import ResendVerificationThrottle

from ...serializers.verification import (
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    PhoneVerificationConfirmSerializer,
    PhoneVerificationRequestSerializer,
    PhoneChangeRequestSerializer,
    PhoneChangeConfirmSerializer,
)
from ...services.verification import (
    resend_email_verification,
    verify_email_token,
)
from ...services.phone import (
    PhoneServiceError,
    request_phone_change,
    request_phone_verification,
    verify_phone,
    verify_phone_change,
)


User = get_user_model()


class EmailVerificationView(APIView):
    """
    Verify a user's email address, activate the account,
    and authenticate the user with a new web session.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = EmailVerificationSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            user = verify_email_token(
                raw_token=serializer.validated_data["token"],
            )
        except ValueError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = Response(
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

        authenticate_web_user(
            request=request,
            response=response,
            user=user,
        )

        return response


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


class PhoneVerificationRequestView(APIView):
    """
    Request a verification code for adding a phone number.
    """

    authentication_classes = [
        VibeNationSessionAuthentication,
    ]
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = PhoneVerificationRequestSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            request_phone_verification(
                user=request.user,
                phone_number=serializer.validated_data[
                    "phone_number"
                ],
                country_code=serializer.validated_data[
                    "country_code"
                ],
            )
        except (PhoneServiceError, ValueError) as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": (
                    "Verification code sent successfully."
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class PhoneVerificationConfirmView(APIView):
    """
    Verify the code and add the phone number to the account.
    """

    authentication_classes = [
        VibeNationSessionAuthentication,
    ]
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = PhoneVerificationConfirmSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            phone = verify_phone(
                user=request.user,
                phone_number=serializer.validated_data[
                    "phone_number"
                ],
                code=serializer.validated_data["code"],
                country_code=serializer.validated_data[
                    "country_code"
                ],
            )
        except PhoneServiceError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
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
                "detail": (
                    "Phone number verified successfully."
                ),
                "phone_number": phone.phone_number,
                "verified": phone.is_verified,
            },
            status=status.HTTP_200_OK,
        )


class PhoneChangeRequestView(APIView):
    """
    Request a verification code for changing a phone number.
    """

    authentication_classes = [
        VibeNationSessionAuthentication,
    ]
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = PhoneChangeRequestSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            request_phone_change(
                user=request.user,
                current_password=serializer.validated_data[
                    "current_password"
                ],
                new_phone_number=serializer.validated_data[
                    "phone_number"
                ],
                country_code=serializer.validated_data[
                    "country_code"
                ],
            )
        except (PhoneServiceError, ValueError) as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": (
                    "Phone change verification code "
                    "sent successfully."
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class PhoneChangeConfirmView(APIView):
    """
    Verify the code and complete a phone number change.
    """

    authentication_classes = [
        VibeNationSessionAuthentication,
    ]
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = PhoneChangeConfirmSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            phone = verify_phone_change(
                user=request.user,
                new_phone_number=serializer.validated_data[
                    "phone_number"
                ],
                code=serializer.validated_data["code"],
                country_code=serializer.validated_data[
                    "country_code"
                ],
            )
        except PhoneServiceError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
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
                "detail": (
                    "Phone number changed successfully."
                ),
                "phone_number": phone.phone_number,
                "verified": phone.is_verified,
            },
            status=status.HTTP_200_OK,
        )