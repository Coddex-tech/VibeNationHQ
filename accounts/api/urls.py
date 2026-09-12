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
)
from .views.password import ChangePasswordView


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
]