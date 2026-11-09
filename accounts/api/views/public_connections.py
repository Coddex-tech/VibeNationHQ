
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import (
    BooleanField,
    Exists,
    OuterRef,
    Q,
    Value,
)

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from accounts.authentications import (
    VibeNationSessionAuthentication,
)

from music.api.pagination import MusicPagination
from music.models import (
    Artist,
    ArtistFollow,
    UserFollow,
)

from accounts.serializers.public_connections import (
    PublicConnectionArtistSerializer,
    PublicConnectionUserSerializer,
)


User = get_user_model()


class PublicConnectionsView(generics.ListAPIView):
    """
    List the public connections of a VibeNation user.

    Supported tabs:

    - followers: Users who follow the profile.
    - following: Users the profile follows.
    - artists: Artists the profile follows.

    Optional search:

    - User tabs search username and display name.
    - Artist tab searches artist name.

    The current viewer's follow state is annotated onto
    each returned object using EXISTS subqueries.

    Results are paginated using MusicPagination.
    """

    authentication_classes = [
        VibeNationSessionAuthentication,
    ]

    permission_classes = [
        AllowAny,
    ]

    pagination_class = MusicPagination

    lookup_url_kwarg = "username"

    MAX_SEARCH_LENGTH = 100

    # ========================================================
    # PROFILE AND TAB HELPERS
    # ========================================================

    def get_profile(self):
        """
        Retrieve the publicly visible profile whose
        connections are being requested.

        The same visibility rules as PublicProfileView
        are enforced.
        """

        if not hasattr(self, "_profile"):
            username = self.kwargs.get(
                self.lookup_url_kwarg,
            )

            self._profile = get_object_or_404(
                User.objects.filter(
                    is_active=True,
                    is_staff=False,
                    is_superuser=False,
                    onboarding_completed=True,
                ),
                username__iexact=username,
            )

        return self._profile

    def get_tab(self):
        """
        Validate the requested connections tab.

        A tab is required so the endpoint never silently
        returns an unintended connection category.
        """

        tab = self.request.query_params.get(
            "tab",
            "",
        ).strip().lower()

        allowed_tabs = {
            "followers",
            "following",
            "artists",
        }

        if tab not in allowed_tabs:
            raise ValidationError({
                "tab": (
                    "Choose followers, following, or artists."
                ),
            })

        return tab

    def get_search_query(self):
        """
        Retrieve and validate the optional search keyword.

        Empty searches are ignored.
        """

        search = self.request.query_params.get(
            "search",
            "",
        ).strip()

        if len(search) > self.MAX_SEARCH_LENGTH:
            raise ValidationError({
                "search": (
                    "Search cannot exceed "
                    f"{self.MAX_SEARCH_LENGTH} characters."
                ),
            })

        return search

    # ========================================================
    # VIEWER FOLLOW STATE
    # ========================================================

    def annotate_user_follow_state(self, queryset):
        """
        Annotate whether the authenticated viewer follows
        each user in the connections list.

        Anonymous viewers receive False.

        This uses EXISTS instead of a serializer-level
        database query for every returned user.
        """

        viewer = self.request.user

        if viewer.is_authenticated:
            viewer_follows_user = UserFollow.objects.filter(
                follower=viewer,
                following_id=OuterRef("pk"),
            )

            return queryset.annotate(
                is_following=Exists(
                    viewer_follows_user,
                ),
            )

        return queryset.annotate(
            is_following=Value(
                False,
                output_field=BooleanField(),
            ),
        )

    def annotate_artist_follow_state(self, queryset):
        """
        Annotate whether the authenticated viewer follows
        each artist in the connections list.

        Anonymous viewers receive False.

        This uses EXISTS instead of a serializer-level
        database query for every returned artist.
        """

        viewer = self.request.user

        if viewer.is_authenticated:
            viewer_follows_artist = ArtistFollow.objects.filter(
                user=viewer,
                artist_id=OuterRef("pk"),
            )

            return queryset.annotate(
                is_following=Exists(
                    viewer_follows_artist,
                ),
            )

        return queryset.annotate(
            is_following=Value(
                False,
                output_field=BooleanField(),
            ),
        )

    # ========================================================
    # QUERYSET
    # ========================================================

    def get_queryset(self):
        """
        Return the requested connections as user or artist
        objects rather than raw relationship objects.

        Relationship creation timestamps determine ordering,
        with the newest connections appearing first.

        Search filtering is applied before pagination.
        """

        profile = self.get_profile()
        tab = self.get_tab()
        search = self.get_search_query()

        # ----------------------------------------------------
        # FOLLOWERS
        # ----------------------------------------------------

        if tab == "followers":
            queryset = (
                User.objects
                .filter(
                    following_relationships__following=profile,
                    is_active=True,
                    is_staff=False,
                    is_superuser=False,
                    onboarding_completed=True,
                )
            )

            if search:
                queryset = queryset.filter(
                    Q(username__icontains=search)
                    | Q(display_name__icontains=search)
                )

            queryset = queryset.order_by(
                "-following_relationships__created_at",
                "-pk",
            )

            return self.annotate_user_follow_state(
                queryset,
            )

        # ----------------------------------------------------
        # FOLLOWING
        # ----------------------------------------------------

        if tab == "following":
            queryset = (
                User.objects
                .filter(
                    follower_relationships__follower=profile,
                    is_active=True,
                    is_staff=False,
                    is_superuser=False,
                    onboarding_completed=True,
                )
            )

            if search:
                queryset = queryset.filter(
                    Q(username__icontains=search)
                    | Q(display_name__icontains=search)
                )

            queryset = queryset.order_by(
                "-follower_relationships__created_at",
                "-pk",
            )

            return self.annotate_user_follow_state(
                queryset,
            )

        # ----------------------------------------------------
        # FOLLOWED ARTISTS
        # ----------------------------------------------------

        queryset = (
            Artist.objects
            .filter(
                followers__user=profile,
                is_active=True,
            )
        )

        if search:
            queryset = queryset.filter(
                name__icontains=search,
            )

        queryset = queryset.order_by(
            "-followers__created_at",
            "-pk",
        )

        return self.annotate_artist_follow_state(
            queryset,
        )

    # ========================================================
    # SERIALIZER
    # ========================================================

    def get_serializer_class(self):
        """
        Select the appropriate representation for each tab.
        """

        tab = self.get_tab()

        if tab == "artists":
            return PublicConnectionArtistSerializer

        return PublicConnectionUserSerializer
