import phonenumbers
from phonenumbers import (
    NumberParseException,
    PhoneNumberFormat,
)

from django.db import transaction
from django.utils import timezone

from ..models import PhoneOTP, UserPhone
from .security import create_phone_otp, verify_phone_otp
from .sms import send_sms


class PhoneServiceError(Exception):
    """
    Raised when a phone-related operation fails.
    """

    pass


def normalize_phone_number(
    phone_number,
    country_code=None,
):
    """
    Normalize a phone number into E.164 format.

    Supports:
    - National numbers + ISO country code.
    - Full international numbers beginning with '+'.

    Examples:
        08012345678 + NG
        -> +2348012345678

        07911 123456 + GB
        -> +447911123456

        +234 801 234 5678
        -> +2348012345678
    """

    if not isinstance(phone_number, str):
        raise PhoneServiceError(
            "Phone number must be a string."
        )

    phone_number = phone_number.strip()

    if not phone_number:
        raise PhoneServiceError(
            "Phone number is required."
        )

    if phone_number.startswith("+"):
        region = None

    else:
        if not country_code:
            raise PhoneServiceError(
                "Country code is required for "
                "national phone numbers."
            )

        if not isinstance(country_code, str):
            raise PhoneServiceError(
                "Invalid country code."
            )

        country_code = country_code.strip().upper()

        if country_code not in phonenumbers.SUPPORTED_REGIONS:
            raise PhoneServiceError(
                "Invalid country code."
            )

        region = country_code

    try:
        parsed_number = phonenumbers.parse(
            phone_number,
            region,
        )

    except NumberParseException as exc:
        raise PhoneServiceError(
            "Invalid phone number."
        ) from exc

    if not phonenumbers.is_possible_number(
        parsed_number,
    ):
        raise PhoneServiceError(
            "Invalid phone number."
        )

    if not phonenumbers.is_valid_number(
        parsed_number,
    ):
        raise PhoneServiceError(
            "Invalid phone number."
        )

    return phonenumbers.format_number(
        parsed_number,
        PhoneNumberFormat.E164,
    )


def get_verified_phone(*, user):
    """
    Return the user's verified phone if one exists.
    """

    try:
        phone = user.phone
    except UserPhone.DoesNotExist:
        return None

    if not phone.is_verified:
        return None

    return phone


@transaction.atomic
def request_phone_verification(
    *,
    user,
    phone_number,
    country_code=None,
):
    """
    Start the process of adding and verifying a phone number.

    The phone is NOT trusted until the OTP is successfully verified.
    """

    phone_number = normalize_phone_number(
        phone_number,
        country_code,
    )

    existing_phone = (
        UserPhone.objects
        .select_for_update()
        .filter(
            phone_number=phone_number,
        )
        .first()
    )

    if existing_phone is not None:
        if existing_phone.user_id != user.id:
            raise PhoneServiceError(
                "This phone number is already associated "
                "with another account."
            )

        if existing_phone.is_verified:
            raise PhoneServiceError(
                "This phone number is already verified."
            )

    otp, raw_code = create_phone_otp(
        user=user,
        phone_number=phone_number,
        purpose=PhoneOTP.Purpose.VERIFY_PHONE,
    )

    message = (
        "Your VibeNationHQ verification code is "
        f"{raw_code}. It expires in 10 minutes."
    )

    transaction.on_commit(
        lambda: send_sms(
            phone_number=phone_number,
            message=message,
        )
    )

    return otp


@transaction.atomic
def verify_phone(
    *,
    user,
    phone_number,
    code,
    country_code=None,
):
    """
    Verify a phone number using a valid OTP.

    The phone becomes trusted only after successful verification.
    """

    phone_number = normalize_phone_number(
        phone_number,
        country_code,
    )

    verify_phone_otp(
        user=user,
        phone_number=phone_number,
        purpose=PhoneOTP.Purpose.VERIFY_PHONE,
        code=code,
    )

    phone, created = (
        UserPhone.objects
        .select_for_update()
        .get_or_create(
            user=user,
            defaults={
                "phone_number": phone_number,
            },
        )
    )

    if not created:
        phone.phone_number = phone_number

    phone.verified_at = timezone.now()

    phone.save(
        update_fields=[
            "phone_number",
            "verified_at",
            "updated_at",
        ],
    )
    return phone

def request_phone_change(
    *,
    user,
    current_password,
    new_phone_number,
    country_code=None,
):
    """
    Request a phone-number change.

    The existing verified phone remains trusted until
    the new phone number is successfully verified.
    """

    if not user.check_password(
        current_password,
    ):
        raise PhoneServiceError(
            "Current password is incorrect."
        )

    new_phone_number = normalize_phone_number(
        new_phone_number,
        country_code,
    )

    current_phone = get_verified_phone(
        user=user,
    )

    if (
        current_phone is not None
        and current_phone.phone_number
        == new_phone_number
    ):
        raise PhoneServiceError(
            "This is already your verified phone number."
        )

    existing_phone = (
        UserPhone.objects
        .filter(
            phone_number=new_phone_number,
        )
        .first()
    )

    if existing_phone is not None:
        raise PhoneServiceError(
            "This phone number is already associated "
            "with another account."
        )

    otp, raw_code = create_phone_otp(
        user=user,
        phone_number=new_phone_number,
        purpose=PhoneOTP.Purpose.CHANGE_PHONE,
    )

    message = (
        "Your VibeNationHQ phone-change verification code is "
        f"{raw_code}. It expires in 10 minutes."
    )

    transaction.on_commit(
        lambda: send_sms(
            phone_number=new_phone_number,
            message=message,
        )
    )

    return otp

@transaction.atomic
def verify_phone_change(
    *,
    user,
    new_phone_number,
    code,
    country_code=None
):
    """
    Verify and complete a pending phone-number change.

    The existing verified phone is replaced only after
    successful OTP verification.
    """

    new_phone_number = normalize_phone_number(
        new_phone_number,
        country_code,
    )

    verify_phone_otp(
        user=user,
        phone_number=new_phone_number,
        purpose=PhoneOTP.Purpose.CHANGE_PHONE,
        code=code,
    )

    existing_phone = (
        UserPhone.objects
        .filter(
            phone_number=new_phone_number,
        )
        .exclude(
            user=user,
        )
        .first()
    )

    if existing_phone is not None:
        raise PhoneServiceError(
            "This phone number is already associated "
            "with another account."
        )

    phone, created = (
        UserPhone.objects
        .get_or_create(
            user=user,
            defaults={
                "phone_number": new_phone_number,
            },
        )
    )

    phone.phone_number = new_phone_number
    phone.verified_at = timezone.now()

    phone.save(
        update_fields=[
            "phone_number",
            "verified_at",
            "updated_at",
        ],
    )

    return phone