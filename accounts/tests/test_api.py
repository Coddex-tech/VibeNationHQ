from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core import mail
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.exceptions import AuthenticationFailed

from datetime import  timedelta
from accounts.models import User
from accounts.services.verification import (
    VERIFICATION_RESEND_COOLDOWN,
    create_email_verification_token,
)
from accounts.authentications import (
    AUTH_COOKIE_NAME,
    VibeNationSessionAuthentication,
)
from accounts.services.sessions import (
    create_session,
    revoke_session,
)

User = get_user_model()


class RegistrationAPITests(APITestCase):
    url = reverse("register")

    def test_successful_registration(self):
        response = self.client.post(
            self.url,
            {
                "email": "john@example.com",
                "password": "StrongPassword123!",
                "password_confirm": "StrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            User.objects.count(),
            1,
        )

        user = User.objects.get(
            email="john@example.com",
        )

        self.assertEqual(
            user.username,
            "john",
        )

        self.assertFalse(
            user.is_active,
        )

    def test_response_contains_safe_user_data(self):
        response = self.client.post(
            self.url,
            {
                "email": "john@example.com",
                "password": "StrongPassword123!",
                "password_confirm": "StrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertIn(
            "message",
            response.data,
        )

        self.assertIn(
            "user",
            response.data,
        )

        self.assertEqual(
            response.data["user"]["email"],
            "john@example.com",
        )

        self.assertEqual(
            response.data["user"]["username"],
            "john",
        )

        self.assertNotIn(
            "password",
            response.data,
        )

        self.assertNotIn(
            "password_confirm",
            response.data,
        )

    def test_duplicate_email_returns_400(self):
        User.objects.create_user(
            email="john@example.com",
            password="StrongPassword123!",
        )

        response = self.client.post(
            self.url,
            {
                "email": "john@example.com",
                "password": "AnotherStrongPassword123!",
                "password_confirm": "AnotherStrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "email",
            response.data,
        )

    def test_password_mismatch_returns_400(self):
        response = self.client.post(
            self.url,
            {
                "email": "john@example.com",
                "password": "StrongPassword123!",
                "password_confirm": "DifferentPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "password_confirm",
            response.data,
        )

    def test_weak_password_returns_400(self):
        response = self.client.post(
            self.url,
            {
                "email": "john@example.com",
                "password": "12345678",
                "password_confirm": "12345678",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "password",
            response.data,
        )

    def test_invalid_email_returns_400(self):
        response = self.client.post(
            self.url,
            {
                "email": "not-an-email",
                "password": "StrongPassword123!",
                "password_confirm": "StrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "email",
            response.data,
        )

    def test_registration_requires_no_authentication(self):
        response = self.client.post(
            self.url,
            {
                "email": "john@example.com",
                "password": "StrongPassword123!",
                "password_confirm": "StrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_successful_registration_sends_verification_email(self):
        response = self.client.post(
            self.url,
            {
                "email": "john@example.com",
                "password": "StrongPassword123!",
                "password_confirm": "StrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        self.assertEqual(
            mail.outbox[0].to,
            ["john@example.com"],
        )

        self.assertIn(
            "http://localhost:3000/verify-email?token=",
            mail.outbox[0].body,
        )


class EmailVerificationAPITests(APITestCase):
    url = reverse("verify-email")

    def setUp(self):
        cache.clear()
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

    def test_valid_token_verifies_email(self):
        response = self.client.post(
            self.url,
            {
                "token": self.raw_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.is_active
        )

        self.assertEqual(
            response.data["user"]["email"],
            "john@example.com",
        )

    def test_invalid_token_returns_400(self):
        response = self.client.post(
            self.url,
            {
                "token": "invalid-token",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_used_token_returns_400(self):
        self.client.post(
            self.url,
            {
                "token": self.raw_token,
            },
            format="json",
        )

        response = self.client.post(
            self.url,
            {
                "token": self.raw_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_expired_token_returns_400(self):
        self.verification_token.expires_at = (
            timezone.now() - timedelta(minutes=1)
        )

        self.verification_token.save(
            update_fields=["expires_at"]
        )

        response = self.client.post(
            self.url,
            {
                "token": self.raw_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertFalse(
            self.user.is_active
        )

    def test_missing_token_returns_400(self):
        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "token",
            response.data,
        )

    def test_verification_requires_no_authentication(self):
        response = self.client.post(
            self.url,
            {
                "token": self.raw_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )


class ResendVerificationAPITests(APITestCase):
    url = reverse("resend-verification")

    def setUp(self):
        cache.clear()

        self.user = User.objects.create_user(
            email="john@example.com",
            password="StrongPassword123!",
            is_active=False,
        )

        self.verification_token, _ = (
            create_email_verification_token(
                self.user
            )
        )

        self.url = reverse("resend-verification")

    def test_existing_unverified_account_returns_200(self):
        response = self.client.post(
            self.url,
            {
                "email": "john@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_unknown_email_returns_200(self):
        response = self.client.post(
            self.url,
            {
                "email": "unknown@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_existing_and_unknown_email_have_same_response(self):
        existing_response = self.client.post(
            self.url,
            {
                "email": "john@example.com",
            },
            format="json",
        )

        unknown_response = self.client.post(
            self.url,
            {
                "email": "unknown@example.com",
            },
            format="json",
        )

        self.assertEqual(
            existing_response.data,
            unknown_response.data,
        )

    def test_missing_email_returns_400(self):
        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "email",
            response.data,
        )

    def test_resend_sends_email_for_existing_account(self):
        self.verification_token.created_at = (
            timezone.now()
            - VERIFICATION_RESEND_COOLDOWN
            - timedelta(seconds=1)
        )

        self.verification_token.save(
            update_fields=["created_at"]
        )

        response = self.client.post(
            self.url,
            {
                "email": "john@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

    def test_resend_does_not_send_email_for_unknown_account(self):
        self.client.post(
            self.url,
            {
                "email": "unknown@example.com",
            },
            format="json",
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )

    def test_resend_verification_is_throttled(self):
        for _ in range(5):
            response = self.client.post(
                self.url,
                {
                    "email": "unknown@example.com",
                },
                format="json",
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
            )

        response = self.client.post(
            self.url,
            {
                "email": "unknown@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )


class LoginAPITests(TestCase):

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

        self.url = reverse("login")

    def test_valid_login_returns_200(self):
        response = self.client.post(
            self.url,
            {
                "email": "john@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["message"],
            "Login successful.",
        )

        self.assertEqual(
            response.data["user"]["email"],
            "john@example.com",
        )

    def test_wrong_password_returns_401(self):
        response = self.client.post(
            self.url,
            {
                "email": "john@example.com",
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertEqual(
            response.data["detail"],
            "Invalid email or password.",
        )

    def test_unknown_email_returns_401(self):
        response = self.client.post(
            self.url,
            {
                "email": "unknown@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertEqual(
            response.data["detail"],
            "Invalid email or password.",
        )

    def test_inactive_account_returns_403(self):
        response = self.client.post(
            self.url,
            {
                "email": "inactive@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(
            response.data["detail"],
            "Please verify your email before signing in.",
        )

    def test_login_does_not_return_password(self):
        response = self.client.post(
            self.url,
            {
                "email": "john@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertNotIn(
            "password",
            response.data,
        )

    def test_successful_login_creates_session(self):
        response = self.client.post(
            self.url,
            {
                "email": self.active_user.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            self.active_user.sessions.count(),
            1,
        )


    def test_successful_login_sets_session_cookie(self):
        response = self.client.post(
            self.url,
            {
                "email": self.active_user.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "vibenation_session",
            response.cookies,
        )


    def test_successful_login_cookie_is_httponly(self):
        response = self.client.post(
            self.url,
            {
                "email": self.active_user.email,
                "password": self.password,
            },
            format="json",
        )

        cookie = response.cookies["vibenation_session"]

        self.assertTrue(
            cookie["httponly"]
        )


    def test_successful_login_cookie_is_samesite_lax(self):
        response = self.client.post(
            self.url,
            {
                "email": self.active_user.email,
                "password": self.password,
            },
            format="json",
        )

        cookie = response.cookies["vibenation_session"]

        self.assertEqual(
            cookie["samesite"],
            "Lax",
        )


    def test_successful_login_does_not_return_session_secret(self):
        response = self.client.post(
            self.url,
            {
                "email": self.active_user.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        response_data = response.json()

        self.assertNotIn(
            "session",
            response_data,
        )

        self.assertNotIn(
            "token",
            response_data,
        )

        self.assertNotIn(
            "secret",
            response_data,
        )


class WebSessionAuthenticationTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        self.user = User.objects.create_user(
            email="auth@example.com",
            password="StrongPassword123!",
            is_active=True,
        )

        self.authentication = (
            VibeNationSessionAuthentication()
        )

    def test_missing_cookie_returns_none(self):
        request = self.factory.get(
            "/api/accounts/me/"
        )

        result = self.authentication.authenticate(
            request
        )

        self.assertIsNone(result)

    def test_valid_cookie_authenticates_user(self):
        session, raw_secret = create_session(
            user=self.user,
        )

        request = self.factory.get(
            "/api/accounts/me/",
        )

        request.COOKIES[AUTH_COOKIE_NAME] = (
            raw_secret
        )

        result = self.authentication.authenticate(
            request
        )

        authenticated_user, auth_session = result

        self.assertEqual(
            authenticated_user,
            self.user,
        )

        self.assertEqual(
            auth_session,
            session,
        )

    def test_invalid_cookie_raises_authentication_failed(
        self,
    ):
        request = self.factory.get(
            "/api/accounts/me/",
        )

        request.COOKIES[AUTH_COOKIE_NAME] = (
            "completely-invalid-session-secret"
        )

        with self.assertRaises(
            AuthenticationFailed
        ):
            self.authentication.authenticate(
                request
            )

    def test_revoked_session_raises_authentication_failed(
        self,
    ):
        session, raw_secret = create_session(
            user=self.user,
        )

        session.revoked_at = timezone.now()

        session.save(
            update_fields=["revoked_at"]
        )

        request = self.factory.get(
            "/api/accounts/me/",
        )

        request.COOKIES[AUTH_COOKIE_NAME] = (
            raw_secret
        )

        with self.assertRaises(
            AuthenticationFailed
        ):
            self.authentication.authenticate(
                request
            )

    def test_expired_session_raises_authentication_failed(
        self,
    ):
        session, raw_secret = create_session(
            user=self.user,
        )

        session.expires_at = (
            timezone.now() - timedelta(seconds=1)
        )

        session.save(
            update_fields=["expires_at"]
        )

        request = self.factory.get(
            "/api/accounts/me/",
        )

        request.COOKIES[AUTH_COOKIE_NAME] = (
            raw_secret
        )

        with self.assertRaises(
            AuthenticationFailed
        ):
            self.authentication.authenticate(
                request
            )

    def test_inactive_user_cannot_authenticate(
        self,
    ):
        session, raw_secret = create_session(
            user=self.user,
        )

        self.user.is_active = False

        self.user.save(
            update_fields=["is_active"]
        )

        request = self.factory.get(
            "/api/accounts/me/",
        )

        request.COOKIES[AUTH_COOKIE_NAME] = (
            raw_secret
        )

        with self.assertRaises(
            AuthenticationFailed
        ):
            self.authentication.authenticate(
                request
            )


class CurrentUserAPITests(TestCase):

    def setUp(self):
        self.password = "StrongPassword123!"

        self.user = User.objects.create_user(
            email="me@example.com",
            password=self.password,
            is_active=True,
        )

        self.url = reverse("current-user")

    def test_authenticated_user_can_access_me(self):
        session, raw_secret = create_session(
            user=self.user,
        )

        self.client.cookies[AUTH_COOKIE_NAME] = (
            raw_secret
        )

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()["user"]["email"],
            self.user.email,
        )

        self.assertEqual(
            response.json()["user"]["id"],
            self.user.id,
        )

    def test_unauthenticated_user_cannot_access_me(self):
        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_invalid_session_cannot_access_me(self):
        self.client.cookies[AUTH_COOKIE_NAME] = (
            "invalid-session-secret"
        )

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_revoked_session_cannot_access_me(self):
        session, raw_secret = create_session(
            user=self.user,
        )

        revoke_session(
            raw_secret=raw_secret,
        )

        self.client.cookies[AUTH_COOKIE_NAME] = (
            raw_secret
        )

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_expired_session_cannot_access_me(self):
        session, raw_secret = create_session(
            user=self.user,
        )

        session.expires_at = (
            timezone.now()
            - timedelta(seconds=1)
        )

        session.save(
            update_fields=["expires_at"],
        )

        self.client.cookies[AUTH_COOKIE_NAME] = (
            raw_secret
        )

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            401,
        )


class LogoutAPITests(TestCase):

    def setUp(self):
        self.password = "StrongPassword123!"

        self.user = User.objects.create_user(
            email="logout@example.com",
            password=self.password,
            is_active=True,
        )

        self.url = reverse("logout")

    def test_logout_revokes_current_session(self):
        session, raw_secret = create_session(
            user=self.user,
        )

        self.client.cookies[AUTH_COOKIE_NAME] = (
            raw_secret
        )

        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        session.refresh_from_db()

        self.assertIsNotNone(
            session.revoked_at
        )

    def test_logout_deletes_cookie(self):
        session, raw_secret = create_session(
            user=self.user,
        )

        self.client.cookies[AUTH_COOKIE_NAME] = (
            raw_secret
        )

        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            AUTH_COOKIE_NAME,
            response.cookies,
        )

        cookie = response.cookies[
            AUTH_COOKIE_NAME
        ]

        self.assertEqual(
            cookie["max-age"],
            0,
        )

    def test_logout_without_cookie_is_successful(self):
        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()["message"],
            "Logout successful.",
        )

    def test_logout_with_invalid_cookie_is_successful(
        self,
    ):
        self.client.cookies[AUTH_COOKIE_NAME] = (
            "invalid-session-secret"
        )

        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()["message"],
            "Logout successful.",
        )

    def test_logout_does_not_revoke_other_sessions(
        self,
    ):
        first_session, first_secret = (
            create_session(
                user=self.user,
            )
        )

        second_session, second_secret = (
            create_session(
                user=self.user,
            )
        )

        self.client.cookies[AUTH_COOKIE_NAME] = (
            first_secret
        )

        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        first_session.refresh_from_db()
        second_session.refresh_from_db()

        self.assertIsNotNone(
            first_session.revoked_at
        )

        self.assertIsNone(
            second_session.revoked_at
        )

    def test_logout_revoked_session_is_still_successful(
        self,
    ):
        session, raw_secret = create_session(
            user=self.user,
        )

        revoke_session(
            raw_secret=raw_secret,
        )

        self.client.cookies[AUTH_COOKIE_NAME] = (
            raw_secret
        )

        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        session.refresh_from_db()

        self.assertIsNotNone(
            session.revoked_at
        )

    def test_logged_out_session_cannot_access_me(self):
        session, raw_secret = create_session(
            user=self.user,
        )

        self.client.cookies[AUTH_COOKIE_NAME] = (
            raw_secret
        )

        logout_response = self.client.post(
            self.url,
        )

        self.assertEqual(
            logout_response.status_code,
            200,
        )

        me_response = self.client.get(
            reverse("current-user"),
        )

        self.assertEqual(
            me_response.status_code,
            401,
        )


class SessionListAPITests(TestCase):

    def setUp(self):
        self.password = "StrongPassword123!"

        self.user = User.objects.create_user(
            email="sessions@example.com",
            password=self.password,
            is_active=True,
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            password=self.password,
            is_active=True,
        )

        self.url = reverse(
            "session-list"
        )

    def test_authenticated_user_can_list_sessions(
        self,
    ):
        session, raw_secret = create_session(
            user=self.user,
        )

        self.client.cookies[
            AUTH_COOKIE_NAME
        ] = raw_secret

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.json()["sessions"]),
            1,
        )

    def test_current_session_is_marked_current(
        self,
    ):
        session, raw_secret = create_session(
            user=self.user,
        )

        self.client.cookies[
            AUTH_COOKIE_NAME
        ] = raw_secret

        response = self.client.get(
            self.url,
        )

        sessions = response.json()["sessions"]

        self.assertTrue(
            sessions[0]["is_current"]
        )

    def test_other_sessions_are_marked_not_current(
        self,
    ):
        first_session, first_secret = (
            create_session(
                user=self.user,
            )
        )

        second_session, second_secret = (
            create_session(
                user=self.user,
            )
        )

        self.client.cookies[
            AUTH_COOKIE_NAME
        ] = first_secret

        response = self.client.get(
            self.url,
        )

        sessions = response.json()["sessions"]

        self.assertEqual(
            len(sessions),
            2,
        )

        current_sessions = [
            item
            for item in sessions
            if item["is_current"]
        ]

        self.assertEqual(
            len(current_sessions),
            1,
        )

        self.assertEqual(
            current_sessions[0]["id"],
            str(first_session.id),
        )

    def test_revoked_sessions_are_not_listed(
        self,
    ):
        active_session, active_secret = (
            create_session(
                user=self.user,
            )
        )

        revoked_session, revoked_secret = (
            create_session(
                user=self.user,
            )
        )

        revoke_session(
            raw_secret=revoked_secret,
        )

        self.client.cookies[
            AUTH_COOKIE_NAME
        ] = active_secret

        response = self.client.get(
            self.url,
        )

        sessions = response.json()["sessions"]

        self.assertEqual(
            len(sessions),
            1,
        )

        self.assertEqual(
            sessions[0]["id"],
            str(active_session.id),
        )

    def test_expired_sessions_are_not_listed(
        self,
    ):
        active_session, active_secret = (
            create_session(
                user=self.user,
            )
        )

        expired_session, expired_secret = (
            create_session(
                user=self.user,
            )
        )

        expired_session.expires_at = (
            timezone.now()
            - timedelta(seconds=1)
        )

        expired_session.save(
            update_fields=["expires_at"],
        )

        self.client.cookies[
            AUTH_COOKIE_NAME
        ] = active_secret

        response = self.client.get(
            self.url,
        )

        sessions = response.json()["sessions"]

        self.assertEqual(
            len(sessions),
            1,
        )

        self.assertEqual(
            sessions[0]["id"],
            str(active_session.id),
        )

    def test_sessions_from_other_users_are_not_listed(
        self,
    ):
        user_session, user_secret = (
            create_session(
                user=self.user,
            )
        )

        other_session, other_secret = (
            create_session(
                user=self.other_user,
            )
        )

        self.client.cookies[
            AUTH_COOKIE_NAME
        ] = user_secret

        response = self.client.get(
            self.url,
        )

        sessions = response.json()["sessions"]

        self.assertEqual(
            len(sessions),
            1,
        )

        self.assertEqual(
            sessions[0]["id"],
            str(user_session.id),
        )

    def test_unauthenticated_user_cannot_list_sessions(
        self,
    ):
        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            401,
        )



class SessionRevokeAPITests(TestCase):

    def setUp(self):
        self.password = "StrongPassword123!"

        self.user = User.objects.create_user(
            email="revoke@example.com",
            password=self.password,
            is_active=True,
        )

        self.other_user = User.objects.create_user(
            email="other-revoke@example.com",
            password=self.password,
            is_active=True,
        )

        self.session, self.raw_secret = (
            create_session(
                user=self.user,
            )
        )

        self.url = reverse(
            "session-revoke",
            kwargs={
                "session_id": self.session.id,
            },
        )

        self.client.cookies[
            AUTH_COOKIE_NAME
        ] = self.raw_secret

    def test_user_can_revoke_own_session(self):
        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.session.refresh_from_db()

        self.assertIsNotNone(
            self.session.revoked_at,
        )

    def test_revoked_session_cannot_authenticate(self):
        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        me_response = self.client.get(
            reverse("current-user"),
        )

        self.assertEqual(
            me_response.status_code,
            401,
        )

    def test_user_cannot_revoke_another_users_session(
        self,
    ):
        other_session, other_secret = (
            create_session(
                user=self.other_user,
            )
        )

        url = reverse(
            "session-revoke",
            kwargs={
                "session_id": other_session.id,
            },
        )

        response = self.client.delete(
            url,
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        other_session.refresh_from_db()

        self.assertIsNone(
            other_session.revoked_at,
        )

    def test_unauthenticated_user_cannot_revoke_session(
        self,
    ):
        self.client.cookies.clear()

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.session.refresh_from_db()

        self.assertIsNone(
            self.session.revoked_at,
        )

    def test_revoked_session_cannot_revoke_session(
        self,
    ):
        revoke_session(
            raw_secret=self.raw_secret,
        )

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.session.refresh_from_db()

        self.assertIsNotNone(
            self.session.revoked_at,
        )

    def test_invalid_session_id_returns_not_found(self):
        url = (
            "/api/accounts/sessions/"
            "00000000-0000-0000-0000-000000000000/"
        )

        response = self.client.delete(
            url,
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_authenticated_user_can_change_password(self):
        response = self.client.post(
            "/api/accounts/password/change/",
            {
                "current_password": self.password,
                "new_password": "NewPassword456!",
                "new_password_confirm": "NewPassword456!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "NewPassword456!"
            )
        )

        self.assertEqual(
            response.data["message"],
            "Password changed successfully.",
        )

    def test_change_password_requires_authentication(self):
        self.client.cookies.clear()

        response = self.client.post(
            "/api/accounts/password/change/",
            {
                "current_password": self.password,
                "new_password": "NewPassword456!",
                "new_password_confirm": "NewPassword456!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_wrong_current_password_is_rejected(self):
        response = self.client.post(
            "/api/accounts/password/change/",
            {
                "current_password": "WrongPassword123!",
                "new_password": "NewPassword456!",
                "new_password_confirm": "NewPassword456!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "current_password",
            response.data,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                self.password
            )
        )

    def test_password_confirmation_must_match(self):
        response = self.client.post(
            "/api/accounts/password/change/",
            {
                "current_password": self.password,
                "new_password": "NewPassword456!",
                "new_password_confirm": "DifferentPassword456!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "new_password_confirm",
            response.data,
        )

    def test_new_password_cannot_equal_current_password(self):
        response = self.client.post(
            "/api/accounts/password/change/",
            {
                "current_password": self.password,
                "new_password": self.password,
                "new_password_confirm": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "new_password",
            response.data,
        )

    def test_weak_new_password_is_rejected(self):
        response = self.client.post(
            "/api/accounts/password/change/",
            {
                "current_password": self.password,
                "new_password": "password",
                "new_password_confirm": "password",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "new_password",
            response.data,
        )

    def test_current_session_remains_valid_after_password_change(
        self,
    ):
        response = self.client.post(
            "/api/accounts/password/change/",
            {
                "current_password": self.password,
                "new_password": "NewPassword456!",
                "new_password_confirm": "NewPassword456!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        response = self.client.get(
            "/api/accounts/me/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_other_sessions_are_revoked_after_password_change(
        self,
    ):
        other_session, _ = create_session(
            user=self.user,
            device_name="Other device",
        )

        response = self.client.post(
            "/api/accounts/password/change/",
            {
                "current_password": self.password,
                "new_password": "NewPassword456!",
                "new_password_confirm": "NewPassword456!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        other_session.refresh_from_db()

        self.assertIsNotNone(
            other_session.revoked_at,
        )

    def test_other_user_sessions_are_not_revoked(
        self,
    ):
        other_user = User.objects.create_user(
            email="other@example.com",
            password="OtherPassword123!",
            is_active=True,
        )

        other_session, _ = create_session(
            user=other_user,
            device_name="Other user device",
        )

        response = self.client.post(
            "/api/accounts/password/change/",
            {
                "current_password": self.password,
                "new_password": "NewPassword456!",
                "new_password_confirm": "NewPassword456!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        other_session.refresh_from_db()

        self.assertIsNone(
            other_session.revoked_at,
        )

    def test_password_change_does_not_return_password(
        self,
    ):
        response = self.client.post(
            "/api/accounts/password/change/",
            {
                "current_password": self.password,
                "new_password": "NewPassword456!",
                "new_password_confirm": "NewPassword456!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertNotIn(
            "password",
            response.data,
        )

        self.assertNotIn(
            "current_password",
            response.data,
        )

        self.assertNotIn(
            "new_password",
            response.data,
        )