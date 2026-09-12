from django.contrib.auth import authenticate, get_user_model

User = get_user_model()


class InvalidLoginError(Exception):
    """
    Raised when login credentials are invalid.
    """


class InactiveAccountError(Exception):
    """
    Raised when the account exists but is not active.
    """


def login_user(*, email, password):
    try:
        user = User.objects.get(
            email__iexact=email,
        )
    except User.DoesNotExist:
        raise InvalidLoginError(
            "Invalid email or password."
        )

    if not user.check_password(password):
        raise InvalidLoginError(
            "Invalid email or password."
        )

    if not user.is_active:
        raise InactiveAccountError(
            "Please verify your email before signing in."
        )

    return user