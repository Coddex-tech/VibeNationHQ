from django.contrib.auth import get_user_model
from django.db import transaction

from .verification import (
    create_email_verification_token,
    send_verification_email,
)


User = get_user_model()


@transaction.atomic
def register_user(*, email, password):
    """
    Create an ordinary VibeNationHQ account and initiate
    email verification.

    Account onboarding remains incomplete until the user
    has selected a display name and username.
    """

    user = User.objects.create_user(
        email=email,
        password=password,
        is_active=False,
        is_staff=False,
        is_superuser=False,
        onboarding_completed=False,
    )

    _, raw_token = create_email_verification_token(user)

    send_verification_email(
        user=user,
        raw_token=raw_token,
    )
    return user