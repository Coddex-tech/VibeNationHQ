from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from music.models import (
    Album,
    Artist,
    Genre,
    Song,
)


User = get_user_model()


class MusicSearchAPITest(APITestCase):

    def setUp(self):
        self.artist = Artist.objects.create(
            name="Tems",
            slug="tems",
            is_active=True,
        )

        self.other_artist = Artist.objects.create(
            name="Davido",
            slug="davido",
            is_active=True,
        )

        self.genre = Genre.objects.create(
            name="Afrobeats",
            slug="afrobeats",
            is_active=True,
        )

        self.album = Album.objects.create(
            title="Born in the Wild",
            slug="born-in-the-wild",
            release_type=Album.ReleaseType.ALBUM,
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.album.artists.add(self.artist)

        self.song = Song.objects.create(
            title="Me & U",
            slug="me-and-u",
            album=self.album,
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.song.artists.add(self.artist)
        self.song.genres.add(self.genre)

        self.unpublished_song = Song.objects.create(
            title="Tems Unreleased Song",
            slug="tems-unreleased-song",
            status=Song.Status.DRAFT,
        )

        self.inactive_artist = Artist.objects.create(
            name="Tems Inactive",
            slug="tems-inactive",
            is_active=False,
        )

        self.unpublished_album = Album.objects.create(
            title="Tems Unreleased Album",
            slug="tems-unreleased-album",
            status=Album.Status.DRAFT,
        )

    # ========================================================
    # BASIC SEARCH
    # ========================================================

    def test_search_returns_matching_song(self):
        response = self.client.get(
            "/api/v1/music/search/?q=Me"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["query"],
            "Me",
        )

        self.assertEqual(
            len(response.data["songs"]),
            1,
        )

        self.assertEqual(
            response.data["songs"][0]["title"],
            "Me & U",
        )

    def test_search_returns_matching_artist(self):
        response = self.client.get(
            "/api/v1/music/search/?q=Tems"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.data["artists"]),
            1,
        )

        self.assertEqual(
            response.data["artists"][0]["name"],
            "Tems",
        )

    def test_search_returns_matching_album(self):
        response = self.client.get(
            "/api/v1/music/search/?q=Born"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.data["albums"]),
            1,
        )

        self.assertEqual(
            response.data["albums"][0]["title"],
            "Born in the Wild",
        )

    def test_search_returns_matching_genre(self):
        response = self.client.get(
            "/api/v1/music/search/?q=Afro"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.data["genres"]),
            1,
        )

        self.assertEqual(
            response.data["genres"][0]["name"],
            "Afrobeats",
        )

    # ========================================================
    # CROSS ENTITY SEARCH
    # ========================================================

    def test_artist_search_also_finds_artist_songs_and_albums(self):
        response = self.client.get(
            "/api/v1/music/search/?q=Tems"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.data["artists"]),
            1,
        )

        self.assertEqual(
            len(response.data["songs"]),
            1,
        )

        self.assertEqual(
            len(response.data["albums"]),
            1,
        )

    # ========================================================
    # CASE INSENSITIVE
    # ========================================================

    def test_search_is_case_insensitive(self):
        response = self.client.get(
            "/api/v1/music/search/?q=tEmS"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.data["artists"]),
            1,
        )

    # ========================================================
    # EMPTY / INVALID QUERY
    # ========================================================

    def test_missing_query_is_rejected(self):
        response = self.client.get(
            "/api/v1/music/search/"
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_empty_query_is_rejected(self):
        response = self.client.get(
            "/api/v1/music/search/?q="
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_one_character_query_is_rejected(self):
        response = self.client.get(
            "/api/v1/music/search/?q=a"
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_whitespace_query_is_rejected(self):
        response = self.client.get(
            "/api/v1/music/search/?q=%20%20"
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    # ========================================================
    # PUBLICATION / ACTIVE FILTERING
    # ========================================================

    def test_unpublished_song_is_not_returned(self):
        response = self.client.get(
            "/api/v1/music/search/?q=Unreleased"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.data["songs"]),
            0,
        )

    def test_inactive_artist_is_not_returned(self):
        response = self.client.get(
            "/api/v1/music/search/?q=Inactive"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.data["artists"]),
            0,
        )

    def test_unpublished_album_is_not_returned(self):
        response = self.client.get(
            "/api/v1/music/search/?q=Unreleased"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.data["albums"]),
            0,
        )

    # ========================================================
    # NO RESULTS
    # ========================================================

    def test_no_results_returns_empty_lists(self):
        response = self.client.get(
            "/api/v1/music/search/?q=xxxxxxxx"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["songs"],
            [],
        )

        self.assertEqual(
            response.data["artists"],
            [],
        )

        self.assertEqual(
            response.data["albums"],
            [],
        )

        self.assertEqual(
            response.data["genres"],
            [],
        )

    # ========================================================
    # ANONYMOUS ACCESS
    # ========================================================

    def test_anonymous_user_can_search(self):
        response = self.client.get(
            "/api/v1/music/search/?q=Tems"
        )

        self.assertEqual(
            response.status_code,
            200,
        )