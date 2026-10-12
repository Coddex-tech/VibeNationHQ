from django.urls import resolve, reverse
from django.test import SimpleTestCase

from music.api.views.genre_preferences import (
    UserGenrePreferenceDeleteAPIView,
    UserGenrePreferenceListCreateAPIView,
    UserGenrePreferenceSetAPIView,
)


class UserGenrePreferenceURLTests(
    SimpleTestCase,
):
    def test_genre_preference_list_url(self):
        url = reverse(
            "music_api:genre-preference-list",
        )

        self.assertEqual(
            url,
            "/api/v1/music/preferences/genres/",
        )

        match = resolve(url)

        self.assertEqual(
            match.func.view_class,
            UserGenrePreferenceListCreateAPIView,
        )

    def test_genre_preference_delete_url(self):
        url = reverse(
            "music_api:genre-preference-delete",
            kwargs={
                "genre_id": 123,
            },
        )

        self.assertEqual(
            url,
            "/api/v1/music/preferences/genres/123/",
        )

        match = resolve(url)

        self.assertEqual(
            match.func.view_class,
            UserGenrePreferenceDeleteAPIView,
        )

    def test_genre_preference_set_url(self):
        url = reverse(
            "music_api:genre-preference-set",
        )

        self.assertEqual(
            url,
            "/api/v1/music/preferences/genres/set/",
        )

        match = resolve(url)

        self.assertEqual(
            match.func.view_class,
            UserGenrePreferenceSetAPIView,
        )

    def test_set_url_is_not_treated_as_genre_id(self):
        url = reverse(
            "music_api:genre-preference-set",
        )

        match = resolve(url)

        self.assertEqual(
            match.kwargs,
            {},
        )

        self.assertNotEqual(
            match.url_name,
            "genre-preference-delete",
        )