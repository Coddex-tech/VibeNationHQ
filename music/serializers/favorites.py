from rest_framework import serializers

from music.models import (
    SongFavorite,
    AlbumFavorite,
)

from .base import BaseModelSerializer
from .catalog import (
    SongCardSerializer,
    AlbumCardSerializer,
)


# ============================================================
# SONG FAVORITE
# ============================================================

class SongFavoriteSerializer(BaseModelSerializer):
    """
    Read-only representation of a user's saved/favorite song.
    """

    song = SongCardSerializer(
        read_only=True,
    )

    class Meta:
        model = SongFavorite
        fields = [
            "id",
            "user",
            "song",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class SongFavoriteCreateSerializer(serializers.ModelSerializer):
    """
    Create a favorite/save relationship for a song.

    The authenticated user and song are assigned server-side.
    The song comes from the URL, not the request body.
    """

    class Meta:
        model = SongFavorite
        fields = []


# ============================================================
# ALBUM FAVORITE
# ============================================================

class AlbumFavoriteSerializer(BaseModelSerializer):
    """
    Read-only representation of a user's saved/favorite album.
    """

    album = AlbumCardSerializer(
        read_only=True,
    )

    class Meta:
        model = AlbumFavorite
        fields = [
            "id",
            "user",
            "album",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class AlbumFavoriteCreateSerializer(serializers.ModelSerializer):
    """
    Create a favorite/save relationship for an album.

    The authenticated user and album are assigned server-side.
    The album comes from the URL, not the request body.
    """

    class Meta:
        model = AlbumFavorite
        fields = []