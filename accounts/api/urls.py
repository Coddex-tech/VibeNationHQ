from django.urls import path

from .views.registration import RegistrationView
from .views.verification import (
    EmailVerificationView,
    ResendVerificationView,
)
from .views.login import LoginView
from .views.profile import CurrentUserView
from ..api.views.sessions import (
    LogoutView,
    SessionListView,
    SessionRevokeView,
    SessionRevokeAllOthersView, 
)
from .views.password import (
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,
)
from .views.security import (
    ChangeEmailView,
    VerifyEmailChangeView,
)
from .views.verification import (
    PhoneChangeConfirmView,
    PhoneChangeRequestView,
    PhoneVerificationConfirmView,
    PhoneVerificationRequestView,
)
from .views.google import GoogleLoginView


urlpatterns = [
    path(
        "accounts/register/",
        RegistrationView.as_view(),
        name="register",
    ),

    path(
        "accounts/verify-email/",
        EmailVerificationView.as_view(),
        name="verify-email",
    ),

    path(
        "accounts/resend-verification/",
        ResendVerificationView.as_view(),
        name="resend-verification",
    ),

    path(
        "accounts/login/",
        LoginView.as_view(),
        name="login",
    ),

    # GOOGLE AUTH
    path(
        "auth/google/",
        GoogleLoginView.as_view(),
        name="google-login",
    ),

    path(
        "accounts/me/",
        CurrentUserView.as_view(),
        name="current-user",
    ),

    path(
        "accounts/logout/",
        LogoutView.as_view(),
        name="logout",
    ),

    # View all log sessions
    path(
    "accounts/sessions/",
        SessionListView.as_view(),
        name="session-list",
    ),

    path(
        "accounts/sessions/revoke-others/",
        SessionRevokeAllOthersView.as_view(),
        name="session-revoke-others",
    ),

    path(
        "accounts/sessions/<uuid:session_id>/",
        SessionRevokeView.as_view(),
        name="session-revoke",
    ),

    # Change password
    path(
        "accounts/password/change/",
        ChangePasswordView.as_view(),
        name="password-change",
    ),

    # Forgotten password
    path(
        "accounts/password/forgot/",
        ForgotPasswordView.as_view(),
        name="password-forgot",
    ),

    # Reset Forgotten password 
    path(
        "accounts/password/reset/",
        ResetPasswordView.as_view(),
        name="password-reset",
    ),

    # Change Gmail
    path(
        "accounts/email/change/",
        ChangeEmailView.as_view(),
        name="email-change",
    ),

    path(
        "accounts/email/change/verify/",
        VerifyEmailChangeView.as_view(),
        name="email-change-verify",
    ),

    # Add and Change phone number
    path(
        "phone/add/",
        PhoneVerificationRequestView.as_view(),
        name="phone-add",
    ),

    path(
        "phone/add/verify/",
        PhoneVerificationConfirmView.as_view(),
        name="phone-add-verify",
    ),

    path(
        "phone/change/",
        PhoneChangeRequestView.as_view(),
        name="phone-change",
    ),

    path(
        "phone/change/verify/",
        PhoneChangeConfirmView.as_view(),
        name="phone-change-verify",
    ),
]