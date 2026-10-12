import hashlib
import secrets
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from ..models import UserSession


SESSION_SECRET_BYTES = 32
SESSION_LIFETIME = timedelta(days=30)
SESSION_LAST_SEEN_UPDATE_INTERVAL = timedelta(
    minutes=5
)


class InvalidSessionError(Exception):
    """
    Raised when a session secret is invalid,
    expired, or revoked.
    """


def _hash_secret(secret):
    return hashlib.sha256(
        secret.encode("utf-8")
    ).hexdigest()


@transaction.atomic
def create_session(
    *,
    user,
    device_name="",
    user_agent="",
    ip_address=None,
):
    raw_secret = secrets.token_urlsafe(
        SESSION_SECRET_BYTES
    )

    session = UserSession.objects.create(
        user=user,
        session_key_hash=_hash_secret(raw_secret),
        device_name=device_name,
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=(
            timezone.now()
            + SESSION_LIFETIME
        ),
    )

    return session, raw_secret


def get_valid_session(*, raw_secret):
    session_hash = _hash_secret(raw_secret)

    try:
        session = (
            UserSession.objects
            .select_related("user")
            .get(
                session_key_hash=session_hash,
            )
        )
    except UserSession.DoesNotExist:
        raise InvalidSessionError(
            "Invalid session."
        )

    now = timezone.now()

    if session.revoked_at is not None:
        raise InvalidSessionError(
            "Invalid session."
        )

    if now >= session.expires_at:
        raise InvalidSessionError(
            "Invalid session."
        )

    if not session.user.is_active:
        raise InvalidSessionError(
            "Invalid session."
        )

    # Avoid writing to the database on every
    # authenticated request. Refresh last_seen_at
    # at most once every five minutes.
    if (
        session.last_seen_at is None
        or (
            now - session.last_seen_at
            >= SESSION_LAST_SEEN_UPDATE_INTERVAL
        )
    ):
        UserSession.objects.filter(
            id=session.id,
        ).update(
            last_seen_at=now,
        )

        session.last_seen_at = now

    return session


@transaction.atomic
def revoke_session(*, raw_secret):
    session_hash = _hash_secret(raw_secret)

    try:
        session = UserSession.objects.get(
            session_key_hash=session_hash,
        )
    except UserSession.DoesNotExist:
        raise InvalidSessionError(
            "Invalid session."
        )

    if session.revoked_at is not None:
        return session

    session.revoked_at = timezone.now()

    session.save(
        update_fields=["revoked_at"],
    )

    return session


def logout_web_user(*, raw_secret):
    """
    Revoke the authenticated web session.
    """

    return revoke_session(
        raw_secret=raw_secret,
    )


@transaction.atomic
def revoke_session_by_id(*, user, session_id):
    try:
        session = UserSession.objects.get(
            id=session_id,
            user=user,
        )
    except UserSession.DoesNotExist:
        raise InvalidSessionError(
            "Session not found."
        )

    if session.revoked_at is not None:
        return session

    session.revoked_at = timezone.now()

    session.save(
        update_fields=["revoked_at"],
    )

    return session


@transaction.atomic
def revoke_all_other_sessions(
    *,
    user,
    current_session_id,
):
    revoked_at = timezone.now()

    updated = (
        UserSession.objects
        .filter(
            user=user,
            revoked_at__isnull=True,
        )
        .exclude(
            id=current_session_id,
        )
        .update(
            revoked_at=revoked_at,
        )
    )

    return updated