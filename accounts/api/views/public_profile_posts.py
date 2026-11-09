from django.contrib.auth import get_user_model
from django.db.models import (
    BooleanField,
    Count,
    Exists,
    OuterRef,
    Prefetch,
    Value,
)
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import AllowAny

from accounts.authentications import (
    VibeNationSessionAuthentication,
)
from music.api.pagination import MusicPagination
from music.models import (
    CommunityPost,
    CommunityPostFavorite,
    CommunityPostLike,
    UserFollow,
)
from music.serializers.community import (
    CommunityPostSerializer,
)


User = get_user_model()


class PublicProfilePostsView(generics.ListAPIView):
    """
    List published community posts belonging to a public
    VibeNation user profile.

    Posts are returned newest first.

    The queryset preserves the optimized relationship
    loading and viewer-specific annotations used by the
    general community feed.
    """

    authentication_classes = [
        VibeNationSessionAuthentication,
    ]

    permission_classes = [
        AllowAny,
    ]

    serializer_class = CommunityPostSerializer
    pagination_class = MusicPagination

    lookup_url_kwarg = "username"

    def get_profile(self):
        """
        Retrieve the publicly visible profile whose posts
        are being requested.
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

    def get_queryset(self):
        profile = self.get_profile()
        viewer = self.request.user

        # ----------------------------------------------------
        # Author queryset and viewer follow state
        # ----------------------------------------------------

        author_queryset = User.objects.all()

        if viewer.is_authenticated:
            author_follows = UserFollow.objects.filter(
                follower=viewer,
                following_id=OuterRef("pk"),
            )

            author_queryset = author_queryset.annotate(
                is_following=Exists(
                    author_follows,
                ),
            )
        else:
            author_queryset = author_queryset.annotate(
                is_following=Value(
                    False,
                    output_field=BooleanField(),
                ),
            )

        # ----------------------------------------------------
        # Published posts belonging to this profile
        # ----------------------------------------------------

        queryset = (
            CommunityPost.objects
            .filter(
                user=profile,
                status=CommunityPost.Status.PUBLISHED,
            )
            .select_related(
                "target",
            )
            .prefetch_related(
                Prefetch(
                    "user",
                    queryset=author_queryset,
                ),
                "target__song__artists",
                "target__song__featured_artists",
                "target__song__provider_identities",
                "target__album__artists",
                "target__artist",
            )
            .annotate(
                favorites_count=Count(
                    "favorites",
                    distinct=True,
                ),
            )
        )

        # ----------------------------------------------------
        # Viewer-specific like and favorite states
        # ----------------------------------------------------

        if viewer.is_authenticated:
            liked_posts = CommunityPostLike.objects.filter(
                user=viewer,
                post_id=OuterRef("pk"),
            )

            favorited_posts = (
                CommunityPostFavorite.objects.filter(
                    user=viewer,
                    post_id=OuterRef("pk"),
                )
            )

            queryset = queryset.annotate(
                is_liked=Exists(
                    liked_posts,
                ),
                is_favorited=Exists(
                    favorited_posts,
                ),
            )
        else:
            queryset = queryset.annotate(
                is_liked=Value(
                    False,
                    output_field=BooleanField(),
                ),
                is_favorited=Value(
                    False,
                    output_field=BooleanField(),
                ),
            )

        # ----------------------------------------------------
        # Fixed chronological ordering
        # ----------------------------------------------------

        return queryset.order_by(
            "-created_at",
            "-pk",
        )