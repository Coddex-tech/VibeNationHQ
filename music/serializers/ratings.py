from rest_framework import serializers

from music.models import (
    SongRating,
    AlbumRating,
    Song,
    Album,
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

    The authenticated user is assigned server-side.
    The song must be published.
    """

    song = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.filter(
            status=Song.Status.PUBLISHED,
        )
    )

    rating = serializers.DecimalField(
        max_digits=2,
        decimal_places=1,
    )

    class Meta:
        model = SongRating
        fields = [
            "song",
            "rating",
        ]

    def validate_rating(self, value):
        return validate_half_star_rating(value)

    def create(self, validated_data):
        request = self.context["request"]

        return SongRating.objects.create(
            user=request.user,
            **validated_data,
        )


class SongRatingUpdateSerializer(serializers.ModelSerializer):
    """
    Update an existing song rating.

    Only the rating itself can be changed.
    """

    rating = serializers.DecimalField(
        max_digits=2,
        decimal_places=1,
    )

    class Meta:
        model = SongRating
        fields = [
            "rating",
        ]

    def validate_rating(self, value):
        return validate_half_star_rating(value)


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

    The authenticated user is assigned server-side.
    The album must be published.
    """

    album = serializers.PrimaryKeyRelatedField(
        queryset=Album.objects.filter(
            status=Album.Status.PUBLISHED,
        )
    )

    rating = serializers.DecimalField(
        max_digits=2,
        decimal_places=1,
    )

    class Meta:
        model = AlbumRating
        fields = [
            "album",
            "rating",
        ]

    def validate_rating(self, value):
        return validate_half_star_rating(value)

    def create(self, validated_data):
        request = self.context["request"]

        return AlbumRating.objects.create(
            user=request.user,
            **validated_data,
        )


class AlbumRatingUpdateSerializer(serializers.ModelSerializer):
    """
    Update an existing album rating.

    Only the rating itself can be changed.
    """

    rating = serializers.DecimalField(
        max_digits=2,
        decimal_places=1,
    )

    class Meta:
        model = AlbumRating
        fields = [
            "rating",
        ]

    def validate_rating(self, value):
        return validate_half_star_rating(value)