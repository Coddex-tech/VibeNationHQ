from django.contrib.auth.models import BaseUserManager

from .validators import (
    USERNAME_MAX_LENGTH,
    is_username_available,
    normalize_generated_username,
)


class UserManager(BaseUserManager):
    """
    Custom manager for VibeNationHQ accounts.

    Ordinary platform users cannot be created with Django
    administrative privileges through create_user().
    """

    USERNAME_MAX_LENGTH = USERNAME_MAX_LENGTH

    def _generate_username(self, email):
        """
        Generate a unique username from the user's email address.

        Generated usernames use lowercase letters, numbers,
        and underscores. Users can choose their own capitalization
        during onboarding.
        """

        email_prefix = email.split("@")[0]

        base = normalize_generated_username(email_prefix)

        username = base
        counter = 1

        while not is_username_available(username):
            suffix = f"_{counter}"

            available_length = (
                self.USERNAME_MAX_LENGTH - len(suffix)
            )

            if available_length < 1:
                raise RuntimeError(
                    "Unable to generate a unique username "
                    "within the allowed length."
                )

            username = (
                f"{base[:available_length]}{suffix}"
            )

            counter += 1

        return username

    def _create_user(self, email, password=None, **extra_fields):
        """
        Internal account creation method.

        Used by ordinary user creation and superuser creation.
        """

        if not email:
            raise ValueError("The email address is required.")

        email = self.normalize_email(email)

        if not extra_fields.get("username"):
            extra_fields["username"] = self._generate_username(
                email
            )

        user = self.model(
            email=email,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create an ordinary VibeNation account.

        Administrative privileges must not be granted through
        ordinary user registration.
        """

        if extra_fields.get("is_staff", False):
            raise ValueError(
                "Ordinary VibeNation users cannot have is_staff=True."
            )

        if extra_fields.get("is_superuser", False):
            raise ValueError(
                "Ordinary VibeNation users cannot be superusers."
            )

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(
            email=email,
            password=password,
            **extra_fields,
        )

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create a Django superuser.
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be is_superuser=True.")

        return self._create_user(
            email=email,
            password=password,
            **extra_fields,
        )
