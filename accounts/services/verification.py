import hashlib
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import constant_time_compare

from ..models import EmailVerificationToken


VERIFICATION_TOKEN_LIFETIME = timedelta(hours=24)

VERIFICATION_RESEND_COOLDOWN = timedelta(seconds=60)


def _hash_token(token):
    """
    Hash a raw verification token.
    """

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


@transaction.atomic
def create_email_verification_token(user):
    """
    Create or replace the email verification token for a user.

    Returns:
        tuple[EmailVerificationToken, str]:
            The database token object and the raw token.
    """

    raw_token = EmailVerificationToken.generate_token()

    token_hash = _hash_token(raw_token)

    expires_at = (
        timezone.now()
        + VERIFICATION_TOKEN_LIFETIME
    )

    verification_token, _ = (
        EmailVerificationToken.objects.update_or_create(
            user=user,
            defaults={
                "token_hash": token_hash,
                "expires_at": expires_at,
                "used_at": None,
            },
        )
    )

    return verification_token, raw_token


@transaction.atomic
def verify_email_token(*, raw_token):
    """
    Verify an email verification token.

    Returns:
        User

    Raises:
        ValueError: If the token is invalid, expired, or already used.
    """

    token_hash = _hash_token(raw_token)

    try:
        verification_token = (
            EmailVerificationToken.objects.select_related(
                "user"
            ).get(
                token_hash=token_hash,
            )
        )
    except EmailVerificationToken.DoesNotExist:
        raise ValueError(
            "Invalid or expired verification token."
        )

    if verification_token.is_used:
        raise ValueError(
            "This verification token has already been used."
        )

    if verification_token.is_expired:
        raise ValueError(
            "Invalid or expired verification token."
        )

    user = verification_token.user

    user.is_active = True
    user.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    verification_token.used_at = timezone.now()
    verification_token.save(
        update_fields=["used_at"]
    )

    return user

def send_verification_email(*, user, raw_token):
    """
    Send the email verification message to a user.

    The raw token is used only to construct the verification URL.
    It is never stored in the database.
    """

    verification_url = (
        f"{settings.VIBENATION_FRONTEND_URL}"
        f"/verify-email?token={raw_token}"
    )

    send_mail(
        subject="Verify your VibeNationHQ account",
        message=(
            "Welcome to VibeNationHQ!\n\n"
            "Please verify your email address by opening the link below:\n\n"
            f"{verification_url}\n\n"
            "This verification link expires in 24 hours.\n\n"
            "If you did not create this account, you can safely "
            "ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def resend_email_verification(*, user):
    """
    Generate a new email verification token and send it.

    The previous token is replaced only when the resend
    is permitted by the cooldown.
    """

    if user.is_active:
        raise ValueError(
            "This account has already been verified."
        )

    existing_token = (
        EmailVerificationToken.objects.filter(
            user=user
        ).first()
    )

    if existing_token:
        cooldown_until = (
            existing_token.created_at
            + VERIFICATION_RESEND_COOLDOWN
        )

        if timezone.now() < cooldown_until:
            raise ValueError(
                "Please wait before requesting another "
                "verification email."
            )

    verification_token, raw_token = (
        create_email_verification_token(user)
    )

    send_verification_email(
        user=user,
        raw_token=raw_token,
    )

    return verification_token