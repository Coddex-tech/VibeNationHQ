from rest_framework import serializers

from music.models import (
    ArtistFollow,
    UserFollow,
)

from .base import BaseModelSerializer
from .catalog import ArtistCardSerializer


# ============================================================
# ARTIST FOLLOW
# ============================================================

class ArtistFollowSerializer(BaseModelSerializer):
    """
    Read-only representation of a user following an artist.
    """

    artist = ArtistCardSerializer(
        read_only=True,
    )

    class Meta:
        model = ArtistFollow
        fields = [
            "id",
            "user",
            "artist",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ArtistFollowCreateSerializer(serializers.ModelSerializer):
    """
    Create an artist follow relationship.

    The authenticated user and target artist are assigned
    server-side. The artist comes from the URL.
    """

    class Meta:
        model = ArtistFollow
        fields = []


# ============================================================
# USER FOLLOW
# ============================================================

class UserFollowSerializer(BaseModelSerializer):
    """
    Read-only representation of a user-to-user follow relationship.
    """

    class Meta:
        model = UserFollow
        fields = [
            "id",
            "follower",
            "following",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class UserFollowCreateSerializer(serializers.ModelSerializer):
    """
    Create a user-to-user follow relationship.

    The authenticated user becomes the follower.
    The target user comes from the URL.
    """

    class Meta:
        model = UserFollow
        fields = []