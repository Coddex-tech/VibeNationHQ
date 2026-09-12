from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .services.sessions import (
    InvalidSessionError,
    get_valid_session,
)


AUTH_COOKIE_NAME = "vibenation_session"


class VibeNationSessionAuthentication(
    BaseAuthentication
):
    """
    Authenticate API requests using the
    VibeNationHQ web session cookie.
    """

    def authenticate(self, request):
        raw_secret = request.COOKIES.get(
            AUTH_COOKIE_NAME
        )

        if not raw_secret:
            return None

        try:
            session = get_valid_session(
                raw_secret=raw_secret
            )

        except InvalidSessionError:
            raise AuthenticationFailed(
                "Invalid or expired session."
            )

        return (
            session.user,
            session,
        )

    def authenticate_header(self, request):
        return "Session"