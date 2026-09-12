from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.core import mail
from django.http import HttpResponse

from datetime import timedelta

from accounts.services.registration import register_user
from accounts.models import (
    EmailVerificationToken,
    User,
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

from accounts.models import UserSession
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