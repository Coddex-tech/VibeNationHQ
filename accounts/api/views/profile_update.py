from django.db import IntegrityError, transaction

from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...authentications import VibeNationSessionAuthentication
from ...serializers.profile import ProfileUpdateSerializer
from ...serializers.public_profile import PublicProfileSerializer


class ProfileUpdateView(APIView):
    authentication_classes = [VibeNationSessionAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_user(self, request):
        user = request.user

        if (
            user.is_staff
            or user.is_superuser
            or not user.is_active
        ):
            raise PermissionDenied(
                "This account cannot update a public VibeNation profile."
            )

        if not user.onboarding_completed:
            raise PermissionDenied(
                "Complete your account setup before editing your profile."
            )

        return user

    def patch(self, request):
        user = self.get_user(request)

        serializer = ProfileUpdateSerializer(
            instance=user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                updated_user = serializer.save()

        except IntegrityError:
            raise ValidationError({
                "username": "This username is already taken."
            })

        response_serializer = PublicProfileSerializer(
            updated_user,
            context={"request": request},
        )

        return Response(
            {
                "message": "Your profile has been updated successfully.",
                "user": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
