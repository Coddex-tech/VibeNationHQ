from django.conf import settings
from django.http import HttpRequest, HttpResponse

from .sessions import (
    create_session,
    SESSION_LIFETIME,
)


AUTH_COOKIE_NAME = "vibenation_session"


def authenticate_web_user(
    *,
    request: HttpRequest,
    response: HttpResponse,
    user,
):
    """
    Create a VibeNation web session and attach the
    session secret to the response as a secure cookie.
    """

    session, raw_secret = create_session(
        user=user,
        device_name="Web browser",
        user_agent=request.META.get(
            "HTTP_USER_AGENT",
            "",
        ),
        ip_address=request.META.get(
            "REMOTE_ADDR",
        ),
    )

    response.set_cookie(
        AUTH_COOKIE_NAME,
        raw_secret,
        max_age=int(
                SESSION_LIFETIME.total_seconds()
        ),
        httponly=True,
        secure=getattr(
            settings,
            "SESSION_COOKIE_SECURE",
            False,
        ),
        samesite="Lax",
    )

    return session