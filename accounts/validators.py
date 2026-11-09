import re

from django.contrib.auth import get_user_model

from rest_framework.exceptions import ValidationError


USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 30

USERNAME_PATTERN = re.compile(
    rf"^[A-Za-z0-9_]{{{USERNAME_MIN_LENGTH},{USERNAME_MAX_LENGTH}}}$"
)


def validate_username_format(value):
    """
    Validate the format of a VibeNationHQ username.

    Allowed:
    - Letters (A-Z, a-z)
    - Numbers (0-9)
    - Underscores (_)

    Length: 3–30 characters.

    Spaces and all other special characters are rejected.
    """

    if not isinstance(value, str):
        raise ValidationError(
            "A valid username is required."
        )

    if not USERNAME_PATTERN.fullmatch(value):
        raise ValidationError(
            "Username must contain only letters, numbers "
            "and underscores, and must be between "
            "3 and 30 characters."
        )

    return value


def is_username_available(
    username,
    *,
    exclude_user=None,
):
    """
    Check username availability using case-insensitive matching.

    Optionally exclude an existing user when checking whether
    they can retain or change their own username.
    """

    User = get_user_model()

    queryset = User.objects.filter(
        username__iexact=username,
    )

    if exclude_user is not None:
        queryset = queryset.exclude(
            pk=exclude_user.pk,
        )

    return not queryset.exists()


def validate_username_availability(
    username,
    *,
    exclude_user=None,
):
    """
    Validate that a username is not already in use.
    """

    if not is_username_available(
        username,
        exclude_user=exclude_user,
    ):
        raise ValidationError(
            "This username is already taken."
        )

    return username


def normalize_generated_username(value):
    """
    Normalise an automatically generated username.

    This function is only for system-generated usernames.
    It must not be used to silently transform usernames
    manually submitted by users.
    """

    if not isinstance(value, str):
        value = ""

    value = value.lower()

    value = re.sub(
        r"[^a-z0-9_]",
        "",
        value,
    )

    value = value[:USERNAME_MAX_LENGTH]

    if len(value) < USERNAME_MIN_LENGTH:
        value = "user"

    return value
