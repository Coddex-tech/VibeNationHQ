import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from ..models import (
    EmailChangeToken,
    PhoneOTP,
)


User = get_user_model()


EMAIL_CHANGE_TOKEN_LIFETIME = timedelta(
    hours=1
)


class EmailChangeError(Exception):
    pass


@transaction.atomic
def create_email_change_token(
    *,
    user,
    new_email,
):
    new_email = User.objects.normalize_email(
        new_email
    )

    if User.objects.filter(
        email__iexact=new_email
    ).exclude(
        pk=user.pk
    ).exists():
        raise EmailChangeError(
            "An account with this email already exists."
        )

    # Invalidate previous active email-change tokens.
    EmailChangeToken.objects.filter(
        user=user,
        used_at__isnull=True,
        expires_at__gt=timezone.now(),
    ).update(
        used_at=timezone.now(),
    )

    raw_token = EmailChangeToken.generate_token()

    token_hash = EmailChangeToken.hash_token(
        raw_token
    )

    token = EmailChangeToken.objects.create(
        user=user,
        new_email=new_email,
        token_hash=token_hash,
        expires_at=(
            timezone.now()
            + EMAIL_CHANGE_TOKEN_LIFETIME
        ),
    )

    return token, raw_token


def send_email_change_verification(
    *,
    user,
    raw_token,
    new_email,
):
    verification_url = (
        f"{settings.VIBENATION_FRONTEND_URL}"
        f"/verify-email-change?token={raw_token}"
    )

    send_mail(
        subject="Verify your new VibeNationHQ email",
        message=(
            "You requested to change the email address "
            "on your VibeNationHQ account.\n\n"
            "Your new email address is:\n"
            f"{new_email}\n\n"
            "Verify it by opening the link below:\n\n"
            f"{verification_url}\n\n"
            "This verification link expires in 1 hour.\n\n"
            "If you did not request this change, "
            "please secure your account immediately."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[new_email],
        fail_silently=False,
    )


@transaction.atomic
def request_email_change(
    *,
    user,
    current_password,
    new_email,
):
    if not user.check_password(
        current_password
    ):
        raise EmailChangeError(
            "Your current password is incorrect."
        )

    new_email = User.objects.normalize_email(
        new_email
    )

    if new_email.lower() == user.email.lower():
        raise EmailChangeError(
            "Your new email must be different "
            "from your current email."
        )

    token, raw_token = create_email_change_token(
        user=user,
        new_email=new_email,
    )

    send_email_change_verification(
        user=user,
        raw_token=raw_token,
        new_email=new_email,
    )

    return token

def verify_email_change_token(
    *,
    raw_token,
):
    token_hash = EmailChangeToken.hash_token(
        raw_token
    )

    try:
        token = (
            EmailChangeToken.objects
            .select_related("user")
            .get(
                token_hash=token_hash,
            )
        )
    except EmailChangeToken.DoesNotExist:
        raise EmailChangeError(
            "Invalid or expired email change token."
        )

    if token.is_used:
        raise EmailChangeError(
            "Invalid or expired email change token."
        )

    if token.is_expired:
        raise EmailChangeError(
            "Invalid or expired email change token."
        )

    if not token.user.is_active:
        raise EmailChangeError(
            "Invalid or expired email change token."
        )

    return token

@transaction.atomic
def confirm_email_change(
    *,
    raw_token,
):
    token = verify_email_change_token(
        raw_token=raw_token,
    )

    user = token.user

    new_email = token.new_email

    # Protect against the email becoming occupied
    # after the token was created.
    if User.objects.filter(
        email__iexact=new_email
    ).exclude(
        pk=user.pk
    ).exists():
        raise EmailChangeError(
            "This email address is no longer available."
        )

    user.email = new_email

    user.save(
        update_fields=[
            "email",
            "updated_at",
        ],
    )

    token.used_at = timezone.now()

    token.save(
        update_fields=[
            "used_at",
        ],
    )
    return user

# ===================================
# PHONE NUMBER OTP IMPLEMENT
# ===================================
PHONE_OTP_LENGTH = 6

PHONE_OTP_LIFETIME = timedelta(
    minutes=10
)

PHONE_OTP_RESEND_COOLDOWN = timedelta(
    seconds=60
)

PHONE_OTP_MAX_ATTEMPTS = 5

def generate_phone_otp_code():
    return "".join(
        str(secrets.randbelow(10))
        for _ in range(PHONE_OTP_LENGTH)
    )

@transaction.atomic
def create_phone_otp(
    *,
    user,
    phone_number,
    purpose,
):
    now = timezone.now()

    existing_otp = (
        PhoneOTP.objects
        .filter(
            user=user,
            purpose=purpose,
            used_at__isnull=True,
        )
        .order_by("-created_at")
        .first()
    )

    if existing_otp:
        cooldown_until = (
            existing_otp.created_at
            + PHONE_OTP_RESEND_COOLDOWN
        )

        if now < cooldown_until:
            raise ValueError(
                "Please wait before requesting "
                "another verification code."
            )

        existing_otp.used_at = now

        existing_otp.save(
            update_fields=[
                "used_at",
            ],
        )

    raw_code = generate_phone_otp_code()

    otp = PhoneOTP.objects.create(
        user=user,
        phone_number=phone_number,
        purpose=purpose,
        code_hash=PhoneOTP.hash_code(
            raw_code,
        ),
        expires_at=(
            now
            + PHONE_OTP_LIFETIME
        ),
        max_attempts=PHONE_OTP_MAX_ATTEMPTS,
    )
    return otp, raw_code


def verify_phone_otp(
    *,
    user,
    phone_number,
    purpose,
    code,
):
    with transaction.atomic():
        otp = (
            PhoneOTP.objects
            .select_for_update()
            .filter(
                user=user,
                phone_number=phone_number,
                purpose=purpose,
                used_at__isnull=True,
            )
            .order_by("-created_at")
            .first()
        )

        if otp is None:
            raise ValueError(
                "Invalid or expired verification code."
            )

        if otp.is_expired:
            raise ValueError(
                "Invalid or expired verification code."
            )

        if otp.attempts_exhausted:
            raise ValueError(
                "Too many verification attempts."
            )

        expected_hash = PhoneOTP.hash_code(code)

        if not secrets.compare_digest(
            otp.code_hash,
            expected_hash,
        ):
            otp.attempts += 1

            otp.save(
                update_fields=["attempts"],
            )

            error = ValueError(
                "Invalid verification code."
            )

        else:
            otp.used_at = timezone.now()

            otp.save(
                update_fields=["used_at"],
            )

            return otp

    raise error