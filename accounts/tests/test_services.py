from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.core import mail
from django.http import HttpResponse

from unittest.mock import patch

from datetime import timedelta

from accounts.services.registration import register_user
from accounts.models import (
    EmailVerificationToken,
    User,
    PasswordResetToken,
    EmailChangeToken,
    PhoneOTP,
    UserPhone,
    UserIdentity,
)
from accounts.services.authentication import (
    AUTH_COOKIE_NAME,
    authenticate_web_user,
)
from accounts.services.verification import (
    VERIFICATION_RESEND_COOLDOWN,
    create_email_verification_token,
    verify_email_token,
    resend_email_verification,
    send_verification_email,
)
from accounts.services.login import (
    InactiveAccountError,
    InvalidLoginError,
    login_user,
)
from accounts.services.sessions import (
    InvalidSessionError,
    create_session,
    get_valid_session,
    revoke_session,
)
from accounts.services.password import (
    PASSWORD_RESET_TOKEN_LIFETIME,
    consume_password_reset_token,
    create_password_reset_token,
    verify_password_reset_token,
)
from accounts.services.security import (
    EmailChangeError,
    confirm_email_change,
    create_email_change_token,
    request_email_change,
    verify_email_change_token,
    PHONE_OTP_LIFETIME,
    PHONE_OTP_MAX_ATTEMPTS,
    PHONE_OTP_RESEND_COOLDOWN,
    create_phone_otp,
    generate_phone_otp_code,
    verify_phone_otp,
)
from accounts.services.sms import (
    ConsoleSMSProvider,
    SMSDeliveryError,
    get_sms_provider,
    send_sms,
)
from accounts.services.phone import (
    PhoneServiceError,
    get_verified_phone,
    normalize_phone_number,
    request_phone_change,
    request_phone_verification,
    verify_phone,
    verify_phone_change,
)
from accounts.services.google import (
    GoogleAccountError,
    InvalidGoogleTokenError,
    resolve_google_user,
    verify_google_id_token,
    login_with_google,
)

User = get_user_model()


class RegistrationServiceTests(TestCase):
    def test_register_user_creates_account(self):
        user = register_user(
            email="john@example.com",
            password="StrongPassword123!",
        )

        self.assertIsNotNone(user.pk)
        self.assertEqual(
            user.email,
            "john@example.com",
        )

        self.assertTrue(
            user.check_password("StrongPassword123!")
        )

    def test_registered_user_is_inactive(self):
        user = register_user(
            email="john@example.com",
            password="StrongPassword123!",
        )

        self.assertFalse(user.is_active)

    def test_username_is_generated(self):
        user = register_user(
            email="john@example.com",
            password="StrongPassword123!",
        )

        self.assertEqual(
            user.username,
            "john",
        )

    def test_password_is_hashed(self):
        user = register_user(
            email="john@example.com",
            password="StrongPassword123!",
        )

        self.assertNotEqual(
            user.password,
            "StrongPassword123!",
        )

        self.assertTrue(
            user.check_password("StrongPassword123!")
        )

        def test_register_user_creates_verification_token(self):
            register_user(
                email="john@example.com",
                password="StrongPassword123!",
            )

            self.assertEqual(
                EmailVerificationToken.objects.count(),
                1,
            )

        def test_register_user_sends_verification_email(self):
            register_user(
                email="john@example.com",
                password="StrongPassword123!",
            )

            self.assertEqual(
                len(mail.outbox),
                1,
            )

            self.assertEqual(
                mail.outbox[0].to,
                ["john@example.com"],
            )

        def test_register_user_email_contains_verification_token(self):
            register_user(
                email="john@example.com",
                password="StrongPassword123!",
            )

            email = mail.outbox[0]

            verification_token = (
                EmailVerificationToken.objects.get(
                    user__email="john@example.com"
                )
            )

            # The raw token isn't stored, so we can't compare
            # directly against the database value.
            # Instead, verify that the email contains the
            # expected verification URL structure.
            self.assertIn(
                "http://localhost:3000/verify-email?token=",
                email.body,
            )


class EmailVerificationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="john@example.com",
            password="StrongPassword123!",
            is_active=False,
        )

    def test_create_email_verification_token(self):
        verification_token, raw_token = (
            create_email_verification_token(
                self.user
            )
        )

        self.assertIsNotNone(
            verification_token.pk
        )

        self.assertTrue(raw_token)

        self.assertNotEqual(
            verification_token.token_hash,
            raw_token,
        )

    def test_token_is_stored_as_hash(self):
        verification_token, raw_token = (
            create_email_verification_token(
                self.user
            )
        )

        self.assertEqual(
            len(verification_token.token_hash),
            64,
        )

        self.assertNotEqual(
            verification_token.token_hash,
            raw_token,
        )

    def test_token_expires_in_24_hours(self):
        verification_token, _ = (
            create_email_verification_token(
                self.user
            )
        )

        now = timezone.now()

        difference = (
            verification_token.expires_at - now
        )

        self.assertGreater(
            difference.total_seconds(),
            23 * 60 * 60,
        )

        self.assertLess(
            difference.total_seconds(),
            25 * 60 * 60,
        )

    def test_new_token_replaces_previous_token(self):
        first_token, first_raw_token = (
            create_email_verification_token(
                self.user
            )
        )

        second_token, second_raw_token = (
            create_email_verification_token(
                self.user
            )
        )

        self.assertEqual(
            EmailVerificationToken.objects.count(),
            1,
        )

        self.assertEqual(
            first_token.pk,
            second_token.pk,
        )

        self.assertNotEqual(
            first_raw_token,
            second_raw_token,
        )

        with self.assertRaises(ValueError):
            verify_email_token(
                raw_token=first_raw_token
            )

    def test_valid_token_activates_user(self):
        _, raw_token = (
            create_email_verification_token(
                self.user
            )
        )

        user = verify_email_token(
            raw_token=raw_token
        )

        user.refresh_from_db()

        self.assertEqual(
            user.pk,
            self.user.pk,
        )

        self.assertTrue(
            user.is_active
        )

    def test_valid_token_is_marked_used(self):
        verification_token, raw_token = (
            create_email_verification_token(
                self.user
            )
        )

        verify_email_token(
            raw_token=raw_token
        )

        verification_token.refresh_from_db()

        self.assertIsNotNone(
            verification_token.used_at
        )

    def test_used_token_cannot_be_used_again(self):
        _, raw_token = (
            create_email_verification_token(
                self.user
            )
        )

        verify_email_token(
            raw_token=raw_token
        )

        with self.assertRaises(ValueError):
            verify_email_token(
                raw_token=raw_token
            )

    def test_invalid_token_is_rejected(self):
        with self.assertRaises(ValueError):
            verify_email_token(
                raw_token="completely-invalid-token"
            )

    def test_expired_token_is_rejected(self):
        verification_token, raw_token = (
            create_email_verification_token(
                self.user
            )
        )

        verification_token.expires_at = (
            timezone.now() - timedelta(minutes=1)
        )

        verification_token.save(
            update_fields=["expires_at"]
        )

        with self.assertRaises(ValueError):
            verify_email_token(
                raw_token=raw_token
            )

    def test_expired_token_does_not_activate_user(self):
        verification_token, raw_token = (
            create_email_verification_token(
                self.user
            )
        )

        verification_token.expires_at = (
            timezone.now() - timedelta(minutes=1)
        )

        verification_token.save(
            update_fields=["expires_at"]
        )

        with self.assertRaises(ValueError):
            verify_email_token(
                raw_token=raw_token
            )

        self.user.refresh_from_db()

        self.assertFalse(
            self.user.is_active
        )

class VerificationEmailServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="john@example.com",
            password="StrongPassword123!",
            is_active=False,
        )

        self.verification_token, self.raw_token = (
            create_email_verification_token(
                self.user
            )
        )

    def test_verification_email_is_sent(self):
        send_verification_email(
            user=self.user,
            raw_token=self.raw_token,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

    def test_verification_email_recipient(self):
        send_verification_email(
            user=self.user,
            raw_token=self.raw_token,
        )

        email = mail.outbox[0]

        self.assertEqual(
            email.to,
            ["john@example.com"],
        )

    def test_verification_email_subject(self):
        send_verification_email(
            user=self.user,
            raw_token=self.raw_token,
        )

        email = mail.outbox[0]

        self.assertEqual(
            email.subject,
            "Verify your VibeNationHQ account",
        )

    def test_verification_email_contains_token(self):
        send_verification_email(
            user=self.user,
            raw_token=self.raw_token,
        )

        email = mail.outbox[0]

        self.assertIn(
            self.raw_token,
            email.body,
        )

    def test_verification_email_contains_frontend_url(self):
        send_verification_email(
            user=self.user,
            raw_token=self.raw_token,
        )

        email = mail.outbox[0]

        self.assertIn(
            "http://localhost:3000/verify-email",
            email.body,
        )

    def test_verification_email_does_not_contain_password(self):
        password = "StrongPassword123!"

        send_verification_email(
            user=self.user,
            raw_token=self.raw_token,
        )

        email = mail.outbox[0]

        self.assertNotIn(
            password,
            email.body,
        )


class EmailVerificationResendServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="john@example.com",
            password="StrongPassword123!",
            is_active=False,
        )

    def test_resend_creates_verification_token(self):
        resend_email_verification(
            user=self.user
        )

        self.assertEqual(
            EmailVerificationToken.objects.count(),
            1,
        )

    def test_resend_sends_email(self):
        resend_email_verification(
            user=self.user
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        self.assertEqual(
            mail.outbox[0].to,
            ["john@example.com"],
        )

    def test_resend_cannot_be_requested_during_cooldown(self):
        resend_email_verification(
            user=self.user
        )

        with self.assertRaises(ValueError):
            resend_email_verification(
                user=self.user
            )

    def test_resend_replaces_previous_token_after_cooldown(self):
        first_token, first_raw_token = (
            create_email_verification_token(
                self.user
            )
        )

        # Move the existing token into the past so
        # the cooldown has expired.
        first_token.created_at = (
            timezone.now()
            - VERIFICATION_RESEND_COOLDOWN
            - timedelta(seconds=1)
        )

        first_token.save(
            update_fields=["created_at"]
        )

        resend_email_verification(
            user=self.user
        )

        self.assertEqual(
            EmailVerificationToken.objects.count(),
            1,
        )

        with self.assertRaises(ValueError):
            verify_email_token(
                raw_token=first_raw_token
            )

    def test_verified_user_cannot_resend(self):
        self.user.is_active = True
        self.user.save(
            update_fields=["is_active"]
        )

        with self.assertRaises(ValueError):
            resend_email_verification(
                user=self.user
            )


class LoginServiceTests(TestCase):

    def setUp(self):
        self.password = "StrongPassword123!"

        self.active_user = User.objects.create_user(
            email="john@example.com",
            password=self.password,
            is_active=True,
        )

        self.inactive_user = User.objects.create_user(
            email="inactive@example.com",
            password=self.password,
            is_active=False,
        )

    def test_valid_credentials_return_user(self):
        user = login_user(
            email="john@example.com",
            password=self.password,
        )

        self.assertEqual(
            user,
            self.active_user,
        )

    def test_wrong_password_is_rejected(self):
        with self.assertRaises(InvalidLoginError):
            login_user(
                email="john@example.com",
                password="WrongPassword123!",
            )

    def test_unknown_email_is_rejected(self):
        with self.assertRaises(InvalidLoginError):
            login_user(
                email="unknown@example.com",
                password=self.password,
            )

    def test_inactive_account_is_rejected(self):
        with self.assertRaises(InactiveAccountError):
            login_user(
                email="inactive@example.com",
                password=self.password,
            )


class SessionServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="session@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

    def test_create_session_returns_raw_secret(self):
        session, raw_secret = create_session(
            user=self.user,
            device_name="Chrome on Windows",
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1",
        )

        self.assertIsNotNone(session)
        self.assertTrue(raw_secret)

        self.assertEqual(
            session.user,
            self.user,
        )

    def test_raw_secret_is_not_stored(self):
        session, raw_secret = create_session(
            user=self.user,
        )

        self.assertNotEqual(
            session.session_key_hash,
            raw_secret,
        )

        self.assertEqual(
            len(session.session_key_hash),
            64,
        )

    def test_session_secret_is_random(self):
        session_one, secret_one = create_session(
            user=self.user,
        )

        session_two, secret_two = create_session(
            user=self.user,
        )

        self.assertNotEqual(
            secret_one,
            secret_two,
        )

        self.assertNotEqual(
            session_one.session_key_hash,
            session_two.session_key_hash,
        )

    def test_valid_session_can_be_retrieved(self):
        session, raw_secret = create_session(
            user=self.user,
        )

        retrieved_session = get_valid_session(
            raw_secret=raw_secret,
        )

        self.assertEqual(
            retrieved_session,
            session,
        )

    def test_invalid_secret_is_rejected(self):
        create_session(
            user=self.user,
        )

        with self.assertRaises(InvalidSessionError):
            get_valid_session(
                raw_secret="invalid-secret",
            )

    def test_expired_session_is_rejected(self):
        session, raw_secret = create_session(
            user=self.user,
        )

        session.expires_at = (
            timezone.now()
            - timedelta(minutes=1)
        )

        session.save(
            update_fields=["expires_at"],
        )

        with self.assertRaises(InvalidSessionError):
            get_valid_session(
                raw_secret=raw_secret,
            )

    def test_revoked_session_is_rejected(self):
        session, raw_secret = create_session(
            user=self.user,
        )

        revoke_session(
            raw_secret=raw_secret,
        )

        with self.assertRaises(InvalidSessionError):
            get_valid_session(
                raw_secret=raw_secret,
            )

    def test_inactive_user_session_is_rejected(self):
        session, raw_secret = create_session(
            user=self.user,
        )

        self.user.is_active = False
        self.user.save(
            update_fields=["is_active"],
        )

        with self.assertRaises(InvalidSessionError):
            get_valid_session(
                raw_secret=raw_secret,
            )

    def test_revoke_session(self):
        session, raw_secret = create_session(
            user=self.user,
        )

        self.assertIsNone(
            session.revoked_at,
        )

        revoked_session = revoke_session(
            raw_secret=raw_secret,
        )

        self.assertIsNotNone(
            revoked_session.revoked_at,
        )

    def test_revoking_session_twice_is_safe(self):
        session, raw_secret = create_session(
            user=self.user,
        )

        first_result = revoke_session(
            raw_secret=raw_secret,
        )

        first_revoked_at = first_result.revoked_at

        second_result = revoke_session(
            raw_secret=raw_secret,
        )

        self.assertEqual(
            second_result.revoked_at,
            first_revoked_at,
        )


class WebAuthenticationServiceTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            email="web@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

    def test_authenticate_web_user_creates_session(self):
        request = self.factory.get("/")

        response = HttpResponse()

        session = authenticate_web_user(
            request=request,
            response=response,
            user=self.user,
        )

        self.assertIsNotNone(session)

        self.assertEqual(
            session.user,
            self.user,
        )

        self.assertIsNone(
            session.revoked_at,
        )

    def test_authenticate_web_user_sets_cookie(self):
        request = self.factory.get("/")

        response = HttpResponse()

        authenticate_web_user(
            request=request,
            response=response,
            user=self.user,
        )

        self.assertIn(
            AUTH_COOKIE_NAME,
            response.cookies,
        )

    def test_auth_cookie_is_httponly(self):
        request = self.factory.get("/")

        response = HttpResponse()

        authenticate_web_user(
            request=request,
            response=response,
            user=self.user,
        )

        cookie = response.cookies[
            AUTH_COOKIE_NAME
        ]

        self.assertTrue(
            cookie["httponly"],
        )

    def test_auth_cookie_uses_samesite_lax(self):
        request = self.factory.get("/")

        response = HttpResponse()

        authenticate_web_user(
            request=request,
            response=response,
            user=self.user,
        )

        cookie = response.cookies[
            AUTH_COOKIE_NAME
        ]

        self.assertEqual(
            cookie["samesite"],
            "Lax",
        )

    def test_auth_cookie_is_not_secure_in_development(self):
        request = self.factory.get("/")

        response = HttpResponse()

        authenticate_web_user(
            request=request,
            response=response,
            user=self.user,
        )

        cookie = response.cookies[
            AUTH_COOKIE_NAME
        ]

        self.assertFalse(
            cookie["secure"],
        )

    def test_session_stores_user_agent(self):
        request = self.factory.get(
            "/",
            HTTP_USER_AGENT="VibeNationTestBrowser/1.0",
        )

        response = HttpResponse()

        session = authenticate_web_user(
            request=request,
            response=response,
            user=self.user,
        )

        self.assertEqual(
            session.user_agent,
            "VibeNationTestBrowser/1.0",
        )

    def test_session_stores_ip_address(self):
        request = self.factory.get(
            "/",
            REMOTE_ADDR="127.0.0.1",
        )

        response = HttpResponse()

        session = authenticate_web_user(
            request=request,
            response=response,
            user=self.user,
        )

        self.assertEqual(
            session.ip_address,
            "127.0.0.1",
        )

    def test_raw_secret_is_not_in_response_body(self):
        request = self.factory.get("/")

        response = HttpResponse()

        authenticate_web_user(
            request=request,
            response=response,
            user=self.user,
        )

        self.assertEqual(
            response.content,
            b"",
        )

    def test_cookie_has_session_lifetime(self):
        request = self.factory.get("/")

        response = HttpResponse()

        authenticate_web_user(
            request=request,
            response=response,
            user=self.user,
        )

        cookie = response.cookies[
            AUTH_COOKIE_NAME
        ]

        self.assertEqual(
            cookie["max-age"],
            30 * 24 * 60 * 60,
        )


from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import (
    UserSession,
    PhoneOTP,
    User,
)
from accounts.services.password import change_password


User = get_user_model()


class ChangePasswordServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="password@example.com",
            password="OldPassword123!",
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="OtherPassword123!",
        )

        self.current_session = UserSession.objects.create(
            user=self.user,
            session_key_hash="a" * 64,
            expires_at=timezone.now() + timedelta(days=30),
        )

        self.other_session = UserSession.objects.create(
            user=self.user,
            session_key_hash="b" * 64,
            expires_at=timezone.now() + timedelta(days=30),
        )

        self.other_user_session = UserSession.objects.create(
            user=self.other_user,
            session_key_hash="c" * 64,
            expires_at=timezone.now() + timedelta(days=30),
        )

    def test_changes_password(self):
        change_password(
            user=self.user,
            new_password="NewPassword456!",
            current_session_id=self.current_session.id,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "NewPassword456!"
            )
        )

    def test_keeps_current_session(self):
        change_password(
            user=self.user,
            new_password="NewPassword456!",
            current_session_id=self.current_session.id,
        )

        self.current_session.refresh_from_db()

        self.assertIsNone(
            self.current_session.revoked_at,
        )

    def test_revokes_other_sessions(self):
        change_password(
            user=self.user,
            new_password="NewPassword456!",
            current_session_id=self.current_session.id,
        )

        self.other_session.refresh_from_db()

        self.assertIsNotNone(
            self.other_session.revoked_at,
        )

    def test_does_not_revoke_other_users_sessions(self):
        change_password(
            user=self.user,
            new_password="NewPassword456!",
            current_session_id=self.current_session.id,
        )

        self.other_user_session.refresh_from_db()

        self.assertIsNone(
            self.other_user_session.revoked_at,
        )


class PasswordResetTokenServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="reset@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

    def test_create_password_reset_token(self):
        token, raw_token = (
            create_password_reset_token(
                user=self.user,
            )
        )

        self.assertIsNotNone(
            token,
        )

        self.assertTrue(
            raw_token,
        )

        self.assertNotEqual(
            token.token_hash,
            raw_token,
        )

        self.assertEqual(
            token.user,
            self.user,
        )

    def test_created_token_expires_in_one_hour(self):
        before = timezone.now()

        token, _ = create_password_reset_token(
            user=self.user,
        )

        after = timezone.now()

        expected_min = (
            before
            + PASSWORD_RESET_TOKEN_LIFETIME
        )

        expected_max = (
            after
            + PASSWORD_RESET_TOKEN_LIFETIME
        )

        self.assertGreaterEqual(
            token.expires_at,
            expected_min,
        )

        self.assertLessEqual(
            token.expires_at,
            expected_max,
        )

    def test_created_token_can_be_verified(self):
        _, raw_token = (
            create_password_reset_token(
                user=self.user,
            )
        )

        token = verify_password_reset_token(
            raw_token=raw_token,
        )

        self.assertEqual(
            token.user,
            self.user,
        )

        self.assertTrue(
            token.is_valid,
        )

    def test_invalid_token_is_rejected(self):
        with self.assertRaisesMessage(
            ValueError,
            "Invalid or expired password reset token.",
        ):
            verify_password_reset_token(
                raw_token="invalid-token",
            )

    def test_expired_token_is_rejected(self):
        token, raw_token = (
            create_password_reset_token(
                user=self.user,
            )
        )

        token.expires_at = (
            timezone.now()
            - timedelta(seconds=1)
        )

        token.save(
            update_fields=["expires_at"],
        )

        with self.assertRaisesMessage(
            ValueError,
            "Invalid or expired password reset token.",
        ):
            verify_password_reset_token(
                raw_token=raw_token,
            )

    def test_used_token_is_rejected(self):
        token, raw_token = (
            create_password_reset_token(
                user=self.user,
            )
        )

        token.used_at = timezone.now()

        token.save(
            update_fields=["used_at"],
        )

        with self.assertRaisesMessage(
            ValueError,
            "Invalid or expired password reset token.",
        ):
            verify_password_reset_token(
                raw_token=raw_token,
            )

    def test_new_token_invalidates_previous_active_token(
        self,
    ):
        _, first_raw_token = (
            create_password_reset_token(
                user=self.user,
            )
        )

        first_token = PasswordResetToken.objects.get(
            user=self.user,
            token_hash=(
                PasswordResetToken.hash_token(
                    first_raw_token,
                )
            ),
        )

        _, second_raw_token = (
            create_password_reset_token(
                user=self.user,
            )
        )

        first_token.refresh_from_db()

        self.assertIsNotNone(
            first_token.used_at,
        )

        with self.assertRaisesMessage(
            ValueError,
            "Invalid or expired password reset token.",
        ):
            verify_password_reset_token(
                raw_token=first_raw_token,
            )

        second_token = (
            verify_password_reset_token(
                raw_token=second_raw_token,
            )
        )

        self.assertTrue(
            second_token.is_valid,
        )

    def test_consume_token_marks_it_used(self):
        _, raw_token = (
            create_password_reset_token(
                user=self.user,
            )
        )

        token = consume_password_reset_token(
            raw_token=raw_token,
        )

        self.assertIsNotNone(
            token.used_at,
        )

        self.assertFalse(
            token.is_valid,
        )

    def test_consumed_token_cannot_be_consumed_again(
        self,
    ):
        _, raw_token = (
            create_password_reset_token(
                user=self.user,
            )
        )

        consume_password_reset_token(
            raw_token=raw_token,
        )

        with self.assertRaisesMessage(
            ValueError,
            "Invalid or expired password reset token.",
        ):
            consume_password_reset_token(
                raw_token=raw_token,
            )

    def test_inactive_user_token_is_rejected(self):
        self.user.is_active = False

        self.user.save(
            update_fields=["is_active"],
        )

        _, raw_token = (
            create_password_reset_token(
                user=self.user,
            )
        )

        with self.assertRaisesMessage(
            ValueError,
            "Invalid or expired password reset token.",
        ):
            verify_password_reset_token(
                raw_token=raw_token,
            )


