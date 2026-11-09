from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrdinaryVibeNationUser(BasePermission):
    """
    Allows fully onboarded ordinary VibeNation users.

    Staff accounts and superusers are reserved for administration
    and cannot participate in public community activities.
    """

    message = (
        "Complete your account setup before participating "
        "in VibeNation community activities."
    )

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and not user.is_staff
            and not user.is_superuser
            and user.onboarding_completed
        )


class IsOrdinaryVibeNationUserOrReadOnly(BasePermission):
    """
    Allows public read-only access.

    Write operations require an authenticated, active,
    fully onboarded ordinary VibeNation account.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return IsOrdinaryVibeNationUser().has_permission(
            request,
            view,
        )
