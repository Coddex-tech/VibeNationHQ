from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction

from google.auth.transport import requests
from google.oauth2 import id_token

from ..models import UserIdentity


User = get_user_model()


class InvalidGoogleTokenError(Exception):
    """
    Raised when a Google ID token is invalid.
    """


def verify_google_id_token(*, token):
    """
    Verify a Google ID token issued for VibeNationHQ.

    Returns the verified Google token claims.
    """

    if not token:
        raise InvalidGoogleTokenError(
            "Google credential is required."
        )

    if not settings.GOOGLE_CLIENT_ID:
        raise InvalidGoogleTokenError(
            "Google authentication is not configured."
        )

    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        raise InvalidGoogleTokenError(
            "Invalid Google credential."
        )

    if idinfo.get("iss") not in (
        "accounts.google.com",
        "https://accounts.google.com",
    ):
        raise InvalidGoogleTokenError(
            "Invalid Google issuer."
        )

    if not idinfo.get("sub"):
        raise InvalidGoogleTokenError(
            "Google account identifier is missing."
        )

    if not idinfo.get("email"):
        raise InvalidGoogleTokenError(
            "Google account email is missing."
        )

    if idinfo.get("email_verified") is not True:
        raise InvalidGoogleTokenError(
            "Google account email is not verified."
        )
    return idinfo


class GoogleAccountError(Exception):
    """
    Raised when a Google account cannot be resolved safely.
    """


def _get_google_email(*, claims):
    email = claims.get("email")

    if not email:
        raise GoogleAccountError(
            "Google account email is missing."
        )

    return email


@transaction.atomic
def resolve_google_user(*, claims):
    """
    Resolve a VibeNationHQ user from verified Google claims.

    Existing Google identity:
        Return the linked VibeNationHQ user.

    New Google identity:
        Create a new VibeNationHQ user when no existing
        VibeNationHQ account uses the verified email.

    Existing VibeNationHQ accounts are not automatically
    linked to a new Google identity.
    """

    provider_subject = claims.get("sub")

    if not provider_subject:
        raise GoogleAccountError(
            "Google account identifier is missing."
        )

    email = _get_google_email(
        claims=claims,
    )

    try:
        identity = (
            UserIdentity.objects
            .select_related("user")
            .get(
                provider=UserIdentity.Provider.GOOGLE,
                provider_subject=provider_subject,
            )
        )
    except UserIdentity.DoesNotExist:
        identity = None

    if identity is not None:
        user = identity.user

        if not user.is_active:
            raise GoogleAccountError(
                "This VibeNation account is inactive."
            )

        return user

    existing_user = (
        User.objects
        .filter(
            email__iexact=email,
        )
        .first()
    )

    if existing_user is not None:
        raise GoogleAccountError(
            "A VibeNation account already exists with this email. "
            "Sign in with your existing account to link Google."
        )

    user = User.objects.create_user(
        email=email,
        password=None,
        is_active=True,
    )

    UserIdentity.objects.create(
        user=user,
        provider=UserIdentity.Provider.GOOGLE,
        provider_subject=provider_subject,
        email=email,
    )
    return user


def login_with_google(
    *,
    token,
):
    """
    Authenticate a user with a Google ID token.

    Returns the resolved VibeNationHQ user.
    Session creation is handled by the web
    authentication layer.
    """

    claims = verify_google_id_token(
        token=token,
    )

    return resolve_google_user(
        claims=claims,
    )