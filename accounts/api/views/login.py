from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ...serializers.login import LoginSerializer
from ...services.authentication import authenticate_web_user
from ...services.login import (
    InactiveAccountError,
    InvalidLoginError,
    login_user,
)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            user = login_user(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )

        except InvalidLoginError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        except InactiveAccountError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        response = Response(
            {
                "message": "Login successful.",
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