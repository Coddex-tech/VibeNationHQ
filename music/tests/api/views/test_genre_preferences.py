from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from music.api.views.genre_preferences import (
    UserGenrePreferenceDeleteAPIView,
    UserGenrePreferenceListCreateAPIView,
    UserGenrePreferenceSetAPIView,
)
from music.models import (
    Genre,
    UserGenrePreference,
)


User = get_user_model()


class UserGenrePreferenceAPITests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

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

        self.afrobeats = Genre.objects.create(
            name="Afrobeats",
            slug="afrobeats",
        )

        self.amapiano = Genre.objects.create(
            name="Amapiano",
            slug="amapiano",
        )

        self.gospel = Genre.objects.create(
            name="Gospel",
            slug="gospel",
        )

        self.inactive_genre = Genre.objects.create(
            name="Inactive Genre",
            slug="inactive-genre",
            is_active=False,
        )

    def authenticate(self, request):
        force_authenticate(
            request,
            user=self.user,
        )

        return request

    def test_get_requires_authentication(self):
        request = self.factory.get(
            "/api/v1/music/preferences/genres/",
        )

        response = (
            UserGenrePreferenceListCreateAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_post_requires_authentication(self):
        request = self.factory.post(
            "/api/v1/music/preferences/genres/",
            {
                "genre_id": self.afrobeats.id,
            },
            format="json",
        )

        response = (
            UserGenrePreferenceListCreateAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_delete_requires_authentication(self):
        request = self.factory.delete(
            f"/api/v1/music/preferences/genres/{self.afrobeats.id}/",
        )

        response = (
            UserGenrePreferenceDeleteAPIView.as_view()(
                request,
                genre_id=self.afrobeats.id,
            )
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_set_requires_authentication(self):
        request = self.factory.post(
            "/api/v1/music/preferences/genres/set/",
            {
                "genre_ids": [
                    self.afrobeats.id,
                ],
            },
            format="json",
        )

        response = (
            UserGenrePreferenceSetAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_get_returns_only_current_users_preferences(
        self,
    ):
        UserGenrePreference.objects.create(
            user=self.user,
            genre=self.afrobeats,
        )

        UserGenrePreference.objects.create(
            user=self.other_user,
            genre=self.amapiano,
        )

        request = self.authenticate(
            self.factory.get(
                "/api/v1/music/preferences/genres/",
            )
        )

        response = (
            UserGenrePreferenceListCreateAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            response.data["results"][0]["genre_id"],
            self.afrobeats.id,
        )

    def test_get_returns_empty_results_for_user_without_preferences(
        self,
    ):
        request = self.authenticate(
            self.factory.get(
                "/api/v1/music/preferences/genres/",
            )
        )

        response = (
            UserGenrePreferenceListCreateAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["results"],
            [],
        )

    def test_post_creates_preference(self):
        request = self.authenticate(
            self.factory.post(
                "/api/v1/music/preferences/genres/",
                {
                    "genre_id": self.afrobeats.id,
                },
                format="json",
            )
        )

        response = (
            UserGenrePreferenceListCreateAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            response.data["genre_id"],
            self.afrobeats.id,
        )

        self.assertTrue(
            UserGenrePreference.objects.filter(
                user=self.user,
                genre=self.afrobeats,
            ).exists()
        )

    def test_post_duplicate_preference_is_idempotent(
        self,
    ):
        existing = (
            UserGenrePreference.objects.create(
                user=self.user,
                genre=self.afrobeats,
            )
        )

        request = self.authenticate(
            self.factory.post(
                "/api/v1/music/preferences/genres/",
                {
                    "genre_id": self.afrobeats.id,
                },
                format="json",
            )
        )

        response = (
            UserGenrePreferenceListCreateAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            response.data["id"],
            existing.id,
        )

        self.assertEqual(
            UserGenrePreference.objects.filter(
                user=self.user,
                genre=self.afrobeats,
            ).count(),
            1,
        )

    def test_post_rejects_inactive_genre(self):
        request = self.authenticate(
            self.factory.post(
                "/api/v1/music/preferences/genres/",
                {
                    "genre_id": self.inactive_genre.id,
                },
                format="json",
            )
        )

        response = (
            UserGenrePreferenceListCreateAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "genre_id",
            response.data,
        )

    def test_post_rejects_missing_genre(self):
        request = self.authenticate(
            self.factory.post(
                "/api/v1/music/preferences/genres/",
                {},
                format="json",
            )
        )

        response = (
            UserGenrePreferenceListCreateAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "genre_id",
            response.data,
        )

    def test_post_rejects_nonexistent_genre(self):
        request = self.authenticate(
            self.factory.post(
                "/api/v1/music/preferences/genres/",
                {
                    "genre_id": 999999,
                },
                format="json",
            )
        )

        response = (
            UserGenrePreferenceListCreateAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_post_cannot_set_user_id(self):
        request = self.authenticate(
            self.factory.post(
                "/api/v1/music/preferences/genres/",
                {
                    "genre_id": self.afrobeats.id,
                    "user_id": self.other_user.id,
                },
                format="json",
            )
        )

        response = (
            UserGenrePreferenceListCreateAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        preference = (
            UserGenrePreference.objects.get(
                id=response.data["id"],
            )
        )

        self.assertEqual(
            preference.user,
            self.user,
        )

    def test_delete_removes_current_users_preference(
        self,
    ):
        UserGenrePreference.objects.create(
            user=self.user,
            genre=self.afrobeats,
        )

        request = self.authenticate(
            self.factory.delete(
                f"/api/v1/music/preferences/genres/{self.afrobeats.id}/",
            )
        )

        response = (
            UserGenrePreferenceDeleteAPIView.as_view()(
                request,
                genre_id=self.afrobeats.id,
            )
        )

        self.assertEqual(
            response.status_code,
            204,
        )

        self.assertFalse(
            UserGenrePreference.objects.filter(
                user=self.user,
                genre=self.afrobeats,
            ).exists()
        )

    def test_delete_does_not_remove_other_users_preference(
        self,
    ):
        UserGenrePreference.objects.create(
            user=self.other_user,
            genre=self.afrobeats,
        )

        request = self.authenticate(
            self.factory.delete(
                f"/api/v1/music/preferences/genres/{self.afrobeats.id}/",
            )
        )

        response = (
            UserGenrePreferenceDeleteAPIView.as_view()(
                request,
                genre_id=self.afrobeats.id,
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertTrue(
            UserGenrePreference.objects.filter(
                user=self.other_user,
                genre=self.afrobeats,
            ).exists()
        )

    def test_delete_returns_404_when_preference_does_not_exist(
        self,
    ):
        request = self.authenticate(
            self.factory.delete(
                f"/api/v1/music/preferences/genres/{self.afrobeats.id}/",
            )
        )

        response = (
            UserGenrePreferenceDeleteAPIView.as_view()(
                request,
                genre_id=self.afrobeats.id,
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_delete_returns_404_for_nonexistent_genre(
        self,
    ):
        request = self.authenticate(
            self.factory.delete(
                "/api/v1/music/preferences/genres/999999/",
            )
        )

        response = (
            UserGenrePreferenceDeleteAPIView.as_view()(
                request,
                genre_id=999999,
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_delete_returns_404_for_inactive_genre(
        self,
    ):
        request = self.authenticate(
            self.factory.delete(
                f"/api/v1/music/preferences/genres/{self.inactive_genre.id}/",
            )
        )

        response = (
            UserGenrePreferenceDeleteAPIView.as_view()(
                request,
                genre_id=self.inactive_genre.id,
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_set_preferences_replaces_existing_selection(
        self,
    ):
        UserGenrePreference.objects.create(
            user=self.user,
            genre=self.afrobeats,
        )

        UserGenrePreference.objects.create(
            user=self.user,
            genre=self.gospel,
        )

        request = self.authenticate(
            self.factory.post(
                "/api/v1/music/preferences/genres/set/",
                {
                    "genre_ids": [
                        self.amapiano.id,
                        self.gospel.id,
                    ],
                },
                format="json",
            )
        )

        response = (
            UserGenrePreferenceSetAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertSetEqual(
            {
                item["genre_id"]
                for item in response.data["results"]
            },
            {
                self.amapiano.id,
                self.gospel.id,
            },
        )

        self.assertSetEqual(
            set(
                UserGenrePreference.objects.filter(
                    user=self.user,
                ).values_list(
                    "genre_id",
                    flat=True,
                )
            ),
            {
                self.amapiano.id,
                self.gospel.id,
            },
        )

    def test_set_preferences_can_clear_all_preferences(
        self,
    ):
        UserGenrePreference.objects.create(
            user=self.user,
            genre=self.afrobeats,
        )

        request = self.authenticate(
            self.factory.post(
                "/api/v1/music/preferences/genres/set/",
                {
                    "genre_ids": [],
                },
                format="json",
            )
        )

        response = (
            UserGenrePreferenceSetAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["results"],
            [],
        )

        self.assertFalse(
            UserGenrePreference.objects.filter(
                user=self.user,
            ).exists()
        )

    def test_set_preferences_rejects_non_list(
        self,
    ):
        request = self.authenticate(
            self.factory.post(
                "/api/v1/music/preferences/genres/set/",
                {
                    "genre_ids": self.afrobeats.id,
                },
                format="json",
            )
        )

        response = (
            UserGenrePreferenceSetAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "genre_ids",
            response.data,
        )

    def test_set_preferences_rejects_non_integer_ids(
        self,
    ):
        request = self.authenticate(
            self.factory.post(
                "/api/v1/music/preferences/genres/set/",
                {
                    "genre_ids": [
                        self.afrobeats.id,
                        "invalid",
                    ],
                },
                format="json",
            )
        )

        response = (
            UserGenrePreferenceSetAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "genre_ids",
            response.data,
        )

    def test_set_preferences_rejects_inactive_genres(
        self,
    ):
        request = self.authenticate(
            self.factory.post(
                "/api/v1/music/preferences/genres/set/",
                {
                    "genre_ids": [
                        self.afrobeats.id,
                        self.inactive_genre.id,
                    ],
                },
                format="json",
            )
        )

        response = (
            UserGenrePreferenceSetAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "invalid_genre_ids",
            response.data,
        )

        self.assertFalse(
            UserGenrePreference.objects.filter(
                user=self.user,
            ).exists()
        )

    def test_set_preferences_rejects_nonexistent_genres(
        self,
    ):
        request = self.authenticate(
            self.factory.post(
                "/api/v1/music/preferences/genres/set/",
                {
                    "genre_ids": [
                        self.afrobeats.id,
                        999999,
                    ],
                },
                format="json",
            )
        )

        response = (
            UserGenrePreferenceSetAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "invalid_genre_ids",
            response.data,
        )

        self.assertFalse(
            UserGenrePreference.objects.filter(
                user=self.user,
            ).exists()
        )

    def test_set_preferences_deduplicates_genre_ids(
        self,
    ):
        request = self.authenticate(
            self.factory.post(
                "/api/v1/music/preferences/genres/set/",
                {
                    "genre_ids": [
                        self.afrobeats.id,
                        self.afrobeats.id,
                        self.amapiano.id,
                    ],
                },
                format="json",
            )
        )

        response = (
            UserGenrePreferenceSetAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertSetEqual(
            {
                item["genre_id"]
                for item in response.data["results"]
            },
            {
                self.afrobeats.id,
                self.amapiano.id,
            },
        )

        self.assertEqual(
            UserGenrePreference.objects.filter(
                user=self.user,
            ).count(),
            2,
        )

    def test_set_preferences_does_not_affect_other_users(
        self,
    ):
        UserGenrePreference.objects.create(
            user=self.other_user,
            genre=self.gospel,
        )

        request = self.authenticate(
            self.factory.post(
                "/api/v1/music/preferences/genres/set/",
                {
                    "genre_ids": [
                        self.afrobeats.id,
                    ],
                },
                format="json",
            )
        )

        response = (
            UserGenrePreferenceSetAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTrue(
            UserGenrePreference.objects.filter(
                user=self.other_user,
                genre=self.gospel,
            ).exists()
        )

    def test_set_preferences_cannot_set_user_id(
        self,
    ):
        request = self.authenticate(
            self.factory.post(
                "/api/v1/music/preferences/genres/set/",
                {
                    "genre_ids": [
                        self.afrobeats.id,
                    ],
                    "user_id": self.other_user.id,
                },
                format="json",
            )
        )

        response = (
            UserGenrePreferenceSetAPIView.as_view()(
                request,
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTrue(
            UserGenrePreference.objects.filter(
                user=self.user,
                genre=self.afrobeats,
            ).exists()
        )

        self.assertFalse(
            UserGenrePreference.objects.filter(
                user=self.other_user,
                genre=self.afrobeats,
            ).exists()
        )