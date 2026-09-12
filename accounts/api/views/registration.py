from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ...serializers.registration import RegistrationSerializer
from ...services.registration import register_user


class RegistrationView(APIView):
    """
    Create a new VibeNationHQ account.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegistrationSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        user = register_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        return Response(
            {
                "message": (
                    "Account created successfully. "
                    "Please verify your email."
                ),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "is_active": user.is_active,
                },
            },
            status=status.HTTP_201_CREATED,
        )