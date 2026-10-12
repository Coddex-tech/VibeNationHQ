from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

from .sessions import UserSession
from ..models import PasswordResetToken

User = get_user_model()


@transaction.atomic
def change_password(
    *,
    user,
    new_password,
    current_session_id,
):
    user.set_password(new_password)

    user.save(
        update_fields=[
            "password",
            "updated_at",
        ],
    )

    (
        UserSession.objects
        .filter(
            user=user,
            revoked_at__isnull=True,
        )
        .exclude(
            id=current_session_id,
        )
        .update(
            revoked_at=timezone.now(),
        )
    )

    return user


PASSWORD_RESET_TOKEN_LIFETIME = timedelta(
    hours=1
)

@transaction.atomic
def create_password_reset_token(*, user):
    PasswordResetToken.objects.filter(
        user=user,
        used_at__isnull=True,
        expires_at__gt=timezone.now(),
    ).update(
        used_at=timezone.now(),
    )

    raw_token = PasswordResetToken.generate_token()

    token_hash = PasswordResetToken.hash_token(
        raw_token,
    )

    reset_token = PasswordResetToken.objects.create(
        user=user,
        token_hash=token_hash,
        expires_at=(
            timezone.now()
            + PASSWORD_RESET_TOKEN_LIFETIME
        ),
    )

    return reset_token, raw_token

def verify_password_reset_token(*, raw_token):
    token_hash = PasswordResetToken.hash_token(
        raw_token,
    )

    try:
        reset_token = (
            PasswordResetToken.objects
            .select_related("user")
            .get(
                token_hash=token_hash,
            )
        )
    except PasswordResetToken.DoesNotExist:
        raise ValueError(
            "Invalid or expired password reset token."
        )

    if reset_token.is_used:
        raise ValueError(
            "Invalid or expired password reset token."
        )

    if reset_token.is_expired:
        raise ValueError(
            "Invalid or expired password reset token."
        )

    if not reset_token.user.is_active:
        raise ValueError(
            "Invalid or expired password reset token."
        )

    return reset_token

@transaction.atomic
def consume_password_reset_token(*, raw_token):
    reset_token = verify_password_reset_token(
        raw_token=raw_token,
    )

    reset_token.used_at = timezone.now()

    reset_token.save(
        update_fields=[
            "used_at",
        ],
    )
    return reset_token


def send_password_reset_email(*, user, raw_token):
    reset_url = (
        f"{settings.VIBENATION_FRONTEND_URL}"
        f"/reset-password?token={raw_token}"
    )

    send_mail(
        subject="Reset your VibeNationHQ password",
        message=(
            "We received a request to reset your VibeNationHQ "
            "password.\n\n"
            "If you made this request, open the link below:\n\n"
            f"{reset_url}\n\n"
            "This password reset link expires in 1 hour.\n\n"
            "If you did not request a password reset, you can "
            "safely ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


@transaction.atomic
def request_password_reset(*, email):
    try:
        user = (
            User.objects
            .get(email__iexact=email)
        )
    except User.DoesNotExist:
        return None

    if not user.is_active:
        return None

    reset_token, raw_token = create_password_reset_token(
        user=user,
    )

    send_password_reset_email(
        user=user,
        raw_token=raw_token,
    )
    return reset_token


@transaction.atomic
def reset_password(
    *,
    raw_token,
    new_password,
):
    reset_token = consume_password_reset_token(
        raw_token=raw_token,
    )

    user = reset_token.user

    user.set_password(
        new_password,
    )

    user.save(
        update_fields=[
            "password",
            "updated_at",
        ],
    )

    (
        UserSession.objects
        .filter(
            user=user,
            revoked_at__isnull=True,
        )
        .update(
            revoked_at=timezone.now(),
        )
    )
    return user