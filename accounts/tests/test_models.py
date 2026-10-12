from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from accounts.models import (
    PasswordResetToken,
    EmailChangeToken,
    UserPhone,
    PhoneOTP,
    UserIdentity,
)

User = get_user_model()

class PasswordResetTokenModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="reset@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

    def test_token_can_be_created(self):
        token = PasswordResetToken.objects.create(
            user=self.user,
            token_hash="a" * 64,
            expires_at=(
                timezone.now()
                + timedelta(hours=1)
            ),
        )

        self.assertEqual(
            token.user,
            self.user,
        )

        self.assertFalse(
            token.is_used,
        )

        self.assertFalse(
            token.is_expired,
        )

        self.assertTrue(
            token.is_valid,
        )

    def test_unused_unexpired_token_is_valid(self):
        token = PasswordResetToken.objects.create(
            user=self.user,
            token_hash="b" * 64,
            expires_at=(
                timezone.now()
                + timedelta(hours=1)
            ),
        )

        self.assertTrue(
            token.is_valid,
        )

    def test_used_token_is_not_valid(self):
        token = PasswordResetToken.objects.create(
            user=self.user,
            token_hash="c" * 64,
            expires_at=(
                timezone.now()
                + timedelta(hours=1)
            ),
            used_at=timezone.now(),
        )

        self.assertTrue(
            token.is_used,
        )

        self.assertTrue(
            token.is_valid is False,
        )

    def test_expired_token_is_not_valid(self):
        token = PasswordResetToken.objects.create(
            user=self.user,
            token_hash="d" * 64,
            expires_at=(
                timezone.now()
                - timedelta(seconds=1)
            ),
        )

        self.assertTrue(
            token.is_expired,
        )

        self.assertFalse(
            token.is_valid,
        )

    def test_generate_token_returns_unique_raw_token(self):
        token_one = (
            PasswordResetToken.generate_token()
        )

        token_two = (
            PasswordResetToken.generate_token()
        )

        self.assertNotEqual(
            token_one,
            token_two,
        )

    def test_hash_token_returns_sha256_hash(self):
        raw_token = "test-password-reset-token"

        token_hash = (
            PasswordResetToken.hash_token(
                raw_token,
            )
        )

        self.assertEqual(
            len(token_hash),
            64,
        )

        self.assertNotEqual(
            token_hash,
            raw_token,
        )

    def test_token_string_representation(self):
        token = PasswordResetToken.objects.create(
            user=self.user,
            token_hash="e" * 64,
            expires_at=(
                timezone.now()
                + timedelta(hours=1)
            ),
        )

        self.assertEqual(
            str(token),
            "Password reset for reset@example.com",
        )

    def test_token_hash_is_stored_as_hash(self):
        raw_token = (
            PasswordResetToken.generate_token()
        )

        token_hash = (
            PasswordResetToken.hash_token(
                raw_token,
            )
        )

        token = PasswordResetToken.objects.create(
            user=self.user,
            token_hash=token_hash,
            expires_at=(
                timezone.now()
                + timedelta(hours=1)
            ),
        )

        self.assertNotEqual(
            token.token_hash,
            raw_token,
        )

        self.assertEqual(
            len(token.token_hash),
            64,
        )


class EmailChangeTokenModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="email-change@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

        self.expires_at = (
            timezone.now()
            + timedelta(hours=1)
        )

        self.token = EmailChangeToken.objects.create(
            user=self.user,
            new_email="new@example.com",
            token_hash=EmailChangeToken.hash_token(
                "raw-test-token",
            ),
            expires_at=self.expires_at,
        )

    def test_token_is_not_used_initially(self):
        self.assertFalse(
            self.token.is_used,
        )

    def test_token_is_valid_initially(self):
        self.assertTrue(
            self.token.is_valid,
        )

    def test_used_token_is_invalid(self):
        self.token.used_at = timezone.now()
        self.token.save(
            update_fields=["used_at"],
        )

        self.token.refresh_from_db()

        self.assertTrue(
            self.token.is_used,
        )

        self.assertFalse(
            self.token.is_valid,
        )

    def test_expired_token_is_invalid(self):
        self.token.expires_at = (
            timezone.now()
            - timedelta(seconds=1)
        )

        self.token.save(
            update_fields=["expires_at"],
        )

        self.token.refresh_from_db()

        self.assertTrue(
            self.token.is_expired,
        )

        self.assertFalse(
            self.token.is_valid,
        )

    def test_token_hash_is_deterministic(self):
        token = "some-random-token"

        first_hash = (
            EmailChangeToken.hash_token(token)
        )

        second_hash = (
            EmailChangeToken.hash_token(token)
        )

        self.assertEqual(
            first_hash,
            second_hash,
        )

    def test_generated_tokens_are_different(self):
        first = (
            EmailChangeToken.generate_token()
        )

        second = (
            EmailChangeToken.generate_token()
        )

        self.assertNotEqual(
            first,
            second,
        )

    def test_new_email_is_stored(self):
        self.assertEqual(
            self.token.new_email,
            "new@example.com",
        )

    def test_token_is_related_to_user(self):
        self.assertEqual(
            self.token.user,
            self.user,
        )


class UserPhoneModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="phone@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

        self.phone = UserPhone.objects.create(
            user=self.user,
            phone_number="+2348012345678",
        )

    def test_phone_is_unverified_initially(self):
        self.assertFalse(
            self.phone.is_verified,
        )

    def test_phone_becomes_verified(self):
        self.phone.verified_at = timezone.now()

        self.phone.save(
            update_fields=["verified_at"],
        )

        self.phone.refresh_from_db()

        self.assertTrue(
            self.phone.is_verified,
        )

    def test_phone_belongs_to_user(self):
        self.assertEqual(
            self.phone.user,
            self.user,
        )

    def test_phone_number_is_unique(self):
        another_user = User.objects.create_user(
            email="another-phone@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

        with self.assertRaises(
            IntegrityError,
        ):
            UserPhone.objects.create(
                user=another_user,
                phone_number="+2348012345678",
            )


class PhoneOTPModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="otp@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

        self.expires_at = (
            timezone.now()
            + timedelta(minutes=10)
        )

        self.otp = PhoneOTP.objects.create(
            user=self.user,
            phone_number="+2348012345678",
            purpose=PhoneOTP.Purpose.VERIFY_PHONE,
            code_hash=PhoneOTP.hash_code(
                "482913",
            ),
            expires_at=self.expires_at,
        )

    def test_otp_is_unused_initially(self):
        self.assertFalse(
            self.otp.is_used,
        )

    def test_otp_is_valid_initially(self):
        self.assertTrue(
            self.otp.is_valid,
        )

    def test_used_otp_is_invalid(self):
        self.otp.used_at = timezone.now()

        self.otp.save(
            update_fields=["used_at"],
        )

        self.otp.refresh_from_db()

        self.assertTrue(
            self.otp.is_used,
        )

        self.assertFalse(
            self.otp.is_valid,
        )

    def test_expired_otp_is_invalid(self):
        self.otp.expires_at = (
            timezone.now()
            - timedelta(seconds=1)
        )

        self.otp.save(
            update_fields=["expires_at"],
        )

        self.otp.refresh_from_db()

        self.assertTrue(
            self.otp.is_expired,
        )

        self.assertFalse(
            self.otp.is_valid,
        )

    def test_attempts_exhausted(self):
        self.otp.attempts = (
            self.otp.max_attempts
        )

        self.otp.save(
            update_fields=["attempts"],
        )

        self.otp.refresh_from_db()

        self.assertTrue(
            self.otp.attempts_exhausted,
        )

        self.assertFalse(
            self.otp.is_valid,
        )

    def test_attempts_below_limit_are_valid(self):
        self.otp.attempts = (
            self.otp.max_attempts - 1
        )

        self.otp.save(
            update_fields=["attempts"],
        )

        self.otp.refresh_from_db()

        self.assertFalse(
            self.otp.attempts_exhausted,
        )

        self.assertTrue(
            self.otp.is_valid,
        )

    def test_hash_code_is_deterministic(self):
        code = "482913"

        first_hash = (
            PhoneOTP.hash_code(code)
        )

        second_hash = (
            PhoneOTP.hash_code(code)
        )

        self.assertEqual(
            first_hash,
            second_hash,
        )

    def test_hash_is_not_raw_code(self):
        code = "482913"

        code_hash = (
            PhoneOTP.hash_code(code)
        )

        self.assertNotEqual(
            code_hash,
            code,
        )

    def test_different_codes_have_different_hashes(self):
        first_hash = PhoneOTP.hash_code(
            "482913",
        )

        second_hash = PhoneOTP.hash_code(
            "918274",
        )

        self.assertNotEqual(
            first_hash,
            second_hash,
        )

    def test_verify_phone_purpose(self):
        self.assertEqual(
            self.otp.purpose,
            PhoneOTP.Purpose.VERIFY_PHONE,
        )

    def test_change_phone_purpose(self):
        self.otp.purpose = (
            PhoneOTP.Purpose.CHANGE_PHONE
        )

        self.otp.save(
            update_fields=["purpose"],
        )

        self.otp.refresh_from_db()

        self.assertEqual(
            self.otp.purpose,
            PhoneOTP.Purpose.CHANGE_PHONE,
        )


class UserIdentityModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="google@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

        self.identity = UserIdentity.objects.create(
            user=self.user,
            provider=UserIdentity.Provider.GOOGLE,
            provider_subject="google-sub-123456789",
            email="google@example.com",
        )

    def test_identity_belongs_to_user(self):
        self.assertEqual(
            self.identity.user,
            self.user,
        )

    def test_google_provider_is_stored(self):
        self.assertEqual(
            self.identity.provider,
            UserIdentity.Provider.GOOGLE,
        )

    def test_provider_subject_is_stored(self):
        self.assertEqual(
            self.identity.provider_subject,
            "google-sub-123456789",
        )

    def test_identity_email_is_stored(self):
        self.assertEqual(
            self.identity.email,
            "google@example.com",
        )

    def test_identity_is_available_through_user(self):
        self.assertIn(
            self.identity,
            self.user.identities.all(),
        )

    def test_same_provider_and_subject_cannot_be_linked_twice(self):
        another_user = User.objects.create_user(
            email="another@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

        with self.assertRaises(
            IntegrityError,
        ):
            UserIdentity.objects.create(
                user=another_user,
                provider=UserIdentity.Provider.GOOGLE,
                provider_subject="google-sub-123456789",
                email="another@example.com",
            )

    def test_different_google_subjects_can_be_linked_to_different_users(
        self,
    ):
        another_user = User.objects.create_user(
            email="another@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

        another_identity = UserIdentity.objects.create(
            user=another_user,
            provider=UserIdentity.Provider.GOOGLE,
            provider_subject="google-sub-987654321",
            email="another@example.com",
        )

        self.assertNotEqual(
            self.identity.provider_subject,
            another_identity.provider_subject,
        )

        self.assertNotEqual(
            self.identity.user,
            another_identity.user,
        )

    def test_one_user_can_have_multiple_provider_identities(self):
        another_identity = UserIdentity.objects.create(
            user=self.user,
            provider=UserIdentity.Provider.GOOGLE,
            provider_subject="google-sub-987654321",
            email="another-google@example.com",
        )

        self.assertEqual(
            self.user.identities.count(),
            2,
        )

        self.assertIn(
            self.identity,
            self.user.identities.all(),
        )

        self.assertIn(
            another_identity,
            self.user.identities.all(),
        )

    def test_identity_is_deleted_when_user_is_deleted(self):
        identity_id = self.identity.id

        self.user.delete()

        self.assertFalse(
            UserIdentity.objects.filter(
                id=identity_id,
            ).exists(),
        )

    def test_identity_string_representation(self):
        self.assertEqual(
            str(self.identity),
            "google: google-sub-123456789",
        )