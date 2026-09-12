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
    Create a new VibeNationHQ user account and
    initiate email verification.
    """

    user = User.objects.create_user(
        email=email,
        password=password,
        is_active=False,
    )

    _, raw_token = create_email_verification_token(
        user
    )

    send_verification_email(
        user=user,
        raw_token=raw_token,
    )

    return user