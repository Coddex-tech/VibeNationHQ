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


class UserIdentity(models.Model):
    """
    External authentication identity linked to a VibeNationHQ user.

    A user may have multiple external identities, such as
    Google, Apple, or future authentication providers.
    """

    class Provider(models.TextChoices):
        GOOGLE = (
            "google",
            "Google",
        )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="identities",
    )

    provider = models.CharField(
        max_length=30,
        choices=Provider.choices,
    )

    provider_subject = models.CharField(
        max_length=255,
    )

    email = models.EmailField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "provider",
                    "provider_subject",
                ],
                name="unique_user_identity_provider_subject",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "provider",
                    "provider_subject",
                ],
            ),
        ]

    def __str__(self):
        return (
            f"{self.provider}: "
            f"{self.provider_subject}"
        )


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


class PasswordResetToken(models.Model):
    """
    One-time token used to reset a user's password.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
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
        indexes = [
            models.Index(
                fields=["user", "created_at"],
            ),
            models.Index(
                fields=["expires_at"],
            ),
        ]

    def __str__(self):
        return (
            f"Password reset for {self.user.email}"
        )

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
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(token):
        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()


class EmailChangeToken(models.Model):
    """
    One-time token used to verify a new email address
    before changing the user's account email.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="email_change_tokens",
    )

    new_email = models.EmailField(
        db_index=True,
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
        indexes = [
            models.Index(
                fields=["user", "created_at"],
            ),
            models.Index(
                fields=["new_email"],
            ),
            models.Index(
                fields=["expires_at"],
            ),
        ]

    def __str__(self):
        return (
            f"Email change for "
            f"{self.user.email} → {self.new_email}"
        )

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
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(token):
        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()


class UserPhone(models.Model):
    """
    Stores the optional phone number associated with a user.
    A phone number becomes trusted only after OTP verification.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="phone",
    )

    phone_number = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.phone_number

    @property
    def is_verified(self):
        return self.verified_at is not None


class PhoneOTP(models.Model):
    """
    One-time password used for phone verification
    and other phone-related security operations.
    """

    class Purpose(models.TextChoices):
        VERIFY_PHONE = (
            "verify_phone",
            "Verify phone",
        )

        CHANGE_PHONE = (
            "change_phone",
            "Change phone",
        )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="phone_otps",
    )

    phone_number = models.CharField(
        max_length=20,
        db_index=True,
    )

    purpose = models.CharField(
        max_length=30,
        choices=Purpose.choices,
    )

    code_hash = models.CharField(
        max_length=64,
    )

    expires_at = models.DateTimeField()

    attempts = models.PositiveSmallIntegerField(
        default=0,
    )

    max_attempts = models.PositiveSmallIntegerField(
        default=5,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    used_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=[
                    "user",
                    "purpose",
                    "created_at",
                ],
            ),
            models.Index(
                fields=[
                    "phone_number",
                    "purpose",
                ],
            ),
            models.Index(
                fields=["expires_at"],
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_purpose_display()} "
            f"OTP for {self.phone_number}"
        )

    @property
    def is_used(self):
        return self.used_at is not None

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def attempts_exhausted(self):
        return self.attempts >= self.max_attempts

    @property
    def is_valid(self):
        return (
            not self.is_used
            and not self.is_expired
            and not self.attempts_exhausted
        )

    @staticmethod
    def hash_code(code):
        return hashlib.sha256(
            code.encode("utf-8")
        ).hexdigest()


# ============================================================
# ADMIN PROXY MODELS
# ============================================================


class VibeNationUser(User):
    """
    Proxy model used to display normal VibeNation users
    separately from staff accounts in the admin.

    This does NOT create another database table.
    """

    class Meta:
        proxy = True
        verbose_name = "VibeNation User"
        verbose_name_plural = "VibeNation Users"


class StaffAccount(User):
    """
    Proxy model used to display VibeNation staff accounts
    separately from normal platform users in the admin.

    This does NOT create another database table.
    """

    class Meta:
        proxy = True
        verbose_name = "Staff Account"
        verbose_name_plural = "Staff Accounts"