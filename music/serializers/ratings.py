from rest_framework import serializers

from music.models import (
    SongRating,
    AlbumRating,
)

from .base import (
    BaseModelSerializer,
    validate_half_star_rating,
)

from .catalog import (
    SongCardSerializer,
    AlbumCardSerializer,
)


# ============================================================
# SONG RATING
# ============================================================

class SongRatingSerializer(BaseModelSerializer):
    """
    Read-only representation of a user's rating for a song.
    """

    song = SongCardSerializer(
        read_only=True,
    )

    rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = SongRating
        fields = [
            "id",
            "user",
            "song",
            "rating",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class SongRatingCreateSerializer(serializers.ModelSerializer):
    """
    Create a rating for a song.

    The authenticated user and song are assigned server-side.
    The song must be published.
    """

    rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[
            validate_half_star_rating,
        ],
    )

    class Meta:
        model = SongRating
        fields = [
            "rating",
        ]


class SongRatingUpdateSerializer(serializers.ModelSerializer):
    """
    Update an existing song rating.

    Only the rating itself can be changed.
    """

    rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[
            validate_half_star_rating,
        ],
    )

    class Meta:
        model = SongRating
        fields = [
            "rating",
        ]


# ============================================================
# ALBUM RATING
# ============================================================

class AlbumRatingSerializer(BaseModelSerializer):
    """
    Read-only representation of a user's rating for an album.
    """

    album = AlbumCardSerializer(
        read_only=True,
    )

    rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = AlbumRating
        fields = [
            "id",
            "user",
            "album",
            "rating",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class AlbumRatingCreateSerializer(serializers.ModelSerializer):
    """
    Create a rating for an album.

    The authenticated user and album are assigned server-side.
    The album must be published.
    """

    rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[
            validate_half_star_rating,
        ],
    )

    class Meta:
        model = AlbumRating
        fields = [
            "rating",
        ]


class AlbumRatingUpdateSerializer(serializers.ModelSerializer):
    """
    Update an existing album rating.

    Only the rating itself can be changed.
    """

    rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[
            validate_half_star_rating,
        ],
    )

    class Meta:
        model = AlbumRating
        fields = [
            "rating",
        ]