class EmailChangeServiceTests(TestCase):

    def setUp(self):
        self.password = (
            "StrongPassword123!"
        )

        self.user = User.objects.create_user(
            email="old@example.com",
            password=self.password,
            is_active=True,
        )

        self.new_email = (
            "new@example.com"
        )

    def test_create_email_change_token(self):
        token, raw_token = (
            create_email_change_token(
                user=self.user,
                new_email=self.new_email,
            )
        )

        self.assertIsNotNone(token)

        self.assertTrue(
            raw_token
        )

        self.assertNotEqual(
            token.token_hash,
            raw_token,
        )

        self.assertEqual(
            token.new_email,
            self.new_email,
        )

    def test_token_hash_is_stored_not_raw_token(self):
        token, raw_token = (
            create_email_change_token(
                user=self.user,
                new_email=self.new_email,
            )
        )

        self.assertNotEqual(
            token.token_hash,
            raw_token,
        )

        self.assertEqual(
            token.token_hash,
            EmailChangeToken.hash_token(
                raw_token
            ),
        )

    def test_request_email_change_requires_current_password(
        self,
    ):
        with self.assertRaises(
            EmailChangeError
        ):
            request_email_change(
                user=self.user,
                current_password="WrongPassword123!",
                new_email=self.new_email,
            )

        self.assertFalse(
            EmailChangeToken.objects.exists()
        )

    def test_request_email_change_sends_token(
        self,
    ):
        token = request_email_change(
            user=self.user,
            current_password=self.password,
            new_email=self.new_email,
        )

        self.assertIsNotNone(token)

        self.assertEqual(
            token.new_email,
            self.new_email,
        )

    def test_same_email_is_rejected(self):
        with self.assertRaises(
            EmailChangeError
        ):
            request_email_change(
                user=self.user,
                current_password=self.password,
                new_email=self.user.email,
            )

    def test_existing_email_is_rejected(self):
        User.objects.create_user(
            email="taken@example.com",
            password=self.password,
            is_active=True,
        )

        with self.assertRaises(
            EmailChangeError
        ):
            request_email_change(
                user=self.user,
                current_password=self.password,
                new_email="taken@example.com",
            )

    def test_previous_active_token_is_invalidated(
        self,
    ):
        first_token, _ = (
            create_email_change_token(
                user=self.user,
                new_email="first@example.com",
            )
        )

        second_token, _ = (
            create_email_change_token(
                user=self.user,
                new_email="second@example.com",
            )
        )

        first_token.refresh_from_db()

        self.assertIsNotNone(
            first_token.used_at
        )

        self.assertIsNone(
            second_token.used_at
        )

    def test_verify_token_returns_valid_token(
        self,
    ):
        token, raw_token = (
            create_email_change_token(
                user=self.user,
                new_email=self.new_email,
            )
        )

        verified = verify_email_change_token(
            raw_token=raw_token,
        )

        self.assertEqual(
            verified,
            token,
        )

    def test_confirm_email_change_updates_email(
        self,
    ):
        _, raw_token = (
            create_email_change_token(
                user=self.user,
                new_email=self.new_email,
            )
        )

        confirm_email_change(
            raw_token=raw_token,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.email,
            self.new_email,
        )

    def test_confirm_email_change_consumes_token(
        self,
    ):
        token, raw_token = (
            create_email_change_token(
                user=self.user,
                new_email=self.new_email,
            )
        )

        confirm_email_change(
            raw_token=raw_token,
        )

        token.refresh_from_db()

        self.assertIsNotNone(
            token.used_at
        )

    def test_consumed_token_cannot_be_used_again(
        self,
    ):
        _, raw_token = (
            create_email_change_token(
                user=self.user,
                new_email=self.new_email,
            )
        )

        confirm_email_change(
            raw_token=raw_token,
        )

        with self.assertRaises(
            EmailChangeError
        ):
            confirm_email_change(
                raw_token=raw_token,
            )


class PhoneOTPServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="otp-service@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

        self.phone_number = (
            "+2348012345678"
        )

        self.purpose = (
            PhoneOTP.Purpose.VERIFY_PHONE
        )

    def test_generated_code_has_six_digits(self):
        code = generate_phone_otp_code()

        self.assertEqual(
            len(code),
            6,
        )

        self.assertTrue(
            code.isdigit(),
        )

    def test_create_phone_otp(self):
        otp, raw_code = create_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=self.purpose,
        )

        self.assertIsNotNone(
            otp,
        )

        self.assertEqual(
            len(raw_code),
            6,
        )

        self.assertTrue(
            raw_code.isdigit(),
        )

    def test_raw_code_is_not_stored(self):
        otp, raw_code = create_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=self.purpose,
        )

        self.assertNotEqual(
            otp.code_hash,
            raw_code,
        )

        self.assertEqual(
            otp.code_hash,
            PhoneOTP.hash_code(
                raw_code,
            ),
        )

    def test_otp_expires_in_ten_minutes(self):
        before = timezone.now()

        otp, _ = create_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=self.purpose,
        )

        after = timezone.now()

        expected_minimum = (
            before
            + PHONE_OTP_LIFETIME
        )

        expected_maximum = (
            after
            + PHONE_OTP_LIFETIME
        )

        self.assertGreaterEqual(
            otp.expires_at,
            expected_minimum,
        )

        self.assertLessEqual(
            otp.expires_at,
            expected_maximum,
        )

    def test_max_attempts_are_configured(self):
        otp, _ = create_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=self.purpose,
        )

        self.assertEqual(
            otp.max_attempts,
            PHONE_OTP_MAX_ATTEMPTS,
        )

    def test_correct_code_verifies(self):
        otp, raw_code = create_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=self.purpose,
        )

        verified = verify_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=self.purpose,
            code=raw_code,
        )

        self.assertEqual(
            verified,
            otp,
        )

        otp.refresh_from_db()

        self.assertIsNotNone(
            otp.used_at,
        )

    def test_wrong_code_is_rejected(self):
        create_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=self.purpose,
        )

        with self.assertRaises(
            ValueError,
        ):
            verify_phone_otp(
                user=self.user,
                phone_number=self.phone_number,
                purpose=self.purpose,
                code="000000",
            )

    def test_wrong_code_increments_attempts(self):
        otp, raw_code = create_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=PhoneOTP.Purpose.VERIFY_PHONE,
        )

        with self.assertRaises(ValueError):
            verify_phone_otp(
                user=self.user,
                phone_number=self.phone_number,
                purpose=PhoneOTP.Purpose.VERIFY_PHONE,
                code="000000",
            )

        otp.refresh_from_db()

        self.assertEqual(
            otp.attempts,
            1,
        )

    def test_fifth_wrong_attempt_exhausts_otp(self):
        otp, raw_code = create_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=PhoneOTP.Purpose.VERIFY_PHONE,
        )

        for _ in range(5):
            with self.assertRaises(ValueError):
                verify_phone_otp(
                    user=self.user,
                    phone_number=self.phone_number,
                    purpose=PhoneOTP.Purpose.VERIFY_PHONE,
                    code="000000",
                )

        otp.refresh_from_db()

        self.assertTrue(
            otp.attempts_exhausted,
        )

    def test_exhausted_otp_cannot_be_verified(
        self,
    ):
        otp, raw_code = create_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=self.purpose,
        )

        otp.attempts = (
            PHONE_OTP_MAX_ATTEMPTS
        )

        otp.save(
            update_fields=["attempts"],
        )

        with self.assertRaises(
            ValueError,
        ):
            verify_phone_otp(
                user=self.user,
                phone_number=self.phone_number,
                purpose=self.purpose,
                code=raw_code,
            )

    def test_expired_otp_cannot_be_verified(
        self,
    ):
        otp, raw_code = create_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=self.purpose,
        )

        otp.expires_at = (
            timezone.now()
            - timedelta(seconds=1)
        )

        otp.save(
            update_fields=["expires_at"],
        )

        with self.assertRaises(
            ValueError,
        ):
            verify_phone_otp(
                user=self.user,
                phone_number=self.phone_number,
                purpose=self.purpose,
                code=raw_code,
            )

    def test_used_otp_cannot_be_verified(self):
        otp, raw_code = create_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=self.purpose,
        )

        verify_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=self.purpose,
            code=raw_code,
        )

        with self.assertRaises(
            ValueError,
        ):
            verify_phone_otp(
                user=self.user,
                phone_number=self.phone_number,
                purpose=self.purpose,
                code=raw_code,
            )

    def test_new_otp_invalidates_previous_otp(
        self,
    ):
        first_otp, first_code = (
            create_phone_otp(
                user=self.user,
                phone_number=self.phone_number,
                purpose=self.purpose,
            )
        )

        # Move past the resend cooldown.
        first_otp.created_at = (
            timezone.now()
            - PHONE_OTP_RESEND_COOLDOWN
            - timedelta(seconds=1)
        )

        first_otp.save(
            update_fields=["created_at"],
        )

        second_otp, second_code = (
            create_phone_otp(
                user=self.user,
                phone_number=self.phone_number,
                purpose=self.purpose,
            )
        )

        first_otp.refresh_from_db()

        self.assertIsNotNone(
            first_otp.used_at,
        )

        self.assertIsNone(
            second_otp.used_at,
        )

    def test_resend_within_cooldown_is_rejected(
        self,
    ):
        create_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=self.purpose,
        )

        with self.assertRaises(
            ValueError,
        ):
            create_phone_otp(
                user=self.user,
                phone_number=self.phone_number,
                purpose=self.purpose,
            )

    def test_different_phone_does_not_verify(
        self,
    ):
        otp, raw_code = create_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=self.purpose,
        )

        with self.assertRaises(
            ValueError,
        ):
            verify_phone_otp(
                user=self.user,
                phone_number="+2348099999999",
                purpose=self.purpose,
                code=raw_code,
            )

    def test_different_purpose_does_not_verify(
        self,
    ):
        otp, raw_code = create_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=self.purpose,
        )

        with self.assertRaises(
            ValueError,
        ):
            verify_phone_otp(
                user=self.user,
                phone_number=self.phone_number,
                purpose=PhoneOTP.Purpose.CHANGE_PHONE,
                code=raw_code,
            )

class SMSDeliveryError(Exception):
    """
    Raised when an SMS cannot be delivered.
    """
    pass


class SMSProvider:
    """
    Provider-neutral SMS interface.

    Concrete SMS providers will implement this interface later.
    """

    def send(
        self,
        *,
        phone_number,
        message,
    ):
        raise NotImplementedError


class ConsoleSMSProvider(SMSProvider):
    """
    Development SMS provider.

    Prints SMS messages to the console instead of sending
    real SMS messages.
    """

    def send(
        self,
        *,
        phone_number,
        message,
    ):
        print(
            "\n"
            "========== VibeNationHQ SMS ==========\n"
            f"To: {phone_number}\n"
            f"Message: {message}\n"
            "=======================================\n"
        )

        return True


def get_sms_provider():
    """
    Return the configured SMS provider.
    """

    return ConsoleSMSProvider()


def send_sms(
    *,
    phone_number,
    message,
):
    """
    Send an SMS using the configured provider.
    """

    provider = get_sms_provider()

    try:
        return provider.send(
            phone_number=phone_number,
            message=message,
        )
    except Exception as exc:
        raise SMSDeliveryError(
            "Unable to send SMS."
        ) from exc

class SMSServicesTests(TestCase):

    def test_console_sms_provider_sends_successfully(self):
        provider = ConsoleSMSProvider()

        result = provider.send(
            phone_number="+2348012345678",
            message="Your VibeNationHQ verification code is 123456.",
        )

        self.assertTrue(
            result,
        )

    def test_get_sms_provider_returns_provider(self):
        provider = get_sms_provider()

        self.assertIsInstance(
            provider,
            ConsoleSMSProvider,
        )

    def test_send_sms_returns_success(self):
        result = send_sms(
            phone_number="+2348012345678",
            message="Your VibeNationHQ verification code is 123456.",
        )

        self.assertTrue(
            result,
        )


class PhoneServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="phone-service@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

        self.phone_number = (
            "+2348012345678"
        )

        self.purpose = (
            PhoneOTP.Purpose.VERIFY_PHONE
        )

    def test_normalize_phone_number(self):
        result = normalize_phone_number(
            "  +2348012345678  ",
        )

        self.assertEqual(
            result,
            "+2348012345678",
        )

    def test_normalize_nigerian_national_number(self):
        result = normalize_phone_number(
            "08012345678",
            "NG",
        )

        self.assertEqual(
            result,
            "+2348012345678",
        )


    def test_normalize_uk_national_number(self):
        result = normalize_phone_number(
            "07911 123456",
            "GB",
        )

        self.assertEqual(
            result,
            "+447911123456",
        )


    def test_national_number_without_country_code_is_rejected(self):
        with self.assertRaises(
            PhoneServiceError,
        ):
            normalize_phone_number(
                "08012345678",
            )


    def test_full_international_number_does_not_require_country_code(
        self,
    ):
        result = normalize_phone_number(
            "+234 801 234 5678",
        )

        self.assertEqual(
            result,
            "+2348012345678",
        )


    def test_invalid_region_code_is_rejected(self):
        with self.assertRaises(
            PhoneServiceError,
        ):
            normalize_phone_number(
                "08012345678",
                "XX",
            )

    def test_normalize_nigerian_phone_number(self):
        result = normalize_phone_number(
            "+234 801 234 5678",
        )

        self.assertEqual(
            result,
            "+2348012345678",
        )

    def test_normalize_uk_phone_number(self):
        result = normalize_phone_number(
            "+44 7911 123456",
        )

        self.assertEqual(
            result,
            "+447911123456",
        )

    def test_normalize_us_phone_number(self):
        result = normalize_phone_number(
            "+1 415 555 2671",
        )

        self.assertEqual(
            result,
            "+14155552671",
        )

    def test_normalize_indian_phone_number(self):
        result = normalize_phone_number(
            "+91 98765 43210",
        )

        self.assertEqual(
            result,
            "+919876543210",
        )

    def test_different_formatting_produces_same_number(
        self,
    ):
        first = normalize_phone_number(
            "+234 801 234 5678",
        )

        second = normalize_phone_number(
            "+234-801-234-5678",
        )

        third = normalize_phone_number(
            "+2348012345678",
        )

        self.assertEqual(
            first,
            second,
        )

        self.assertEqual(
            second,
            third,
        )

        self.assertEqual(
            first,
            "+2348012345678",
        )

    def test_invalid_phone_number_is_rejected(self):
        with self.assertRaises(
            PhoneServiceError,
        ):
            normalize_phone_number(
                "+234123",
            )

    def test_impossible_phone_number_is_rejected(self):
        with self.assertRaises(
            PhoneServiceError,
        ):
            normalize_phone_number(
                "+234999999999999999",
            )

    def test_invalid_us_phone_number_is_rejected(self):
        with self.assertRaises(
            PhoneServiceError,
        ):
            normalize_phone_number(
                "+10000000000",
            )

    def test_invalid_country_code_is_rejected(self):
        with self.assertRaises(
            PhoneServiceError,
        ):
            normalize_phone_number(
                "+999123456789",
            )

    def test_phone_number_without_plus_is_rejected(self):
        with self.assertRaises(
            PhoneServiceError,
        ):
            normalize_phone_number(
                "2348012345678",
            )

    def test_non_string_phone_number_is_rejected(self):
        with self.assertRaises(
            PhoneServiceError,
        ):
            normalize_phone_number(
                None,
            )

    

    def test_empty_phone_number_is_rejected(self):
        with self.assertRaises(
            PhoneServiceError,
        ):
            normalize_phone_number("")

    def test_phone_without_country_code_is_rejected(self):
        with self.assertRaises(
            PhoneServiceError,
        ):
            normalize_phone_number(
                "08012345678",
            )

    def test_get_verified_phone_returns_none_when_missing(self):
        result = get_verified_phone(
            user=self.user,
        )

        self.assertIsNone(
            result,
        )

    def test_request_phone_verification_creates_otp(
        self,
    ):
        with self.captureOnCommitCallbacks(
            execute=True,
        ):
            otp = request_phone_verification(
                user=self.user,
                phone_number=self.phone_number,
            )

        self.assertIsNotNone(
            otp,
        )

        self.assertEqual(
            otp.user,
            self.user,
        )

        self.assertEqual(
            otp.phone_number,
            self.phone_number,
        )

        self.assertEqual(
            otp.purpose,
            PhoneOTP.Purpose.VERIFY_PHONE,
        )

    @patch(
        "accounts.services.phone.send_sms"
    )
    def test_request_phone_verification_sends_sms(
        self,
        mock_send_sms,
    ):
        with self.captureOnCommitCallbacks(
            execute=True,
        ):
            request_phone_verification(
                user=self.user,
                phone_number=self.phone_number,
            )

        mock_send_sms.assert_called_once()

        call_kwargs = (
            mock_send_sms.call_args.kwargs
        )

        self.assertEqual(
            call_kwargs["phone_number"],
            self.phone_number,
        )

        self.assertIn(
            "verification code",
            call_kwargs["message"],
        )

    def test_request_verified_phone_is_rejected(
        self,
    ):
        UserPhone.objects.create(
            user=self.user,
            phone_number=self.phone_number,
            verified_at=timezone.now(),
        )

        with self.assertRaises(
            PhoneServiceError,
        ):
            request_phone_verification(
                user=self.user,
                phone_number=self.phone_number,
            )

    def test_phone_owned_by_another_user_is_rejected(
        self,
    ):
        other_user = User.objects.create_user(
            email="other-phone@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

        UserPhone.objects.create(
            user=other_user,
            phone_number=self.phone_number,
            verified_at=timezone.now(),
        )

        with self.assertRaises(
            PhoneServiceError,
        ):
            request_phone_verification(
                user=self.user,
                phone_number=self.phone_number,
            )

    def test_verify_phone_creates_verified_phone(
    self,
    ):
        otp, raw_code = create_phone_otp(
            user=self.user,
            phone_number=self.phone_number,
            purpose=PhoneOTP.Purpose.VERIFY_PHONE,
        )

        phone = verify_phone(
            user=self.user,
            phone_number=self.phone_number,
            code=raw_code,
        )

        self.assertIsNotNone(
            phone,
        )

        self.assertEqual(
            phone.user,
            self.user,
        )

        self.assertEqual(
            phone.phone_number,
            self.phone_number,
        )

        self.assertIsNotNone(
            phone.verified_at,
        )

        self.assertTrue(
            phone.is_verified,
        )

    def test_wrong_phone_code_does_not_create_phone(
        self,
    ):
        with self.captureOnCommitCallbacks(
            execute=True,
        ):
            request_phone_verification(
                user=self.user,
                phone_number=self.phone_number,
            )

        with self.assertRaises(
            ValueError,
        ):
            verify_phone(
                user=self.user,
                phone_number=self.phone_number,
                code="000000",
            )

        self.assertFalse(
            UserPhone.objects.filter(
                user=self.user,
            ).exists(),
        )

    def test_verified_phone_is_returned(
        self,
    ):
        phone = UserPhone.objects.create(
            user=self.user,
            phone_number=self.phone_number,
            verified_at=timezone.now(),
        )

        result = get_verified_phone(
            user=self.user,
        )

        self.assertEqual(
            result,
            phone,
        )


class PhoneChangeServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="phone-change@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

        self.current_phone = (
            "+2348012345678"
        )

        self.new_phone = (
            "+2348098765432"
        )

        UserPhone.objects.create(
            user=self.user,
            phone_number=self.current_phone,
            verified_at=timezone.now(),
        )

    def test_wrong_current_password_is_rejected(self):
        with self.assertRaises(
            PhoneServiceError,
        ):
            request_phone_change(
                user=self.user,
                current_password="WrongPassword123!",
                new_phone_number=self.new_phone,
            )

    def test_same_verified_phone_is_rejected(self):
        with self.assertRaises(
            PhoneServiceError,
        ):
            request_phone_change(
                user=self.user,
                current_password="StrongPassword123!",
                new_phone_number=self.current_phone,
            )

    def test_new_phone_request_creates_change_otp(
        self,
    ):
        with self.captureOnCommitCallbacks(
            execute=True,
        ):
            otp = request_phone_change(
                user=self.user,
                current_password="StrongPassword123!",
                new_phone_number=self.new_phone,
            )

        self.assertEqual(
            otp.user,
            self.user,
        )

        self.assertEqual(
            otp.phone_number,
            self.new_phone,
        )

        self.assertEqual(
            otp.purpose,
            PhoneOTP.Purpose.CHANGE_PHONE,
        )

    def test_new_phone_request_sends_sms(self):
        with patch(
            "accounts.services.phone.send_sms"
        ) as mock_send_sms:

            with self.captureOnCommitCallbacks(
                execute=True,
            ):
                request_phone_change(
                    user=self.user,
                    current_password="StrongPassword123!",
                    new_phone_number=self.new_phone,
                )

        mock_send_sms.assert_called_once()

        call_kwargs = (
            mock_send_sms.call_args.kwargs
        )

        self.assertEqual(
            call_kwargs["phone_number"],
            self.new_phone,
        )

        self.assertIn(
            "phone-change verification code",
            call_kwargs["message"],
        )

    def test_new_phone_owned_by_another_user_is_rejected(
        self,
    ):
        other_user = User.objects.create_user(
            email="phone-change-other@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

        UserPhone.objects.create(
            user=other_user,
            phone_number=self.new_phone,
            verified_at=timezone.now(),
        )

        with self.assertRaises(
            PhoneServiceError,
        ):
            request_phone_change(
                user=self.user,
                current_password="StrongPassword123!",
                new_phone_number=self.new_phone,
            )

    def test_failed_verification_keeps_old_phone(
        self,
    ):
        otp, raw_code = create_phone_otp(
            user=self.user,
            phone_number=self.new_phone,
            purpose=PhoneOTP.Purpose.CHANGE_PHONE,
        )

        with self.assertRaises(
            ValueError,
        ):
            verify_phone_change(
                user=self.user,
                new_phone_number=self.new_phone,
                code="000000",
            )

        phone = UserPhone.objects.get(
            user=self.user,
        )

        self.assertEqual(
            phone.phone_number,
            self.current_phone,
        )

        self.assertTrue(
            phone.is_verified,
        )

    def test_successful_verification_replaces_old_phone(
        self,
    ):
        otp, raw_code = create_phone_otp(
            user=self.user,
            phone_number=self.new_phone,
            purpose=PhoneOTP.Purpose.CHANGE_PHONE,
        )

        phone = verify_phone_change(
            user=self.user,
            new_phone_number=self.new_phone,
            code=raw_code,
        )

        self.assertEqual(
            phone.phone_number,
            self.new_phone,
        )

        self.assertTrue(
            phone.is_verified,
        )

        self.assertEqual(
            UserPhone.objects.filter(
                user=self.user,
            ).count(),
            1,
        )

    def test_old_phone_remains_until_new_phone_is_verified(
        self,
    ):
        otp, raw_code = create_phone_otp(
            user=self.user,
            phone_number=self.new_phone,
            purpose=PhoneOTP.Purpose.CHANGE_PHONE,
        )

        phone = UserPhone.objects.get(
            user=self.user,
        )

        self.assertEqual(
            phone.phone_number,
            self.current_phone,
        )

        self.assertTrue(
            phone.is_verified,
        )

    def test_new_phone_change_otp_replaces_previous_pending_otp(
        self,
    ):
        first_otp, first_code = create_phone_otp(
            user=self.user,
            phone_number=self.new_phone,
            purpose=PhoneOTP.Purpose.CHANGE_PHONE,
        )

        first_otp.created_at = (
            timezone.now()
            - PHONE_OTP_RESEND_COOLDOWN
            - timedelta(seconds=1)
        )

        first_otp.save(
            update_fields=["created_at"],
        )

        second_phone = "+2348077777777"

        second_otp, second_code = create_phone_otp(
            user=self.user,
            phone_number=second_phone,
            purpose=PhoneOTP.Purpose.CHANGE_PHONE,
        )

        first_otp.refresh_from_db()

        self.assertIsNotNone(
            first_otp.used_at,
        )

        self.assertIsNone(
            second_otp.used_at,
        )


class GoogleTokenVerificationTests(TestCase):

    @patch(
        "accounts.services.google.id_token.verify_oauth2_token"
    )
    def test_valid_google_id_token_is_verified(
        self,
        mock_verify,
    ):
        mock_verify.return_value = {
            "iss": "https://accounts.google.com",
            "aud": "test-client-id",
            "sub": "google-sub-123456789",
            "email": "google@example.com",
            "email_verified": True,
        }

        with self.settings(
            GOOGLE_CLIENT_ID="test-client-id",
        ):
            claims = verify_google_id_token(
                token="fake-google-id-token",
            )

        self.assertEqual(
            claims["sub"],
            "google-sub-123456789",
        )

        self.assertEqual(
            claims["email"],
            "google@example.com",
        )

        mock_verify.assert_called_once()

    @patch(
        "accounts.services.google.id_token.verify_oauth2_token"
    )
    def test_invalid_google_id_token_raises_error(
        self,
        mock_verify,
    ):
        mock_verify.side_effect = ValueError(
            "Invalid token"
        )

        with self.settings(
            GOOGLE_CLIENT_ID="test-client-id",
        ):
            with self.assertRaises(
                InvalidGoogleTokenError,
            ):
                verify_google_id_token(
                    token="invalid-token",
                )

    def test_missing_google_token_raises_error(self):
        with self.settings(
            GOOGLE_CLIENT_ID="test-client-id",
        ):
            with self.assertRaises(
                InvalidGoogleTokenError,
            ):
                verify_google_id_token(
                    token="",
                )

    def test_google_authentication_requires_client_id(self):
        with self.settings(
            GOOGLE_CLIENT_ID="",
        ):
            with self.assertRaises(
                InvalidGoogleTokenError,
            ):
                verify_google_id_token(
                    token="some-token",
                )

    @patch(
        "accounts.services.google.id_token.verify_oauth2_token"
    )
    def test_invalid_google_issuer_raises_error(
        self,
        mock_verify,
    ):
        mock_verify.return_value = {
            "iss": "https://malicious.example.com",
            "aud": "test-client-id",
            "sub": "google-sub-123456789",
            "email": "google@example.com",
            "email_verified": True,
        }

        with self.settings(
            GOOGLE_CLIENT_ID="test-client-id",
        ):
            with self.assertRaises(
                InvalidGoogleTokenError,
            ):
                verify_google_id_token(
                    token="fake-google-id-token",
                )

    @patch(
    "accounts.services.google.id_token.verify_oauth2_token"
    )
    def test_missing_google_subject_raises_error(
        self,
        mock_verify,
    ):
        mock_verify.return_value = {
            "iss": "https://accounts.google.com",
            "aud": "test-client-id",
            "email": "google@example.com",
            "email_verified": True,
        }

        with self.settings(
            GOOGLE_CLIENT_ID="test-client-id",
        ):
            with self.assertRaises(
                InvalidGoogleTokenError,
            ):
                verify_google_id_token(
                    token="fake-google-id-token",
                )

    @patch(
        "accounts.services.google.id_token.verify_oauth2_token"
    )
    def test_missing_google_email_raises_error(
        self,
        mock_verify,
    ):
        mock_verify.return_value = {
            "iss": "https://accounts.google.com",
            "aud": "test-client-id",
            "sub": "google-sub-123456789",
            "email_verified": True,
        }

        with self.settings(
            GOOGLE_CLIENT_ID="test-client-id",
        ):
            with self.assertRaises(
                InvalidGoogleTokenError,
            ):
                verify_google_id_token(
                    token="fake-google-id-token",
                )

    @patch(
        "accounts.services.google.id_token.verify_oauth2_token"
    )
    def test_unverified_google_email_raises_error(
        self,
        mock_verify,
    ):
        mock_verify.return_value = {
            "iss": "https://accounts.google.com",
            "aud": "test-client-id",
            "sub": "google-sub-123456789",
            "email": "google@example.com",
            "email_verified": False,
        }

        with self.settings(
            GOOGLE_CLIENT_ID="test-client-id",
        ):
            with self.assertRaises(
                InvalidGoogleTokenError,
            ):
                verify_google_id_token(
                    token="fake-google-id-token",
                )


class GoogleAccountResolutionTests(TestCase):

    def _google_claims(
        self,
        *,
        sub="google-sub-123456789",
        email="google@example.com",
        email_verified=True,
    ):
        return {
            "iss": "https://accounts.google.com",
            "aud": "test-client-id",
            "sub": sub,
            "email": email,
            "email_verified": email_verified,
        }

    def test_new_google_account_creates_user_and_identity(self):
        claims = self._google_claims()

        user = resolve_google_user(
            claims=claims,
        )

        self.assertIsNotNone(user)

        self.assertEqual(
            user.email,
            "google@example.com",
        )

        self.assertTrue(
            user.is_active,
        )

        self.assertFalse(
            user.has_usable_password(),
        )

        identity = UserIdentity.objects.get(
            provider=UserIdentity.Provider.GOOGLE,
            provider_subject="google-sub-123456789",
        )

        self.assertEqual(
            identity.user,
            user,
        )

        self.assertEqual(
            identity.email,
            "google@example.com",
        )

    def test_existing_google_identity_returns_same_user(self):
        user = User.objects.create_user(
            email="google@example.com",
            password=None,
            is_active=True,
        )

        UserIdentity.objects.create(
            user=user,
            provider=UserIdentity.Provider.GOOGLE,
            provider_subject="google-sub-123456789",
            email="google@example.com",
        )

        claims = self._google_claims()

        resolved_user = resolve_google_user(
            claims=claims,
        )

        self.assertEqual(
            resolved_user,
            user,
        )

        self.assertEqual(
            User.objects.count(),
            1,
        )

        self.assertEqual(
            UserIdentity.objects.count(),
            1,
        )

    def test_existing_email_account_is_not_automatically_linked(self):
        existing_user = User.objects.create_user(
            email="google@example.com",
            password="ExistingPassword123!",
            is_active=True,
        )

        claims = self._google_claims()

        with self.assertRaises(
            GoogleAccountError,
        ):
            resolve_google_user(
                claims=claims,
            )

        self.assertEqual(
            User.objects.count(),
            1,
        )

        self.assertEqual(
            UserIdentity.objects.count(),
            0,
        )

        self.assertTrue(
            existing_user.check_password(
                "ExistingPassword123!",
            ),
        )

    def test_existing_google_identity_for_inactive_user_is_rejected(self):
        user = User.objects.create_user(
            email="google@example.com",
            password=None,
            is_active=False,
        )

        UserIdentity.objects.create(
            user=user,
            provider=UserIdentity.Provider.GOOGLE,
            provider_subject="google-sub-123456789",
            email="google@example.com",
        )

        claims = self._google_claims()

        with self.assertRaises(
            GoogleAccountError,
        ):
            resolve_google_user(
                claims=claims,
            )

    def test_google_subject_is_required(self):
        claims = self._google_claims()

        claims.pop("sub")

        with self.assertRaises(
            GoogleAccountError,
        ):
            resolve_google_user(
                claims=claims,
            )

    def test_google_email_is_required(self):
        claims = self._google_claims()

        claims.pop("email")

        with self.assertRaises(
            GoogleAccountError,
        ):
            resolve_google_user(
                claims=claims,
            )

    def test_different_google_subject_creates_different_identity(self):
        first_user = resolve_google_user(
            claims=self._google_claims(
                sub="google-sub-111111111",
                email="first@example.com",
            ),
        )

        second_user = resolve_google_user(
            claims=self._google_claims(
                sub="google-sub-222222222",
                email="second@example.com",
            ),
        )

        self.assertNotEqual(
            first_user,
            second_user,
        )

        self.assertEqual(
            User.objects.count(),
            2,
        )

        self.assertEqual(
            UserIdentity.objects.count(),
            2,
        )


class GoogleLoginServiceTests(TestCase):

    @patch(
        "accounts.services.google.verify_google_id_token"
    )
    def test_google_login_returns_new_google_user(
        self,
        mock_verify,
    ):
        mock_verify.return_value = {
            "iss": "https://accounts.google.com",
            "aud": "test-client-id",
            "sub": "google-sub-123456789",
            "email": "google@example.com",
            "email_verified": True,
        }

        user = login_with_google(
            token="fake-google-id-token",
        )

        self.assertEqual(
            user.email,
            "google@example.com",
        )

        self.assertTrue(
            user.is_active,
        )

        self.assertEqual(
            UserIdentity.objects.count(),
            1,
        )

        mock_verify.assert_called_once_with(
            token="fake-google-id-token",
        )

    @patch(
        "accounts.services.google.verify_google_id_token"
    )
    def test_google_login_reuses_existing_google_account(
        self,
        mock_verify,
    ):
        user = User.objects.create_user(
            email="google@example.com",
            password=None,
            is_active=True,
        )

        UserIdentity.objects.create(
            user=user,
            provider=UserIdentity.Provider.GOOGLE,
            provider_subject="google-sub-123456789",
            email="google@example.com",
        )

        mock_verify.return_value = {
            "iss": "https://accounts.google.com",
            "aud": "test-client-id",
            "sub": "google-sub-123456789",
            "email": "google@example.com",
            "email_verified": True,
        }

        resolved_user = login_with_google(
            token="fake-google-id-token",
        )

        self.assertEqual(
            resolved_user,
            user,
        )

        self.assertEqual(
            User.objects.count(),
            1,
        )

        self.assertEqual(
            UserIdentity.objects.count(),
            1,
        )

    @patch(
        "accounts.services.google.verify_google_id_token"
    )
    def test_google_login_rejects_existing_email_account(
        self,
        mock_verify,
    ):
        user = User.objects.create_user(
            email="google@example.com",
            password="ExistingPassword123!",
            is_active=True,
        )

        mock_verify.return_value = {
            "iss": "https://accounts.google.com",
            "aud": "test-client-id",
            "sub": "google-sub-123456789",
            "email": "google@example.com",
            "email_verified": True,
        }

        with self.assertRaises(
            GoogleAccountError,
        ):
            login_with_google(
                token="fake-google-id-token",
            )

        self.assertEqual(
            User.objects.count(),
            1,
        )

        self.assertEqual(
            UserIdentity.objects.count(),
            0,
        )

        self.assertTrue(
            user.check_password(
                "ExistingPassword123!",
            ),
        )