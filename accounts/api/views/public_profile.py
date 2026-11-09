from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import AllowAny

from ...authentications import VibeNationSessionAuthentication
from ...serializers.public_profile import PublicProfileSerializer


User = get_user_model()


class PublicProfileView(generics.RetrieveAPIView):
    """
    Retrieve a publicly visible VibeNation user profile.
    """

    authentication_classes = [
        VibeNationSessionAuthentication,
    ]

    permission_classes = [
        AllowAny,
    ]

    serializer_class = PublicProfileSerializer
    lookup_url_kwarg = "username"

    def get_queryset(self):
        return User.objects.filter(
            is_active=True,
            is_staff=False,
            is_superuser=False,
            onboarding_completed=True,
        )

    def get_object(self):
        username = self.kwargs.get(
            self.lookup_url_kwarg,
        )

        return get_object_or_404(
            self.get_queryset(),
            username__iexact=username,
        )
