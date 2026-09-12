from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.serializers.registration import RegistrationSerializer
from accounts.serializers.login import LoginSerializer


User = get_user_model()


class RegistrationSerializerTests(TestCase):
    def test_valid_registration_data(self):
        serializer = RegistrationSerializer(
            data={
                "email": "john@example.com",
                "password": "StrongPassword123!",
                "password_confirm": "StrongPassword123!",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_email_is_normalized(self):
        serializer = RegistrationSerializer(
            data={
                "email": "john@EXAMPLE.com",
                "password": "StrongPassword123!",
                "password_confirm": "StrongPassword123!",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertEqual(
            serializer.validated_data["email"],
            "john@example.com",
        )

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            email="john@example.com",
            password="StrongPassword123!",
        )

        serializer = RegistrationSerializer(
            data={
                "email": "john@example.com",
                "password": "AnotherStrongPassword123!",
                "password_confirm": "AnotherStrongPassword123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_duplicate_email_is_case_insensitive(self):
        User.objects.create_user(
            email="john@example.com",
            password="StrongPassword123!",
        )

        serializer = RegistrationSerializer(
            data={
                "email": "JOHN@EXAMPLE.COM",
                "password": "AnotherStrongPassword123!",
                "password_confirm": "AnotherStrongPassword123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_invalid_email_is_rejected(self):
        serializer = RegistrationSerializer(
            data={
                "email": "not-an-email",
                "password": "StrongPassword123!",
                "password_confirm": "StrongPassword123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_password_mismatch_is_rejected(self):
        serializer = RegistrationSerializer(
            data={
                "email": "john@example.com",
                "password": "StrongPassword123!",
                "password_confirm": "DifferentPassword123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)

    def test_weak_password_is_rejected(self):
        serializer = RegistrationSerializer(
            data={
                "email": "john@example.com",
                "password": "12345678",
                "password_confirm": "12345678",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_password_fields_are_write_only(self):
        serializer = RegistrationSerializer()

        self.assertTrue(
            serializer.fields["password"].write_only
        )

        self.assertTrue(
            serializer.fields["password_confirm"].write_only
        )



class LoginSerializerTests(TestCase):

    def test_valid_login_data(self):
        serializer = LoginSerializer(
            data={
                "email": "  JOHN@EXAMPLE.COM ",
                "password": "StrongPassword123!",
            }
        )

        self.assertTrue(serializer.is_valid())

        self.assertEqual(
            serializer.validated_data["email"],
            "john@example.com",
        )

        self.assertEqual(
            serializer.validated_data["password"],
            "StrongPassword123!",
        )

    def test_email_is_required(self):
        serializer = LoginSerializer(
            data={
                "password": "StrongPassword123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_password_is_required(self):
        serializer = LoginSerializer(
            data={
                "email": "john@example.com",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_invalid_email_is_rejected(self):
        serializer = LoginSerializer(
            data={
                "email": "not-an-email",
                "password": "StrongPassword123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_password_whitespace_is_preserved(self):
        serializer = LoginSerializer(
            data={
                "email": "john@example.com",
                "password": " password-with-spaces ",
            }
        )

        self.assertTrue(serializer.is_valid())

        self.assertEqual(
            serializer.validated_data["password"],
            " password-with-spaces ",
        )


from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from accounts.serializers.password import (
    ChangePasswordSerializer,
)


User = get_user_model()


class ChangePasswordSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="password@example.com",
            password="OldPassword123!",
        )

        self.factory = RequestFactory()

    def _request(self):
        request = self.factory.post(
            "/api/accounts/password/change/"
        )
        request.user = self.user
        return request

    def test_valid_password_change(self):
        serializer = ChangePasswordSerializer(
            data={
                "current_password": "OldPassword123!",
                "new_password": "NewPassword456!",
                "new_password_confirm": "NewPassword456!",
            },
            context={
                "request": self._request(),
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_wrong_current_password_rejected(self):
        serializer = ChangePasswordSerializer(
            data={
                "current_password": "WrongPassword123!",
                "new_password": "NewPassword456!",
                "new_password_confirm": "NewPassword456!",
            },
            context={
                "request": self._request(),
            },
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "current_password",
            serializer.errors,
        )

    def test_password_confirmation_must_match(self):
        serializer = ChangePasswordSerializer(
            data={
                "current_password": "OldPassword123!",
                "new_password": "NewPassword456!",
                "new_password_confirm": "DifferentPassword456!",
            },
            context={
                "request": self._request(),
            },
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "new_password_confirm",
            serializer.errors,
        )

    def test_new_password_cannot_equal_current_password(self):
        serializer = ChangePasswordSerializer(
            data={
                "current_password": "OldPassword123!",
                "new_password": "OldPassword123!",
                "new_password_confirm": "OldPassword123!",
            },
            context={
                "request": self._request(),
            },
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "new_password",
            serializer.errors,
        )

    def test_weak_password_rejected(self):
        serializer = ChangePasswordSerializer(
            data={
                "current_password": "OldPassword123!",
                "new_password": "password",
                "new_password_confirm": "password",
            },
            context={
                "request": self._request(),
            },
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "new_password",
            serializer.errors,
        )