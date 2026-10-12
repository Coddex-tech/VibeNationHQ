from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.timezone import now

from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)

from .models import (
    EmailChangeToken,
    EmailVerificationToken,
    PasswordResetToken,
    PhoneOTP,
    StaffAccount,
    UserIdentity,
    UserPhone,
    UserSession,
    VibeNationUser,
)


# ============================================================
# VIBENATION USER ADMIN
# ============================================================


class VibeNationUserAdmin(
    BaseUserAdmin,
    UnfoldModelAdmin,
):
    """
    Administration for normal VibeNation platform users.

    Staff and superuser accounts are intentionally excluded
    from this admin.
    """

    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    def has_add_permission(self, request):
        """
        VibeNation users must register through the platform's
        authentication system, not through Django admin.
        """

        return False

    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
        "date_joined",
        "last_login",
    )

    list_filter = (
        "is_active",
        "date_joined",
        "last_login",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
    )

    ordering = (
        "-date_joined",
    )

    readonly_fields = (
        "date_joined",
        "last_login",
        "updated_at",
    )

    fieldsets = (
        (
            "Account Information",
            {
                "fields": (
                    "email",
                    "password",
                ),
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                ),
            },
        ),
        (
            "Account Status",
            {
                "fields": (
                    "is_active",
                ),
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "updated_at",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        """
        Only show normal VibeNation users.

        Staff and superusers are excluded.
        """

        queryset = super().get_queryset(request)

        return queryset.filter(
            is_staff=False,
            is_superuser=False,
        )

    def get_form(
        self,
        request,
        obj=None,
        **kwargs,
    ):
        form = super().get_form(
            request,
            obj,
            **kwargs,
        )

        if "password" in form.base_fields:
            form.base_fields["password"].help_text = (
                "Raw passwords are not stored. "
                "Use the password change form to "
                "set a new password."
            )

        return form

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        """
        Prevent staff accounts from being edited through
        the VibeNation Users section.
        """

        if obj is not None:
            if obj.is_staff or obj.is_superuser:
                return False

        return super().has_change_permission(
            request,
            obj,
        )

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        """
        Prevent accidental deletion of staff accounts
        from the normal user section.
        """

        if obj is not None:
            if obj.is_staff or obj.is_superuser:
                return False

        return super().has_delete_permission(
            request,
            obj,
        )


# ============================================================
# STAFF ACCOUNT ADMIN
# ============================================================


class StaffAccountAdmin(
    BaseUserAdmin,
    UnfoldModelAdmin,
):
    """
    Administration for VibeNationHQ staff accounts.

    Normal VibeNation users are intentionally excluded.
    """

    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    list_display = (
        "email",
        "first_name",
        "last_name",
        "staff_status",
        "is_active",
        "last_login",
    )

    list_filter = (
        "is_active",
        "is_superuser",
        "groups",
        "last_login",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
    )

    ordering = (
        "email",
    )

    readonly_fields = (
        "date_joined",
        "last_login",
        "updated_at",
        "is_superuser",
    )

    fieldsets = (
        (
            "Staff Account",
            {
                "fields": (
                    "email",
                    "password",
                ),
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                ),
            },
        ),
        (
            "Staff Access",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "updated_at",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        """
        Only show staff accounts.

        Normal VibeNation users are excluded.
        """

        queryset = super().get_queryset(request)

        return queryset.filter(
            is_staff=True,
        )

    @admin.display(
        description="Account Type",
    )
    def staff_status(self, obj):
        if obj.is_superuser:
            return "Superuser"

        return "Staff"

    def get_form(
        self,
        request,
        obj=None,
        **kwargs,
    ):
        form = super().get_form(
            request,
            obj,
            **kwargs,
        )

        if "password" in form.base_fields:
            form.base_fields["password"].help_text = (
                "Raw passwords are not stored. "
                "Use the password change form to "
                "set a new password."
            )

        return form

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        """
        Only superusers may delete staff accounts.
        """

        return request.user.is_superuser

    def save_model(
        self,
        request,
        obj,
        form,
        change,
    ):
        """
        Ensure accounts created through Staff Accounts
        are staff accounts.
        """

        if not change:
            obj.is_staff = True

        super().save_model(
            request,
            obj,
            form,
            change,
        )


# ============================================================
# USER IDENTITY ADMIN
# ============================================================


class UserIdentityAdmin(
    UnfoldModelAdmin,
):
    """
    External authentication identities.

    Example:
        Google → provider_subject
    """

    list_display = (
        "user",
        "provider",
        "email",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "provider",
        "created_at",
    )

    search_fields = (
        "user__email",
        "email",
        "provider_subject",
    )

    readonly_fields = (
        "user",
        "provider",
        "provider_subject",
        "email",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return request.user.is_superuser


# ============================================================
# USER SESSION ADMIN
# ============================================================


class UserSessionAdmin(
    UnfoldModelAdmin,
):
    """
    Authenticated VibeNationHQ sessions.

    Session secrets are stored only as hashes and are never
    editable through the admin.
    """

    list_display = (
        "user",
        "device_name",
        "ip_address",
        "created_at",
        "last_seen_at",
        "expires_at",
        "session_status",
    )

    list_filter = (
        "revoked_at",
        "created_at",
        "expires_at",
    )

    search_fields = (
        "user__email",
        "device_name",
        "ip_address",
        "user_agent",
    )

    readonly_fields = (
        "id",
        "user",
        "session_key_hash",
        "device_name",
        "user_agent",
        "ip_address",
        "created_at",
        "last_seen_at",
        "expires_at",
        "revoked_at",
    )

    ordering = (
        "-last_seen_at",
    )

    @admin.display(
        description="Status",
    )
    def session_status(self, obj):
        if obj.revoked_at is not None:
            return "Revoked"

        if now() >= obj.expires_at:
            return "Expired"

        return "Active"

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return request.user.is_superuser

    @admin.action(
        description="Revoke selected sessions",
    )
    def revoke_sessions(
        self,
        request,
        queryset,
    ):
        updated = queryset.filter(
            revoked_at__isnull=True,
        ).update(
            revoked_at=now(),
        )

        self.message_user(
            request,
            f"{updated} session(s) revoked.",
        )

    actions = (
        "revoke_sessions",
    )


# ============================================================
# USER PHONE ADMIN
# ============================================================


class UserPhoneAdmin(
    UnfoldModelAdmin,
):
    """
    User phone-number administration.

    Phone verification is controlled by the application,
    not manually edited through the admin.
    """

    list_display = (
        "user",
        "phone_number",
        "verification_status",
        "verified_at",
        "created_at",
    )

    list_filter = (
        "verified_at",
        "created_at",
    )

    search_fields = (
        "user__email",
        "phone_number",
    )

    readonly_fields = (
        "user",
        "phone_number",
        "verified_at",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    @admin.display(
        description="Verified",
        boolean=True,
    )
    def verification_status(self, obj):
        return obj.is_verified

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return request.user.is_superuser


# ============================================================
# PHONE OTP ADMIN
# ============================================================


class PhoneOTPAdmin(
    UnfoldModelAdmin,
):
    """
    Phone OTP audit administration.

    OTP codes are never stored in plaintext.
    """

    list_display = (
        "user",
        "phone_number",
        "purpose",
        "created_at",
        "expires_at",
        "attempts",
        "max_attempts",
        "otp_status",
        "used_at",
    )

    list_filter = (
        "purpose",
        "used_at",
        "created_at",
        "expires_at",
    )

    search_fields = (
        "user__email",
        "phone_number",
    )

    readonly_fields = (
        "user",
        "phone_number",
        "purpose",
        "code_hash",
        "expires_at",
        "attempts",
        "max_attempts",
        "created_at",
        "used_at",
    )

    ordering = (
        "-created_at",
    )

    @admin.display(
        description="Status",
    )
    def otp_status(self, obj):
        if obj.is_used:
            return "Used"

        if obj.is_expired:
            return "Expired"

        if obj.attempts_exhausted:
            return "Attempts exhausted"

        return "Active"

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return request.user.is_superuser


# ============================================================
# EMAIL VERIFICATION TOKEN ADMIN
# ============================================================


class EmailVerificationTokenAdmin(
    UnfoldModelAdmin,
):
    """
    Email verification token audit administration.
    """

    list_display = (
        "user",
        "created_at",
        "expires_at",
        "token_status",
        "used_at",
    )

    list_filter = (
        "used_at",
        "created_at",
        "expires_at",
    )

    search_fields = (
        "user__email",
    )

    readonly_fields = (
        "user",
        "token_hash",
        "expires_at",
        "created_at",
        "used_at",
    )

    ordering = (
        "-created_at",
    )

    @admin.display(
        description="Status",
    )
    def token_status(self, obj):
        if obj.is_used:
            return "Used"

        if obj.is_expired:
            return "Expired"

        return "Active"

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return request.user.is_superuser


# ============================================================
# PASSWORD RESET TOKEN ADMIN
# ============================================================


class PasswordResetTokenAdmin(
    UnfoldModelAdmin,
):
    """
    Password reset token audit administration.
    """

    list_display = (
        "user",
        "created_at",
        "expires_at",
        "token_status",
        "used_at",
    )

    list_filter = (
        "used_at",
        "created_at",
        "expires_at",
    )

    search_fields = (
        "user__email",
    )

    readonly_fields = (
        "user",
        "token_hash",
        "expires_at",
        "created_at",
        "used_at",
    )

    ordering = (
        "-created_at",
    )

    @admin.display(
        description="Status",
    )
    def token_status(self, obj):
        if obj.is_used:
            return "Used"

        if obj.is_expired:
            return "Expired"

        return "Active"

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return request.user.is_superuser


# ============================================================
# EMAIL CHANGE TOKEN ADMIN
# ============================================================


class EmailChangeTokenAdmin(
    UnfoldModelAdmin,
):
    """
    Email-change token audit administration.
    """

    list_display = (
        "user",
        "new_email",
        "created_at",
        "expires_at",
        "token_status",
        "used_at",
    )

    list_filter = (
        "used_at",
        "created_at",
        "expires_at",
    )

    search_fields = (
        "user__email",
        "new_email",
    )

    readonly_fields = (
        "user",
        "new_email",
        "token_hash",
        "expires_at",
        "created_at",
        "used_at",
    )

    ordering = (
        "-created_at",
    )

    @admin.display(
        description="Status",
    )
    def token_status(self, obj):
        if obj.is_used:
            return "Used"

        if obj.is_expired:
            return "Expired"

        return "Active"

    def has_add_permission(
        self,
        request,
    ):
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return request.user.is_superuser