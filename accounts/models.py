import secrets
import hashlib
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractUser):
    """
    Custom VibeNationHQ user model.
    """

    email = models.EmailField(
        unique=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class UserSession(models.Model):
    """
    Represents an authenticated VibeNationHQ session/device.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions",
    )

    session_key_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
    )

    device_name = models.CharField(
        max_length=255,
        blank=True,
    )

    user_agent = models.TextField(
        blank=True,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    last_seen_at = models.DateTimeField(
        auto_now=True,
    )

    expires_at = models.DateTimeField()

    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-last_seen_at"]
        indexes = [
            models.Index(
                fields=["user", "revoked_at"],
            ),
            models.Index(
                fields=["expires_at"],
            ),
        ]

    def __str__(self):
        return f"{self.user.email} session"


class EmailVerificationToken(models.Model):
    """
    One-time email verification token for a VibeNationHQ user.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="email_verification_token",
    )

    token_hash = models.CharField(
        max_length=64,
        unique=True,
    )

    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    used_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Email verification for {self.user.email}"

    @property
    def is_used(self):
        return self.used_at is not None

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired

    @staticmethod
    def generate_token():
        """
        Generate a cryptographically secure random token.
        """

        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(token):
        """
        Hash a raw verification token before storing it.
        """

        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()