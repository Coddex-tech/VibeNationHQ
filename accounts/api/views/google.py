from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ...serializers.google import GoogleLoginSerializer
from ...services.authentication import authenticate_web_user
from ...services.google import (
    GoogleAccountError,
    InvalidGoogleTokenError,
    login_with_google,
)


class GoogleLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = GoogleLoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            user = login_with_google(
            token=serializer.validated_data[
                "credential"
            ],
        )

        except InvalidGoogleTokenError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        except GoogleAccountError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_409_CONFLICT,
            )

        response = Response(
            {
                "message": "Google login successful.",
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