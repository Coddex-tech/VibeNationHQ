from __future__ import annotations

from django.db import transaction

from music.models import (
    Genre,
    UserGenrePreference,
)


class UserGenrePreferenceService:
    """
    Handles explicit music genre preferences for users.

    Explicit genre preferences are one input to the music
    feed. Behavioral signals such as views, previews,
    favorites, ratings, and follows remain separate.
    """

    @staticmethod
    def add_preference(
        *,
        user,
        genre: Genre,
    ) -> UserGenrePreference:
        """
        Add a genre preference for a user.

        If the preference already exists, return the existing
        preference instead of creating a duplicate.
        """
        preference, _ = (
            UserGenrePreference.objects.get_or_create(
                user=user,
                genre=genre,
            )
        )

        return preference

    @staticmethod
    def remove_preference(
        *,
        user,
        genre: Genre,
    ) -> bool:
        """
        Remove a genre preference for a user.

        Returns True if a preference was removed,
        otherwise False.
        """
        deleted_count, _ = (
            UserGenrePreference.objects.filter(
                user=user,
                genre=genre,
            ).delete()
        )

        return deleted_count > 0

    @staticmethod
    @transaction.atomic
    def set_preferences(
        *,
        user,
        genres: list[Genre],
    ) -> list[UserGenrePreference]:
        """
        Replace all explicit genre preferences for a user.

        The resulting database state contains exactly the
        supplied genres.
        """
        genre_ids = {
            genre.id
            for genre in genres
        }

        UserGenrePreference.objects.filter(
            user=user,
        ).exclude(
            genre_id__in=genre_ids,
        ).delete()

        existing_preferences = {
            preference.genre_id: preference
            for preference in (
                UserGenrePreference.objects.filter(
                    user=user,
                    genre_id__in=genre_ids,
                )
            )
        }

        preferences_to_create = [
            UserGenrePreference(
                user=user,
                genre=genre,
            )
            for genre in genres
            if genre.id not in existing_preferences
        ]

        if preferences_to_create:
            UserGenrePreference.objects.bulk_create(
                preferences_to_create,
                ignore_conflicts=True,
            )

        return list(
            UserGenrePreference.objects.filter(
                user=user,
                genre_id__in=genre_ids,
            ).select_related("genre")
        )

    @staticmethod
    def get_preferences(
        *,
        user,
    ):
        """
        Return a user's explicit genre preferences.
        """
        return (
            UserGenrePreference.objects
            .filter(user=user)
            .select_related("genre")
            .order_by("genre__name")
        )