from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...authentications import (
    VibeNationSessionAuthentication,
)
from ...models import UserPhone


class CurrentUserView(APIView):
    authentication_classes = [
        VibeNationSessionAuthentication,
    ]
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        user = request.user

        phone = (
            UserPhone.objects
            .filter(
                user=user,
            )
            .first()
        )

        phone_data = None

        if phone is not None:
            phone_data = {
                "phone_number": phone.phone_number,
                "is_verified": phone.is_verified,
                "verified_at": phone.verified_at,
            }

        return Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "is_active": user.is_active,
                    "phone": phone_data,
                },
            },
            status=status.HTTP_200_OK,
        )