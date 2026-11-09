
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...authentications import VibeNationSessionAuthentication
from accounts.validators import (
    validate_username_format,
    is_username_available,
)


User = get_user_model()


def get_onboarding_user(request):
    """
    Return the authenticated ordinary user eligible for onboarding.

    Email verification is represented by is_active=True.
    Staff accounts must not participate in public onboarding.
    """

    user = request.user

    if (
        not user.is_active
        or user.is_staff
        or user.is_superuser
    ):
        return None

    return user


class OnboardingAPIView(APIView):
    """
    Shared authentication and eligibility rules for onboarding.
    """

    authentication_classes = [
        VibeNationSessionAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    def get_eligible_user(self, request):
        user = get_onboarding_user(request)

        if user is None:
            return None, Response(
                {
                    "message": (
                        "This account cannot access public "
                        "account onboarding."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if user.onboarding_completed:
            return None, Response(
                {
                    "message": "Onboarding has already been completed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return user, None


class DisplayNameOnboardingView(OnboardingAPIView):
    """
    Save the user's public display name.
    """

    def post(self, request):
        user, error_response = self.get_eligible_user(request)

        if error_response:
            return error_response

        display_name = request.data.get("display_name")

        if not isinstance(display_name, str):
            return Response(
                {
                    "display_name": [
                        "A valid display name is required."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        display_name = display_name.strip()

        if not display_name:
            return Response(
                {
                    "display_name": [
                        "Display name cannot be empty."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(display_name) > 100:
            return Response(
                {
                    "display_name": [
                        "Display name cannot exceed 100 characters."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            locked_user = User.objects.select_for_update().get(
                pk=user.pk,
            )

            if (
                not locked_user.is_active
                or locked_user.is_staff
                or locked_user.is_superuser
            ):
                return Response(
                    {
                        "message": (
                            "This account cannot access public "
                            "account onboarding."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            if locked_user.onboarding_completed:
                return Response(
                    {
                        "message": (
                            "Onboarding has already been completed."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            locked_user.display_name = display_name

            locked_user.save(
                update_fields=[
                    "display_name",
                    "updated_at",
                ]
            )

        return Response(
            {
                "message": "Display name saved successfully.",
                "display_name": display_name,
            },
            status=status.HTTP_200_OK,
        )


class UsernameAvailabilityView(OnboardingAPIView):
    """
    Check whether a username is available.

    This endpoint does not save the username.
    """

    def get(self, request):
        user, error_response = self.get_eligible_user(request)

        if error_response:
            return error_response

        username = request.query_params.get(
            "username",
            "",
        ).strip()

        try:
            validate_username_format(username)

        except ValidationError as exc:
            return Response(
                {
                    "username": username,
                    "available": False,
                    "message": exc.detail[0],
                },
                status=status.HTTP_200_OK,
            )

        available = is_username_available(
            username,
            exclude_user=user,
        )

        return Response(
            {
                "username": username,
                "available": available,
                "message": (
                    "Username is available."
                    if available
                    else "This username is already taken."
                ),
            },
            status=status.HTTP_200_OK,
        )


class UsernameOnboardingView(OnboardingAPIView):
    """
    Save the user's username and complete onboarding.
    """

    def post(self, request):
        user, error_response = self.get_eligible_user(request)

        if error_response:
            return error_response

        username = request.data.get("username")

        if not isinstance(username, str):
            return Response(
                {
                    "username": [
                        "A valid username is required."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        username = username.strip()

        try:
            validate_username_format(username)

        except ValidationError as exc:
            return Response(
                {
                    "username": exc.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                locked_user = User.objects.select_for_update().get(
                    pk=user.pk,
                )

                if (
                    not locked_user.is_active
                    or locked_user.is_staff
                    or locked_user.is_superuser
                ):
                    return Response(
                        {
                            "message": (
                                "This account cannot access public "
                                "account onboarding."
                            )
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

                if locked_user.onboarding_completed:
                    return Response(
                        {
                            "message": (
                                "Onboarding has already been completed."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if not (locked_user.display_name or "").strip():
                    return Response(
                        {
                            "message": (
                                "Please save your display name before "
                                "choosing a username."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if not is_username_available(
                    username,
                    exclude_user=locked_user,
                ):
                    return Response(
                        {
                            "username": [
                                "This username is already taken."
                            ]
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                locked_user.username = username
                locked_user.onboarding_completed = True

                locked_user.save(
                    update_fields=[
                        "username",
                        "onboarding_completed",
                        "updated_at",
                    ]
                )

        except IntegrityError:
            return Response(
                {
                    "username": [
                        "This username is already taken."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "Onboarding completed successfully.",
                "username": locked_user.username,
                "display_name": locked_user.display_name,
                "onboarding_completed": locked_user.onboarding_completed,
            },
            status=status.HTTP_200_OK,
        )
