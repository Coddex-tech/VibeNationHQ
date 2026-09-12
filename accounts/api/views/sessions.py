from uuid import UUID
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from django.utils import timezone

from ...authentications import (
    AUTH_COOKIE_NAME,
    VibeNationSessionAuthentication,
)

from ...services.sessions import (
    InvalidSessionError,
    logout_web_user,
    revoke_session_by_id,
)

from ...serializers.security import (
    UserSessionSerializer,
)

from ...models import UserSession


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        raw_secret = request.COOKIES.get(
            AUTH_COOKIE_NAME
        )

        if raw_secret:
            try:
                logout_web_user(
                    raw_secret=raw_secret,
                )
            except InvalidSessionError:
                pass

        response = Response(
            {
                "message": "Logout successful.",
            },
            status=status.HTTP_200_OK,
        )

        response.delete_cookie(
            AUTH_COOKIE_NAME,
            samesite="Lax",
        )

        return response


class SessionListView(APIView):
    authentication_classes = [
        VibeNationSessionAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        sessions = (
            UserSession.objects
            .filter(
                user=request.user,
                revoked_at__isnull=True,
                expires_at__gt=timezone.now(),
            )
            .order_by("-last_seen_at")
        )

        serializer = UserSessionSerializer(
            sessions,
            many=True,
            context={
                "current_session": request.auth,
            },
        )

        return Response(
            {
                "sessions": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class SessionRevokeView(APIView):
    authentication_classes = [
        VibeNationSessionAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    def delete(self, request, session_id):
        try:
            UUID(str(session_id))
        except ValueError:
            return Response(
                {
                    "detail": "Session not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            revoke_session_by_id(
                user=request.user,
                session_id=session_id,
            )

        except InvalidSessionError:
            return Response(
                {
                    "detail": "Session not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "message": "Session revoked.",
            },
            status=status.HTTP_200_OK,
        )