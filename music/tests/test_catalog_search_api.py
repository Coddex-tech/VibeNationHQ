from __future__ import annotations

from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from music.models import Album, Artist, Song


class MusicCatalogSearchAPITests(APITestCase):
    endpoint = "/api/v1/music/catalog/search/"

    def setUp(self):
        self.burna_boy = Artist.objects.create(
            name="Burna Boy",
            slug="burna-boy",
            country="Nigeria",
        )

        self.wizkid = Artist.objects.create(
            name="Wizkid",
            slug="wizkid",
            country="Nigeria",
        )

        self.tems = Artist.objects.create(
            name="Tems",
            slug="tems",
            country="Nigeria",
        )

        self.love_damini = Album.objects.create(
            title="Love, Damini",
            slug="love-damini",
            release_date=date(2022, 7, 8),
        )
        self.love_damini.artists.add(
            self.burna_boy,
        )

        self.made_in_lagos = Album.objects.create(
            title="Made in Lagos",
            slug="made-in-lagos",
            release_date=date(2020, 10, 30),
        )
        self.made_in_lagos.artists.add(
            self.wizkid,
        )

        self.last_last = Song.objects.create(
            title="Last Last",
            slug="last-last",
            album=self.love_damini,
            release_date=date(2022, 5, 13),
            duration_seconds=175,
        )
        self.last_last.artists.add(
            self.burna_boy,
        )

        self.essence = Song.objects.create(
            title="Essence",
            slug="essence",
            album=self.made_in_lagos,
            release_date=date(2020, 10, 30),
            duration_seconds=244,
        )
        self.essence.artists.add(
            self.wizkid,
        )
        self.essence.featured_artists.add(
            self.tems,
        )

    def test_search_songs_by_title(self):
        response = self.client.get(
            self.endpoint,
            {
                "q": "Last Last",
                "type": "song",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        result = response.data["results"][0]

        self.assertEqual(
            result["entity_type"],
            "song",
        )
        self.assertEqual(
            result["id"],
            self.last_last.id,
        )
        self.assertEqual(
            result["title"],
            "Last Last",
        )

    def test_search_artists_by_name(self):
        response = self.client.get(
            self.endpoint,
            {
                "q": "Burna Boy",
                "type": "artist",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        result = response.data["results"][0]

        self.assertEqual(
            result["entity_type"],
            "artist",
        )
        self.assertEqual(
            result["id"],
            self.burna_boy.id,
        )
        self.assertEqual(
            result["title"],
            "Burna Boy",
        )

    def test_search_albums_by_title(self):
        response = self.client.get(
            self.endpoint,
            {
                "q": "Love, Damini",
                "type": "album",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        result = response.data["results"][0]

        self.assertEqual(
            result["entity_type"],
            "album",
        )
        self.assertEqual(
            result["id"],
            self.love_damini.id,
        )
        self.assertEqual(
            result["title"],
            "Love, Damini",
        )

    def test_search_without_entity_type_searches_all_types(self):
        response = self.client.get(
            self.endpoint,
            {
                "q": "Burna Boy",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        result_types = {
            result["entity_type"]
            for result in response.data["results"]
        }

        self.assertIn(
            "song",
            result_types,
        )
        self.assertIn(
            "artist",
            result_types,
        )
        self.assertIn(
            "album",
            result_types,
        )

    def test_empty_query_returns_empty_results(self):
        response = self.client.get(
            self.endpoint,
            {
                "q": "",
                "type": "song",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["results"],
            [],
        )

    def test_whitespace_query_returns_empty_results(self):
        response = self.client.get(
            self.endpoint,
            {
                "q": "   ",
                "type": "song",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["results"],
            [],
        )

    def test_invalid_entity_type_returns_400(self):
        response = self.client.get(
            self.endpoint,
            {
                "q": "Burna Boy",
                "type": "playlist",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "Invalid entity type",
            response.data["detail"],
        )

    def test_invalid_limit_returns_400(self):
        response = self.client.get(
            self.endpoint,
            {
                "q": "Burna Boy",
                "limit": "abc",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["detail"],
            "Limit must be a valid integer.",
        )

    def test_limit_is_applied(self):
        response = self.client.get(
            self.endpoint,
            {
                "q": "e",
                "type": "song",
                "limit": 1,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(response.data["results"]),
            1,
        )

    def test_limit_cannot_exceed_service_maximum(self):
        response = self.client.get(
            self.endpoint,
            {
                "q": "e",
                "type": "song",
                "limit": 1000,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertLessEqual(
            len(response.data["results"]),
            20,
        )

    def test_zero_limit_is_normalized_to_one(self):
        response = self.client.get(
            self.endpoint,
            {
                "q": "e",
                "type": "song",
                "limit": 0,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertLessEqual(
            len(response.data["results"]),
            1,
        )

    def test_query_longer_than_maximum_returns_400(self):
        response = self.client.get(
            self.endpoint,
            {
                "q": "a" * 201,
                "type": "song",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["detail"],
            "Search query is too long.",
        )

    def test_search_does_not_create_or_modify_records(self):
        artist_count = Artist.objects.count()
        album_count = Album.objects.count()
        song_count = Song.objects.count()

        response = self.client.get(
            self.endpoint,
            {
                "q": "Burna Boy",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            Artist.objects.count(),
            artist_count,
        )
        self.assertEqual(
            Album.objects.count(),
            album_count,
        )
        self.assertEqual(
            Song.objects.count(),
            song_count,
        )