from django.urls import path

from .views.registration import RegistrationView
from .views.verification import (
    EmailVerificationView,
    ResendVerificationView,
    PhoneChangeConfirmView,
    PhoneChangeRequestView,
    PhoneVerificationConfirmView,
    PhoneVerificationRequestView,
)
from .views.login import LoginView
from .views.profile import CurrentUserView
from .views.public_profile import PublicProfileView
from .views.profile_update import ProfileUpdateView
from .views.sessions import (
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
from .views.google import GoogleLoginView
from .views.onboarding import (
    DisplayNameOnboardingView,
    UsernameAvailabilityView,
    UsernameOnboardingView,
)
from .views.public_connections import PublicConnectionsView
from .views.public_profile_posts import PublicProfilePostsView
from .views.public_profile_music import PublicProfileMusicView


urlpatterns = [
    # REGISTRATION
    path(
        "accounts/register/",
        RegistrationView.as_view(),
        name="register",
    ),

    # EMAIL VERIFICATION
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

    # LOGIN
    path(
        "accounts/login/",
        LoginView.as_view(),
        name="login",
    ),

    # GOOGLE AUTHENTICATION
    path(
        "auth/google/",
        GoogleLoginView.as_view(),
        name="google-login",
    ),

    # CURRENT USER
    path(
        "accounts/me/",
        CurrentUserView.as_view(),
        name="current-user",
    ),

    # PUBLIC USER PROFILES
    path(
        "accounts/users/<str:username>/",
        PublicProfileView.as_view(),
        name="public-user-profile",
    ),

    # PUBLIC USER CONNECTIONS
    path(
        "accounts/users/<str:username>/connections/",
        PublicConnectionsView.as_view(),
        name="public-user-connections",
    ),

    # PUBLIC USER PROFILE POSTS
    path(
        "accounts/users/<str:username>/posts/",
        PublicProfilePostsView.as_view(),
        name="public-user-profile-posts",
    ),

    # PUBLIC USER PROFILE MUSIC
    path(
        "accounts/users/<str:username>/music/",
        PublicProfileMusicView.as_view(),
        name="public-user-profile-music",
    ),

    # USER PROFILE (VIEW/EDIT)
    path(
    "accounts/profile/",
    ProfileUpdateView.as_view(),
    name="profile-update",
    ),

    # ACCOUNT ONBOARDING
    path(
        "accounts/onboarding/display-name/",
        DisplayNameOnboardingView.as_view(),
        name="onboarding-display-name",
    ),
    path(
        "accounts/onboarding/username/availability/",
        UsernameAvailabilityView.as_view(),
        name="onboarding-username-availability",
    ),
    path(
        "accounts/onboarding/username/",
        UsernameOnboardingView.as_view(),
        name="onboarding-username",
    ),

    # SESSIONS
    path(
        "accounts/logout/",
        LogoutView.as_view(),
        name="logout",
    ),
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

    # PASSWORD MANAGEMENT
    path(
        "accounts/password/change/",
        ChangePasswordView.as_view(),
        name="password-change",
    ),
    path(
        "accounts/password/forgot/",
        ForgotPasswordView.as_view(),
        name="password-forgot",
    ),
    path(
        "accounts/password/reset/",
        ResetPasswordView.as_view(),
        name="password-reset",
    ),

    # EMAIL MANAGEMENT
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

    # PHONE VERIFICATION AND MANAGEMENT
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
