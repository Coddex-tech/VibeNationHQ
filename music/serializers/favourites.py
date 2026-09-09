from rest_framework import serializers

from music.models import (
    SongFavorite,
    AlbumFavorite,
    Song,
    Album,
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

    The authenticated user is assigned server-side.
    The song must be published.
    """

    song = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.filter(
            status=Song.Status.PUBLISHED,
        )
    )

    class Meta:
        model = SongFavorite
        fields = [
            "song",
        ]

    def create(self, validated_data):
        request = self.context["request"]

        return SongFavorite.objects.create(
            user=request.user,
            **validated_data,
        )


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

    The authenticated user is assigned server-side.
    The album must be published.
    """

    album = serializers.PrimaryKeyRelatedField(
        queryset=Album.objects.filter(
            status=Album.Status.PUBLISHED,
        )
    )

    class Meta:
        model = AlbumFavorite
        fields = [
            "album",
        ]

    def create(self, validated_data):
        request = self.context["request"]

        return AlbumFavorite.objects.create(
            user=request.user,
            **validated_data,
        )