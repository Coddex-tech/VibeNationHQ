from __future__ import annotations

from rest_framework import serializers

from music.models import (
    Genre,
    UserGenrePreference,
)


class UserGenrePreferenceSerializer(
    serializers.ModelSerializer,
):
    """
    Serializer for a user's explicit music genre
    preference.

    The authenticated user is intentionally not accepted
    from request data. It must be supplied by the
    service/API layer.
    """

    genre_id = serializers.PrimaryKeyRelatedField(
        source="genre",
        queryset=Genre.objects.filter(
            is_active=True,
        ),
    )

    class Meta:
        model = UserGenrePreference
        fields = [
            "id",
            "genre_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class UserGenrePreferenceSetSerializer(
    serializers.Serializer,
):
    """
    Validates a complete replacement of a user's
    explicit music genre preferences.

    The serializer returns actual Genre objects so the
    service layer does not need to perform request-data
    validation itself.
    """

    genre_ids = serializers.ListField(
        child=serializers.IntegerField(
            min_value=1,
        ),
        allow_empty=True,
    )

    def validate(self, attrs):
        genre_ids = attrs["genre_ids"]

        unique_genre_ids = list(
            dict.fromkeys(genre_ids)
        )

        genres = list(
            Genre.objects.filter(
                id__in=unique_genre_ids,
                is_active=True,
            )
        )

        genre_by_id = {
            genre.id: genre
            for genre in genres
        }

        missing_genre_ids = [
            genre_id
            for genre_id in unique_genre_ids
            if genre_id not in genre_by_id
        ]

        if missing_genre_ids:
            raise serializers.ValidationError(
                {
                    "genre_ids": [
                        (
                            "One or more selected genres "
                            "are unavailable."
                        )
                    ],
                    "invalid_genre_ids": (
                        missing_genre_ids
                    ),
                }
            )

        attrs["genre_ids"] = [
            genre_by_id[genre_id]
            for genre_id in unique_genre_ids
        ]

        return attrs