from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from music.models import (
    Artist,
    ArtistFollow,
    UserFollow,
)

from music.serializers.follows import (
    ArtistFollowCreateSerializer,
    ArtistFollowSerializer,
    UserFollowCreateSerializer,
    UserFollowSerializer,
)

from music.services.feed_interactions import (
    MusicFeedInteractionService,
)

from music.services.follows import (
    ArtistFollowService,
    UserFollowService,
)


# ============================================================
# ARTIST FOLLOW
# ============================================================

class ArtistFollowAPIView(generics.GenericAPIView):
    """
    Follow or unfollow an artist.

    POST   -> follow artist
    DELETE -> unfollow artist
    """

    queryset = Artist.objects.filter(
        is_active=True,
    )
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        artist = self.get_object()

        serializer = ArtistFollowCreateSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        follow = ArtistFollowService.create(
            user=request.user,
            artist=artist,
        )

        MusicFeedInteractionService.record_artist_follow(
            user=request.user,
            artist=artist,
        )

        artist.refresh_from_db()

        output_serializer = ArtistFollowSerializer(
            follow,
            context=self.get_serializer_context(),
        )

        return Response(
            {
                "following": True,
                "followers_count": artist.followers_count,
                "follow": output_serializer.data,
            },
            status=201,
        )

    def delete(self, request, *args, **kwargs):
        artist = self.get_object()

        follow = ArtistFollow.objects.filter(
            user=request.user,
            artist=artist,
        ).first()

        if follow is None:
            return Response(
                {
                    "following": False,
                    "followers_count": artist.followers_count,
                },
                status=200,
            )

        ArtistFollowService.delete(
            follow_instance=follow,
        )

        artist.refresh_from_db()

        return Response(
            {
                "following": False,
                "followers_count": artist.followers_count,
            },
            status=200,
        )


# ============================================================
# USER FOLLOW
# ============================================================

class UserFollowAPIView(generics.GenericAPIView):
    """
    Follow or unfollow another user.

    POST   -> follow user
    DELETE -> unfollow user
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Return users that can be followed.

        The target user comes from the URL.
        """

        return UserFollow._meta.get_field(
            "following"
        ).remote_field.model.objects.all()

    def post(self, request, *args, **kwargs):
        following = self.get_object()

        serializer = UserFollowCreateSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        follow = UserFollowService.create(
            follower=request.user,
            following=following,
        )

        output_serializer = UserFollowSerializer(
            follow,
            context=self.get_serializer_context(),
        )

        return Response(
            {
                "following": True,
                "follow": output_serializer.data,
            },
            status=201,
        )

    def delete(self, request, *args, **kwargs):
        following = self.get_object()

        follow = UserFollow.objects.filter(
            follower=request.user,
            following=following,
        ).first()

        if follow is None:
            return Response(
                {
                    "following": False,
                },
                status=200,
            )

        UserFollowService.delete(
            follow_instance=follow,
        )

        return Response(
            {
                "following": False,
            },
            status=200,
        )