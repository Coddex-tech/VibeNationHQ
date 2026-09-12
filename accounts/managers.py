import re

from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom manager for the VibeNationHQ User model.
    """

    def _generate_username(self, email):
        """
        Generate a unique username from the user's email address.
        """

        base = email.split("@")[0].lower()

        # Keep only letters, numbers, underscores and hyphens.
        base = re.sub(r"[^a-z0-9_-]", "", base)

        # Make sure we have something usable.
        if not base:
            base = "user"

        # Django's default username field allows 150 characters.
        base = base[:140]

        username = base
        counter = 1

        while self.model.objects.filter(username=username).exists():
            username = f"{base}_{counter}"
            counter += 1

        return username

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email address is required.")

        email = self.normalize_email(email)

        if not extra_fields.get("username"):
            extra_fields["username"] = self._generate_username(email)

        user = self.model(
            email=email,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email=email,
            password=password,
            **extra_fields,
        )