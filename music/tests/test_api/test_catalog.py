from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from music.models import (
    Artist,
    Genre,
    Song,
    Album,
    AlbumTrack
)


class SongListAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.featured_artist = Artist.objects.create(
            name="Featured Artist",
            slug="featured-artist",
            is_active=True,
        )

        cls.genre = Genre.objects.create(
            name="Afrobeats",
            slug="afrobeats",
            is_active=True,
        )

        cls.published_song = Song.objects.create(
            title="Published Song",
            slug="published-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.published_song.artists.add(cls.artist)
        cls.published_song.featured_artists.add(cls.featured_artist)
        cls.published_song.genres.add(cls.genre)

        cls.unpublished_song = Song.objects.create(
            title="Draft Song",
            slug="draft-song",
            status=Song.Status.DRAFT,
        )

    def test_returns_200(self):
        url = reverse("music_api:song-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_published_songs(self):
        url = reverse("music_api:song-list")

        response = self.client.get(url)

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            response.data["results"][0]["title"],
            "Published Song",
        )

    def test_excludes_unpublished_songs(self):
        url = reverse("music_api:song-list")

        response = self.client.get(url)

        returned_slugs = [
            song["slug"]
            for song in response.data["results"]
        ]

        self.assertIn(
            "published-song",
            returned_slugs,
        )

        self.assertNotIn(
            "draft-song",
            returned_slugs,
        )

    def test_uses_song_card_structure(self):
        url = reverse("music_api:song-list")

        response = self.client.get(url)

        song = response.data["results"][0]

        self.assertIn("id", song)
        self.assertIn("title", song)
        self.assertIn("slug", song)
        self.assertIn("artists", song)
        self.assertIn("featured_artists", song)
        self.assertIn("artwork", song)
        self.assertIn("release_date", song)
        self.assertIn("duration_seconds", song)
        self.assertIn("duration_display", song)
        self.assertIn("favorites_count", song)
        self.assertIn("ratings_count", song)

    def test_pagination_first_page_returns_20_songs(self):
        now = timezone.now()

        for index in range(20):
            song = Song.objects.create(
                title=f"Pagination Song {index}",
                slug=f"pagination-song-{index}",
                status=Song.Status.PUBLISHED,
                published_at=now + timedelta(seconds=index + 1),
            )

            song.artists.add(self.artist)
            song.genres.add(self.genre)

        url = reverse("music_api:song-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            21,
        )

        self.assertEqual(
            len(response.data["results"]),
            20,
        )

        self.assertIsNotNone(
            response.data["next"],
        )

        self.assertIsNone(
            response.data["previous"],
        )

    def test_pagination_second_page_returns_remaining_song(self):
        now = timezone.now()

        for index in range(20):
            song = Song.objects.create(
                title=f"Pagination Song {index}",
                slug=f"pagination-song-{index}",
                status=Song.Status.PUBLISHED,
                published_at=now + timedelta(seconds=index + 1),
            )

            song.artists.add(self.artist)
            song.genres.add(self.genre)

        url = reverse("music_api:song-list")

        response = self.client.get(
            url,
            {"page": 2},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            21,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertIsNotNone(
            response.data["previous"],
        )

        self.assertIsNone(
            response.data["next"],
        )

    def test_pagination_preserves_all_songs_across_pages(self):
        now = timezone.now()

        for index in range(20):
            song = Song.objects.create(
                title=f"Pagination Song {index}",
                slug=f"pagination-song-{index}",
                status=Song.Status.PUBLISHED,
                published_at=now + timedelta(seconds=index + 1),
            )

            song.artists.add(self.artist)
            song.genres.add(self.genre)

        url = reverse("music_api:song-list")

        first_page = self.client.get(url)
        second_page = self.client.get(
            url,
            {"page": 2},
        )

        first_page_slugs = {
            song["slug"]
            for song in first_page.data["results"]
        }

        second_page_slugs = {
            song["slug"]
            for song in second_page.data["results"]
        }

        self.assertEqual(
            len(first_page_slugs),
            20,
        )

        self.assertEqual(
            len(second_page_slugs),
            1,
        )

        self.assertTrue(
            first_page_slugs.isdisjoint(second_page_slugs),
        )

        self.assertEqual(
            len(first_page_slugs | second_page_slugs),
            21,
        )


class SongDetailAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.featured_artist = Artist.objects.create(
            name="Featured Artist",
            slug="featured-artist",
            is_active=True,
        )

        cls.genre = Genre.objects.create(
            name="Afrobeats",
            slug="afrobeats",
            is_active=True,
        )

        cls.song = Song.objects.create(
            title="Test Song",
            slug="test-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.song.artists.add(cls.artist)
        cls.song.featured_artists.add(cls.featured_artist)
        cls.song.genres.add(cls.genre)

    def test_returns_200_for_published_song(self):
        url = reverse(
            "music_api:song-detail",
            kwargs={"slug": self.song.slug},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_correct_song(self):
        url = reverse(
            "music_api:song-detail",
            kwargs={"slug": self.song.slug},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.data["slug"],
            "test-song",
        )

        self.assertEqual(
            response.data["title"],
            "Test Song",
        )

    def test_serializes_nested_artists(self):
        url = reverse(
            "music_api:song-detail",
            kwargs={"slug": self.song.slug},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.data["artists"][0]["name"],
            "Test Artist",
        )

        self.assertEqual(
            response.data["featured_artists"][0]["name"],
            "Featured Artist",
        )

    def test_serializes_nested_genres(self):
        url = reverse(
            "music_api:song-detail",
            kwargs={"slug": self.song.slug},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.data["genres"][0]["name"],
            "Afrobeats",
        )

    def test_unpublished_song_returns_404(self):
        unpublished_song = Song.objects.create(
            title="Draft Song",
            slug="draft-song",
            status=Song.Status.DRAFT,
        )

        url = reverse(
            "music_api:song-detail",
            kwargs={"slug": unpublished_song.slug},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_nonexistent_song_returns_404(self):
        url = reverse(
            "music_api:song-detail",
            kwargs={"slug": "does-not-exist"},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )


class AlbumListAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.published_album = Album.objects.create(
            title="Published Album",
            slug="published-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.published_album.artists.add(cls.artist)

        cls.draft_album = Album.objects.create(
            title="Draft Album",
            slug="draft-album",
            status=Album.Status.DRAFT,
        )

        cls.archived_album = Album.objects.create(
            title="Archived Album",
            slug="archived-album",
            status=Album.Status.ARCHIVED,
        )

    def test_returns_200(self):
        url = reverse("music_api:album-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_published_albums(self):
        url = reverse("music_api:album-list")

        response = self.client.get(url)

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            response.data["results"][0]["title"],
            "Published Album",
        )

    def test_excludes_unpublished_albums(self):
        url = reverse("music_api:album-list")

        response = self.client.get(url)

        returned_slugs = [
            album["slug"]
            for album in response.data["results"]
        ]

        self.assertIn(
            "published-album",
            returned_slugs,
        )

        self.assertNotIn(
            "draft-album",
            returned_slugs,
        )

        self.assertNotIn(
            "archived-album",
            returned_slugs,
        )

    def test_uses_album_card_structure(self):
        url = reverse("music_api:album-list")

        response = self.client.get(url)

        album = response.data["results"][0]

        self.assertIn("id", album)
        self.assertIn("title", album)
        self.assertIn("slug", album)
        self.assertIn("artists", album)
        self.assertIn("artwork", album)
        self.assertIn("release_date", album)
        self.assertIn("release_type", album)
        self.assertIn("favorites_count", album)
        self.assertIn("ratings_count", album)


class AlbumDetailAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.featured_artist = Artist.objects.create(
            name="Featured Artist",
            slug="featured-artist",
            is_active=True,
        )

        cls.album = Album.objects.create(
            title="Test Album",
            slug="test-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.album.artists.add(cls.artist)

        cls.song_1 = Song.objects.create(
            title="First Song",
            slug="first-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.song_2 = Song.objects.create(
            title="Second Song",
            slug="second-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.song_3 = Song.objects.create(
            title="Third Song",
            slug="third-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.song_1.artists.add(cls.artist)
        cls.song_2.artists.add(cls.artist)
        cls.song_3.artists.add(cls.artist)

        cls.song_2.featured_artists.add(cls.featured_artist)

        AlbumTrack.objects.create(
            album=cls.album,
            song=cls.song_1,
            track_number=1,
        )

        AlbumTrack.objects.create(
            album=cls.album,
            song=cls.song_2,
            track_number=2,
        )

        AlbumTrack.objects.create(
            album=cls.album,
            song=cls.song_3,
            track_number=3,
        )

        cls.draft_album = Album.objects.create(
            title="Draft Album",
            slug="draft-album",
            status=Album.Status.DRAFT,
        )

        cls.archived_album = Album.objects.create(
            title="Archived Album",
            slug="archived-album",
            status=Album.Status.ARCHIVED,
        )

    def test_returns_200(self):
        url = reverse(
            "music_api:album-detail",
            kwargs={"slug": "test-album"},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_retrieves_album_by_slug(self):
        url = reverse(
            "music_api:album-detail",
            kwargs={"slug": "test-album"},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.data["slug"],
            "test-album",
        )

        self.assertEqual(
            response.data["title"],
            "Test Album",
        )

    def test_uses_album_detail_structure(self):
        url = reverse(
            "music_api:album-detail",
            kwargs={"slug": "test-album"},
        )

        response = self.client.get(url)

        self.assertIn("id", response.data)
        self.assertIn("title", response.data)
        self.assertIn("slug", response.data)
        self.assertIn("artists", response.data)
        self.assertIn("tracks", response.data)

    def test_includes_album_tracks(self):
        url = reverse(
            "music_api:album-detail",
            kwargs={"slug": "test-album"},
        )

        response = self.client.get(url)

        self.assertEqual(
            len(response.data["tracks"]),
            3,
        )

    def test_tracks_are_ordered_by_track_number(self):
        url = reverse(
            "music_api:album-detail",
            kwargs={"slug": "test-album"},
        )

        response = self.client.get(url)

        tracks = response.data["tracks"]

        self.assertEqual(
            [track["track_number"] for track in tracks],
            [1, 2, 3],
        )

        self.assertEqual(
            tracks[0]["song"]["title"],
            "First Song",
        )

        self.assertEqual(
            tracks[1]["song"]["title"],
            "Second Song",
        )

        self.assertEqual(
            tracks[2]["song"]["title"],
            "Third Song",
        )

    def test_excludes_draft_album(self):
        url = reverse(
            "music_api:album-detail",
            kwargs={"slug": "draft-album"},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_excludes_archived_album(self):
        url = reverse(
            "music_api:album-detail",
            kwargs={"slug": "archived-album"},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_unknown_album_returns_404(self):
        url = reverse(
            "music_api:album-detail",
            kwargs={"slug": "does-not-exist"},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )


class ArtistListAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist_a = Artist.objects.create(
            name="Artist Alpha",
            slug="artist-alpha",
            is_active=True,
        )

        cls.artist_b = Artist.objects.create(
            name="Artist Beta",
            slug="artist-beta",
            is_active=True,
        )

        cls.inactive_artist = Artist.objects.create(
            name="Inactive Artist",
            slug="inactive-artist",
            is_active=False,
        )

    def test_returns_200(self):
        url = reverse("music_api:artist-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_active_artists(self):
        url = reverse("music_api:artist-list")

        response = self.client.get(url)

        self.assertEqual(
            response.data["count"],
            2,
        )

        self.assertEqual(
            len(response.data["results"]),
            2,
        )

    def test_excludes_inactive_artists(self):
        url = reverse("music_api:artist-list")

        response = self.client.get(url)

        returned_slugs = [
            artist["slug"]
            for artist in response.data["results"]
        ]

        self.assertIn(
            "artist-alpha",
            returned_slugs,
        )

        self.assertIn(
            "artist-beta",
            returned_slugs,
        )

        self.assertNotIn(
            "inactive-artist",
            returned_slugs,
        )

    def test_artists_are_ordered_by_name(self):
        url = reverse("music_api:artist-list")

        response = self.client.get(url)

        returned_names = [
            artist["name"]
            for artist in response.data["results"]
        ]

        self.assertEqual(
            returned_names,
            [
                "Artist Alpha",
                "Artist Beta",
            ],
        )

    def test_uses_artist_card_structure(self):
        url = reverse("music_api:artist-list")

        response = self.client.get(url)

        artist = response.data["results"][0]

        self.assertIn("id", artist)
        self.assertIn("name", artist)
        self.assertIn("slug", artist)
        self.assertIn("profile_image", artist)
        self.assertIn("is_verified", artist)
        self.assertIn("followers_count", artist)


class ArtistDetailAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            bio="A test artist biography.",
            country="Nigeria",
            is_verified=True,
            is_active=True,
        )

        cls.inactive_artist = Artist.objects.create(
            name="Inactive Artist",
            slug="inactive-artist",
            is_active=False,
        )

    def test_returns_200(self):
        url = reverse(
            "music_api:artist-detail",
            kwargs={"slug": "test-artist"},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_retrieves_artist_by_slug(self):
        url = reverse(
            "music_api:artist-detail",
            kwargs={"slug": "test-artist"},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.data["slug"],
            "test-artist",
        )

        self.assertEqual(
            response.data["name"],
            "Test Artist",
        )

    def test_uses_artist_detail_structure(self):
        url = reverse(
            "music_api:artist-detail",
            kwargs={"slug": "test-artist"},
        )

        response = self.client.get(url)

        self.assertIn("id", response.data)
        self.assertIn("name", response.data)
        self.assertIn("slug", response.data)
        self.assertIn("bio", response.data)
        self.assertIn("country", response.data)
        self.assertIn("is_verified", response.data)

    def test_returns_artist_details(self):
        url = reverse(
            "music_api:artist-detail",
            kwargs={"slug": "test-artist"},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.data["bio"],
            "A test artist biography.",
        )

        self.assertEqual(
            response.data["country"],
            "Nigeria",
        )

        self.assertTrue(
            response.data["is_verified"],
        )

    def test_excludes_inactive_artist(self):
        url = reverse(
            "music_api:artist-detail",
            kwargs={"slug": "inactive-artist"},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_unknown_artist_returns_404(self):
        url = reverse(
            "music_api:artist-detail",
            kwargs={"slug": "does-not-exist"},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )


class GenreListAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.genre_a = Genre.objects.create(
            name="Afrobeats",
            slug="afrobeats",
            is_active=True,
        )

        cls.genre_b = Genre.objects.create(
            name="Hip Hop",
            slug="hip-hop",
            is_active=True,
        )

        cls.inactive_genre = Genre.objects.create(
            name="Inactive Genre",
            slug="inactive-genre",
            is_active=False,
        )

    def test_returns_200(self):
        url = reverse("music_api:genre-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_active_genres(self):
        url = reverse("music_api:genre-list")

        response = self.client.get(url)

        self.assertEqual(
            response.data["count"],
            2,
        )

        self.assertEqual(
            len(response.data["results"]),
            2,
        )

    def test_excludes_inactive_genres(self):
        url = reverse("music_api:genre-list")

        response = self.client.get(url)

        returned_slugs = [
            genre["slug"]
            for genre in response.data["results"]
        ]

        self.assertIn(
            "afrobeats",
            returned_slugs,
        )

        self.assertIn(
            "hip-hop",
            returned_slugs,
        )

        self.assertNotIn(
            "inactive-genre",
            returned_slugs,
        )

    def test_genres_are_ordered_by_name(self):
        url = reverse("music_api:genre-list")

        response = self.client.get(url)

        returned_names = [
            genre["name"]
            for genre in response.data["results"]
        ]

        self.assertEqual(
            returned_names,
            [
                "Afrobeats",
                "Hip Hop",
            ],
        )

    def test_uses_genre_serializer_structure(self):
        url = reverse("music_api:genre-list")

        response = self.client.get(url)

        genre = response.data["results"][0]

        self.assertIn("id", genre)
        self.assertIn("name", genre)
        self.assertIn("slug", genre)