from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...authentications import VibeNationSessionAuthentication
from ...serializers.password import ChangePasswordSerializer
from ...services.password import change_password


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