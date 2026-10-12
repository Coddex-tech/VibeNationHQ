from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from music.models import Genre
from music.serializers.genre_preferences import (
    UserGenrePreferenceSerializer,
    UserGenrePreferenceSetSerializer,
)


User = get_user_model()


class UserGenrePreferenceSerializerTests(
    APITestCase,
):
    def setUp(self):
        self.user = User.objects.create_user(
            email="genre@example.com",
            username="genreuser",
            password="StrongPass123!",
        )

        self.genre = Genre.objects.create(
            name="Afrobeats",
            slug="afrobeats",
            is_active=True,
        )

        self.inactive_genre = Genre.objects.create(
            name="Inactive Genre",
            slug="inactive-genre",
            is_active=False,
        )

    def test_valid_genre_is_accepted(self):
        serializer = UserGenrePreferenceSerializer(
            data={
                "genre_id": self.genre.id,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertEqual(
            serializer.validated_data["genre"],
            self.genre,
        )

    def test_inactive_genre_is_rejected(self):
        serializer = UserGenrePreferenceSerializer(
            data={
                "genre_id": self.inactive_genre.id,
            }
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "genre_id",
            serializer.errors,
        )

    def test_nonexistent_genre_is_rejected(self):
        serializer = UserGenrePreferenceSerializer(
            data={
                "genre_id": 999999,
            }
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "genre_id",
            serializer.errors,
        )

    def test_genre_id_is_required(self):
        serializer = UserGenrePreferenceSerializer(
            data={}
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "genre_id",
            serializer.errors,
        )

    def test_user_id_is_not_accepted(self):
        serializer = UserGenrePreferenceSerializer(
            data={
                "genre_id": self.genre.id,
                "user_id": self.user.id,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertNotIn(
            "user_id",
            serializer.validated_data,
        )

    def test_expected_output_fields_are_present(self):
        preference = (
            self.user.music_genre_preferences.create(
                genre=self.genre,
            )
        )

        serializer = UserGenrePreferenceSerializer(
            preference,
        )

        self.assertEqual(
            set(serializer.data.keys()),
            {
                "id",
                "genre_id",
                "created_at",
                "updated_at",
            },
        )

    def test_serializer_can_create_with_user(self):
        serializer = UserGenrePreferenceSerializer(
            data={
                "genre_id": self.genre.id,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        preference = serializer.save(
            user=self.user,
        )

        self.assertEqual(
            preference.user,
            self.user,
        )

        self.assertEqual(
            preference.genre,
            self.genre,
        )


class UserGenrePreferenceSetSerializerTests(
    APITestCase,
):
    def setUp(self):
        self.genres = [
            Genre.objects.create(
                name="Afrobeats",
                slug="afrobeats",
                is_active=True,
            ),
            Genre.objects.create(
                name="Amapiano",
                slug="amapiano",
                is_active=True,
            ),
            Genre.objects.create(
                name="Hip-Hop",
                slug="hip-hop",
                is_active=True,
            ),
        ]

        self.inactive_genre = Genre.objects.create(
            name="Inactive Genre",
            slug="inactive-genre",
            is_active=False,
        )

    def test_valid_genre_ids_are_accepted(self):
        serializer = UserGenrePreferenceSetSerializer(
            data={
                "genre_ids": [
                    self.genres[0].id,
                    self.genres[1].id,
                ],
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertEqual(
            serializer.validated_data["genre_ids"],
            [
                self.genres[0],
                self.genres[1],
            ],
        )

    def test_empty_genre_list_is_accepted(self):
        serializer = UserGenrePreferenceSetSerializer(
            data={
                "genre_ids": [],
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertEqual(
            serializer.validated_data["genre_ids"],
            [],
        )

    def test_duplicate_genre_ids_are_removed(self):
        serializer = UserGenrePreferenceSetSerializer(
            data={
                "genre_ids": [
                    self.genres[0].id,
                    self.genres[0].id,
                    self.genres[1].id,
                    self.genres[1].id,
                ],
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertEqual(
            serializer.validated_data["genre_ids"],
            [
                self.genres[0],
                self.genres[1],
            ],
        )

    def test_inactive_genre_is_rejected(self):
        serializer = UserGenrePreferenceSetSerializer(
            data={
                "genre_ids": [
                    self.genres[0].id,
                    self.inactive_genre.id,
                ],
            }
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "invalid_genre_ids",
            serializer.errors,
        )

        self.assertEqual(
            [str(self.inactive_genre.id)],
            [
                str(value)
                for value in serializer.errors[
                    "invalid_genre_ids"
                ]
            ],
        )

    def test_nonexistent_genre_is_rejected(self):
        serializer = UserGenrePreferenceSetSerializer(
            data={
                "genre_ids": [
                    self.genres[0].id,
                    999999,
                ],
            }
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "invalid_genre_ids",
            serializer.errors,
        )

        self.assertEqual(
            ["999999"],
            [
                str(value)
                for value in serializer.errors[
                    "invalid_genre_ids"
                ]
            ],
        )

    def test_genre_ids_must_be_a_list(self):
        serializer = UserGenrePreferenceSetSerializer(
            data={
                "genre_ids": self.genres[0].id,
            }
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "genre_ids",
            serializer.errors,
        )

    def test_genre_ids_must_contain_integers(self):
        serializer = UserGenrePreferenceSetSerializer(
            data={
                "genre_ids": [
                    self.genres[0].id,
                    "not-an-integer",
                ],
            }
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "genre_ids",
            serializer.errors,
        )