from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from music.models import (
    Genre,
    UserGenrePreference,
)


User = get_user_model()


class UserGenrePreferenceModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="TestPassword123!",
        )

        self.genre = Genre.objects.create(
            name="Afrobeats",
            slug="afrobeats",
        )

        self.other_genre = Genre.objects.create(
            name="Hip-Hop",
            slug="hip-hop",
        )

    def test_creates_user_genre_preference(self):
        preference = UserGenrePreference.objects.create(
            user=self.user,
            genre=self.genre,
        )

        self.assertEqual(
            preference.user,
            self.user,
        )

        self.assertEqual(
            preference.genre,
            self.genre,
        )

        self.assertEqual(
            UserGenrePreference.objects.count(),
            1,
        )

    def test_string_representation(self):
        preference = UserGenrePreference.objects.create(
            user=self.user,
            genre=self.genre,
        )

        self.assertEqual(
            str(preference),
            f"{self.user} prefers {self.genre}",
        )

    def test_same_user_cannot_prefer_same_genre_twice(self):
        UserGenrePreference.objects.create(
            user=self.user,
            genre=self.genre,
        )

        with self.assertRaises(IntegrityError):
            UserGenrePreference.objects.create(
                user=self.user,
                genre=self.genre,
            )

    def test_different_users_can_prefer_same_genre(self):
        UserGenrePreference.objects.create(
            user=self.user,
            genre=self.genre,
        )

        UserGenrePreference.objects.create(
            user=self.other_user,
            genre=self.genre,
        )

        self.assertEqual(
            UserGenrePreference.objects.count(),
            2,
        )

    def test_same_user_can_prefer_multiple_genres(self):
        UserGenrePreference.objects.create(
            user=self.user,
            genre=self.genre,
        )

        UserGenrePreference.objects.create(
            user=self.user,
            genre=self.other_genre,
        )

        self.assertEqual(
            UserGenrePreference.objects.count(),
            2,
        )

    def test_deleting_user_deletes_preferences(self):
        preference = UserGenrePreference.objects.create(
            user=self.user,
            genre=self.genre,
        )

        preference_id = preference.id

        self.user.delete()

        self.assertFalse(
            UserGenrePreference.objects.filter(
                id=preference_id,
            ).exists()
        )

    def test_deleting_genre_deletes_preferences(self):
        preference = UserGenrePreference.objects.create(
            user=self.user,
            genre=self.genre,
        )

        preference_id = preference.id

        self.genre.delete()

        self.assertFalse(
            UserGenrePreference.objects.filter(
                id=preference_id,
            ).exists()
        )

    def test_user_reverse_relationship(self):
        UserGenrePreference.objects.create(
            user=self.user,
            genre=self.genre,
        )

        UserGenrePreference.objects.create(
            user=self.user,
            genre=self.other_genre,
        )

        preferences = (
            self.user
            .music_genre_preferences
            .all()
        )

        self.assertEqual(
            preferences.count(),
            2,
        )

        self.assertEqual(
            set(preferences.values_list("genre_id", flat=True)),
            {
                self.genre.id,
                self.other_genre.id,
            },
        )

    def test_genre_reverse_relationship(self):
        UserGenrePreference.objects.create(
            user=self.user,
            genre=self.genre,
        )

        UserGenrePreference.objects.create(
            user=self.other_user,
            genre=self.genre,
        )

        preferences = (
            self.genre
            .user_preferences
            .all()
        )

        self.assertEqual(
            preferences.count(),
            2,
        )

        self.assertEqual(
            set(preferences.values_list("user_id", flat=True)),
            {
                self.user.id,
                self.other_user.id,
            },
        )