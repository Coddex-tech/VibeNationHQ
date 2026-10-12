from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from music.models import (
    Album,
    AlbumFavorite,
    AlbumRating,
    Artist,
    ArtistFollow,
    CommunityPost,
    CommunityPostTarget,
    Song,
    SongFavorite,
    SongRating,
)

User = get_user_model()


class TrendingSongsAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.trending_song = Song.objects.create(
            title="Trending Song",
            slug="trending-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.trending_song.artists.add(cls.artist)

        cls.untrending_song = Song.objects.create(
            title="Untrending Song",
            slug="untrending-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.untrending_song.artists.add(cls.artist)

        cls.draft_song = Song.objects.create(
            title="Draft Song",
            slug="draft-song",
            status=Song.Status.DRAFT,
        )

        cls.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )

        SongFavorite.objects.create(
            user=cls.user,
            song=cls.trending_song,
        )

    def test_returns_200(self):
        url = reverse("music_api:trending-songs")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_trending_song(self):
        url = reverse("music_api:trending-songs")

        response = self.client.get(url)

        returned_slugs = [
            song["slug"]
            for song in response.data
        ]

        self.assertIn(
            "trending-song",
            returned_slugs,
        )

    def test_excludes_songs_without_recent_activity(self):
        url = reverse("music_api:trending-songs")

        response = self.client.get(url)

        returned_slugs = [
            song["slug"]
            for song in response.data
        ]

        self.assertNotIn(
            "untrending-song",
            returned_slugs,
        )

    def test_excludes_unpublished_songs(self):
        url = reverse("music_api:trending-songs")

        response = self.client.get(url)

        returned_slugs = [
            song["slug"]
            for song in response.data
        ]

        self.assertNotIn(
            "draft-song",
            returned_slugs,
        )

    def test_uses_song_card_structure(self):
        url = reverse("music_api:trending-songs")

        response = self.client.get(url)

        song = response.data[0]

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


class TrendingAlbumsAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.trending_album = Album.objects.create(
            title="Trending Album",
            slug="trending-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.trending_album.artists.add(cls.artist)

        cls.untrending_album = Album.objects.create(
            title="Untrending Album",
            slug="untrending-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.untrending_album.artists.add(cls.artist)

        cls.draft_album = Album.objects.create(
            title="Draft Album",
            slug="draft-album",
            status=Album.Status.DRAFT,
        )

        cls.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )

        AlbumFavorite.objects.create(
            user=cls.user,
            album=cls.trending_album,
        )

    def test_returns_200(self):
        url = reverse("music_api:trending-albums")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_trending_album(self):
        url = reverse("music_api:trending-albums")

        response = self.client.get(url)

        returned_slugs = [
            album["slug"]
            for album in response.data
        ]

        self.assertIn(
            "trending-album",
            returned_slugs,
        )

    def test_excludes_untrending_albums(self):
        url = reverse("music_api:trending-albums")

        response = self.client.get(url)

        returned_slugs = [
            album["slug"]
            for album in response.data
        ]

        self.assertNotIn(
            "untrending-album",
            returned_slugs,
        )

    def test_excludes_unpublished_albums(self):
        url = reverse("music_api:trending-albums")

        response = self.client.get(url)

        returned_slugs = [
            album["slug"]
            for album in response.data
        ]

        self.assertNotIn(
            "draft-album",
            returned_slugs,
        )

    def test_uses_album_card_structure(self):
        url = reverse("music_api:trending-albums")

        response = self.client.get(url)

        album = response.data[0]

        self.assertIn("id", album)
        self.assertIn("title", album)
        self.assertIn("slug", album)
        self.assertIn("artists", album)
        self.assertIn("artwork", album)
        self.assertIn("release_date", album)
        self.assertIn("release_type", album)
        self.assertIn("favorites_count", album)
        self.assertIn("ratings_count", album)


class TrendingArtistsAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.trending_artist = Artist.objects.create(
            name="Trending Artist",
            slug="trending-artist",
            is_active=True,
        )

        cls.inactive_artist = Artist.objects.create(
            name="Inactive Artist",
            slug="inactive-artist",
            is_active=False,
        )

        cls.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )

        ArtistFollow.objects.create(
            user=cls.user,
            artist=cls.trending_artist,
        )

    def test_returns_200(self):
        url = reverse("music_api:trending-artists")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_trending_artist(self):
        url = reverse("music_api:trending-artists")

        response = self.client.get(url)

        returned_slugs = [
            artist["slug"]
            for artist in response.data
        ]

        self.assertIn(
            "trending-artist",
            returned_slugs,
        )

    def test_excludes_inactive_artists(self):
        url = reverse("music_api:trending-artists")

        response = self.client.get(url)

        returned_slugs = [
            artist["slug"]
            for artist in response.data
        ]

        self.assertNotIn(
            "inactive-artist",
            returned_slugs,
        )

    def test_uses_artist_card_structure(self):
        url = reverse("music_api:trending-artists")

        response = self.client.get(url)

        artist = response.data[0]

        self.assertIn("id", artist)
        self.assertIn("name", artist)
        self.assertIn("slug", artist)
        self.assertIn("profile_image", artist)
        self.assertIn("is_verified", artist)
        self.assertIn("followers_count", artist)


class MostFavoritedSongsAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.song_a = Song.objects.create(
            title="Popular Song",
            slug="popular-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.song_a.artists.add(cls.artist)

        cls.song_b = Song.objects.create(
            title="Less Popular Song",
            slug="less-popular-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.song_b.artists.add(cls.artist)

        cls.user_a = User.objects.create_user(
            username="user_a",
            password="password",
        )

        cls.user_b = User.objects.create_user(
            username="user_b",
            password="password",
        )

        cls.user_c = User.objects.create_user(
            username="user_c",
            password="password",
        )

        SongFavorite.objects.create(
            user=cls.user_a,
            song=cls.song_a,
        )

        SongFavorite.objects.create(
            user=cls.user_b,
            song=cls.song_a,
        )

        SongFavorite.objects.create(
            user=cls.user_c,
            song=cls.song_b,
        )

    def test_returns_200(self):
        url = reverse("music_api:most-favorited-songs")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_orders_by_favorite_count(self):
        url = reverse("music_api:most-favorited-songs")

        response = self.client.get(url)

        self.assertEqual(
            response.data[0]["slug"],
            "popular-song",
        )

    def test_excludes_songs_without_favorites(self):
        song = Song.objects.create(
            title="No Favorites",
            slug="no-favorites",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        song.artists.add(self.artist)

        url = reverse("music_api:most-favorited-songs")

        response = self.client.get(url)

        returned_slugs = [
            item["slug"]
            for item in response.data
        ]

        self.assertNotIn(
            "no-favorites",
            returned_slugs,
        )


class MostFavoritedAlbumsAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.album_a = Album.objects.create(
            title="Popular Album",
            slug="popular-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.album_a.artists.add(cls.artist)

        cls.album_b = Album.objects.create(
            title="Less Popular Album",
            slug="less-popular-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.album_b.artists.add(cls.artist)

        cls.user_a = User.objects.create_user(
            username="user_a",
            password="password",
        )

        cls.user_b = User.objects.create_user(
            username="user_b",
            password="password",
        )

        AlbumFavorite.objects.create(
            user=cls.user_a,
            album=cls.album_a,
        )

        AlbumFavorite.objects.create(
            user=cls.user_b,
            album=cls.album_a,
        )

    def test_returns_200(self):
        url = reverse("music_api:most-favorited-albums")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_favorited_albums(self):
        url = reverse("music_api:most-favorited-albums")

        response = self.client.get(url)

        returned_slugs = [
            album["slug"]
            for album in response.data
        ]

        self.assertIn(
            "popular-album",
            returned_slugs,
        )

    def test_orders_by_favorite_count(self):
        url = reverse("music_api:most-favorited-albums")

        response = self.client.get(url)

        self.assertEqual(
            response.data[0]["slug"],
            "popular-album",
        )

    def test_excludes_albums_without_favorites(self):
        url = reverse("music_api:most-favorited-albums")

        response = self.client.get(url)

        returned_slugs = [
            album["slug"]
            for album in response.data
        ]

        self.assertNotIn(
            "less-popular-album",
            returned_slugs,
        )


class TopRatedSongsAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.song_a = Song.objects.create(
            title="Highly Rated Song",
            slug="highly-rated-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.song_a.artists.add(cls.artist)

        cls.song_b = Song.objects.create(
            title="Lower Rated Song",
            slug="lower-rated-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.song_b.artists.add(cls.artist)

        cls.users = []

        for index in range(5):
            user = User.objects.create_user(
                username=f"user_{index}",
                password="password",
            )
            cls.users.append(user)

        for user in cls.users:
            SongRating.objects.create(
                user=user,
                song=cls.song_a,
                rating=5.0,
            )

        SongRating.objects.create(
            user=cls.users[0],
            song=cls.song_b,
            rating=3.0,
        )

        SongRating.objects.create(
            user=cls.users[1],
            song=cls.song_b,
            rating=3.0,
        )

        SongRating.objects.create(
            user=cls.users[2],
            song=cls.song_b,
            rating=3.0,
        )

        SongRating.objects.create(
            user=cls.users[3],
            song=cls.song_b,
            rating=3.0,
        )

        SongRating.objects.create(
            user=cls.users[4],
            song=cls.song_b,
            rating=3.0,
        )

    def test_returns_200(self):
        url = reverse("music_api:top-rated-songs")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_requires_minimum_number_of_ratings(self):
        song = Song.objects.create(
            title="Insufficient Ratings",
            slug="insufficient-ratings",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        song.artists.add(self.artist)

        SongRating.objects.create(
            user=self.users[0],
            song=song,
            rating=5.0,
        )

        url = reverse("music_api:top-rated-songs")

        response = self.client.get(url)

        returned_slugs = [
            item["slug"]
            for item in response.data
        ]

        self.assertNotIn(
            "insufficient-ratings",
            returned_slugs,
        )

    def test_orders_by_average_rating(self):
        url = reverse("music_api:top-rated-songs")

        response = self.client.get(url)

        self.assertEqual(
            response.data[0]["slug"],
            "highly-rated-song",
        )

    def test_includes_average_rating(self):
        url = reverse("music_api:top-rated-songs")

        response = self.client.get(url)

        song = response.data[0]

        self.assertIn(
            "average_rating",
            song,
        )

        self.assertEqual(
            song["average_rating"],
            5.0,
        )


class TopRatedAlbumsAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.album_a = Album.objects.create(
            title="Highly Rated Album",
            slug="highly-rated-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.album_a.artists.add(cls.artist)

        cls.album_b = Album.objects.create(
            title="Lower Rated Album",
            slug="lower-rated-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.album_b.artists.add(cls.artist)

        cls.users = []

        for index in range(5):
            user = User.objects.create_user(
                username=f"user_{index}",
                password="password",
            )
            cls.users.append(user)

        for user in cls.users:
            AlbumRating.objects.create(
                user=user,
                album=cls.album_a,
                rating=5.0,
            )

            AlbumRating.objects.create(
                user=user,
                album=cls.album_b,
                rating=3.0,
            )

    def test_returns_200(self):
        url = reverse("music_api:top-rated-albums")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_orders_by_average_rating(self):
        url = reverse("music_api:top-rated-albums")

        response = self.client.get(url)

        self.assertEqual(
            response.data[0]["slug"],
            "highly-rated-album",
        )

    def test_includes_average_rating(self):
        url = reverse("music_api:top-rated-albums")

        response = self.client.get(url)

        album = response.data[0]

        self.assertIn(
            "average_rating",
            album,
        )

        self.assertEqual(
            album["average_rating"],
            5.0,
        )


class FeaturedSongsAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.featured_song = Song.objects.create(
            title="Featured Song",
            slug="featured-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
            is_featured=True,
        )
        cls.featured_song.artists.add(cls.artist)

        cls.normal_song = Song.objects.create(
            title="Normal Song",
            slug="normal-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
            is_featured=False,
        )
        cls.normal_song.artists.add(cls.artist)

        cls.draft_song = Song.objects.create(
            title="Draft Featured Song",
            slug="draft-featured-song",
            status=Song.Status.DRAFT,
            is_featured=True,
        )

    def test_returns_200(self):
        url = reverse("music_api:featured-songs")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_featured_songs(self):
        url = reverse("music_api:featured-songs")

        response = self.client.get(url)

        returned_slugs = [
            song["slug"]
            for song in response.data
        ]

        self.assertIn(
            "featured-song",
            returned_slugs,
        )

    def test_excludes_non_featured_songs(self):
        url = reverse("music_api:featured-songs")

        response = self.client.get(url)

        returned_slugs = [
            song["slug"]
            for song in response.data
        ]

        self.assertNotIn(
            "normal-song",
            returned_slugs,
        )

    def test_excludes_unpublished_featured_songs(self):
        url = reverse("music_api:featured-songs")

        response = self.client.get(url)

        returned_slugs = [
            song["slug"]
            for song in response.data
        ]

        self.assertNotIn(
            "draft-featured-song",
            returned_slugs,
        )


class FeaturedAlbumsAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.featured_album = Album.objects.create(
            title="Featured Album",
            slug="featured-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
            is_featured=True,
        )
        cls.featured_album.artists.add(cls.artist)

        cls.normal_album = Album.objects.create(
            title="Normal Album",
            slug="normal-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
            is_featured=False,
        )
        cls.normal_album.artists.add(cls.artist)

    def test_returns_200(self):
        url = reverse("music_api:featured-albums")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_featured_albums(self):
        url = reverse("music_api:featured-albums")

        response = self.client.get(url)

        returned_slugs = [
            album["slug"]
            for album in response.data
        ]

        self.assertIn(
            "featured-album",
            returned_slugs,
        )

    def test_excludes_non_featured_albums(self):
        url = reverse("music_api:featured-albums")

        response = self.client.get(url)

        returned_slugs = [
            album["slug"]
            for album in response.data
        ]

        self.assertNotIn(
            "normal-album",
            returned_slugs,
        )


class FeaturedArtistsAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.verified_artist = Artist.objects.create(
            name="Verified Artist",
            slug="verified-artist",
            is_verified=True,
            is_active=True,
        )

        cls.unverified_artist = Artist.objects.create(
            name="Unverified Artist",
            slug="unverified-artist",
            is_verified=False,
            is_active=True,
        )

        cls.inactive_artist = Artist.objects.create(
            name="Inactive Artist",
            slug="inactive-artist",
            is_verified=True,
            is_active=False,
        )

    def test_returns_200(self):
        url = reverse("music_api:featured-artists")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_verified_artists(self):
        url = reverse("music_api:featured-artists")

        response = self.client.get(url)

        returned_slugs = [
            artist["slug"]
            for artist in response.data
        ]

        self.assertIn(
            "verified-artist",
            returned_slugs,
        )

    def test_excludes_unverified_artists(self):
        url = reverse("music_api:featured-artists")

        response = self.client.get(url)

        returned_slugs = [
            artist["slug"]
            for artist in response.data
        ]

        self.assertNotIn(
            "unverified-artist",
            returned_slugs,
        )

    def test_excludes_inactive_artists(self):
        url = reverse("music_api:featured-artists")

        response = self.client.get(url)

        returned_slugs = [
            artist["slug"]
            for artist in response.data
        ]

        self.assertNotIn(
            "inactive-artist",
            returned_slugs,
        )


class RecentlyReleasedSongsAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.recent_song = Song.objects.create(
            title="Recent Song",
            slug="recent-song",
            status=Song.Status.PUBLISHED,
            release_date=timezone.now().date(),
            published_at=timezone.now(),
        )
        cls.recent_song.artists.add(cls.artist)

        cls.old_song = Song.objects.create(
            title="Old Song",
            slug="old-song",
            status=Song.Status.PUBLISHED,
            release_date=timezone.now().date() - timedelta(days=30),
            published_at=timezone.now(),
        )
        cls.old_song.artists.add(cls.artist)

        cls.no_release_date_song = Song.objects.create(
            title="No Release Date",
            slug="no-release-date",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.no_release_date_song.artists.add(cls.artist)

    def test_returns_200(self):
        url = reverse("music_api:recently-released-songs")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_orders_by_release_date(self):
        url = reverse("music_api:recently-released-songs")

        response = self.client.get(url)

        self.assertEqual(
            response.data[0]["slug"],
            "recent-song",
        )

    def test_excludes_songs_without_release_date(self):
        url = reverse("music_api:recently-released-songs")

        response = self.client.get(url)

        returned_slugs = [
            song["slug"]
            for song in response.data
        ]

        self.assertNotIn(
            "no-release-date",
            returned_slugs,
        )


class RecentlyReleasedAlbumsAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.recent_album = Album.objects.create(
            title="Recent Album",
            slug="recent-album",
            status=Album.Status.PUBLISHED,
            release_date=timezone.now().date(),
            published_at=timezone.now(),
        )
        cls.recent_album.artists.add(cls.artist)

        cls.old_album = Album.objects.create(
            title="Old Album",
            slug="old-album",
            status=Album.Status.PUBLISHED,
            release_date=timezone.now().date() - timedelta(days=30),
            published_at=timezone.now(),
        )
        cls.old_album.artists.add(cls.artist)

        cls.no_release_date_album = Album.objects.create(
            title="No Release Date Album",
            slug="no-release-date-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.no_release_date_album.artists.add(cls.artist)

    def test_returns_200(self):
        url = reverse("music_api:recently-released-albums")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_orders_by_release_date(self):
        url = reverse("music_api:recently-released-albums")

        response = self.client.get(url)

        self.assertEqual(
            response.data[0]["slug"],
            "recent-album",
        )

    def test_excludes_albums_without_release_date(self):
        url = reverse("music_api:recently-released-albums")

        response = self.client.get(url)

        returned_slugs = [
            album["slug"]
            for album in response.data
        ]

        self.assertNotIn(
            "no-release-date-album",
            returned_slugs,
        )


class MostDiscussedSongsAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.song = Song.objects.create(
            title="Discussed Song",
            slug="discussed-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.song.artists.add(cls.artist)

        cls.user = User.objects.create_user(
            username="testuser",
            password="password",
        )

        cls.post = CommunityPost.objects.create(
            user=cls.user,
            content="This is a community discussion.",
            status=CommunityPost.Status.PUBLISHED,
        )

        CommunityPostTarget.objects.create(
            post=cls.post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=cls.song,
        )

    def test_returns_200(self):
        url = reverse("music_api:most-discussed-songs")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_discussed_song(self):
        url = reverse("music_api:most-discussed-songs")

        response = self.client.get(url)

        returned_slugs = [
            song["slug"]
            for song in response.data
        ]

        self.assertIn(
            "discussed-song",
            returned_slugs,
        )

    def test_excludes_songs_without_discussions(self):
        song = Song.objects.create(
            title="Undiscussed Song",
            slug="undiscussed-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        song.artists.add(self.artist)

        url = reverse("music_api:most-discussed-songs")

        response = self.client.get(url)

        returned_slugs = [
            song["slug"]
            for song in response.data
        ]

        self.assertNotIn(
            "undiscussed-song",
            returned_slugs,
        )


class MostDiscussedAlbumsAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.album = Album.objects.create(
            title="Discussed Album",
            slug="discussed-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.album.artists.add(cls.artist)

        cls.user = User.objects.create_user(
            username="testuser",
            password="password",
        )

        cls.post = CommunityPost.objects.create(
            user=cls.user,
            content="This is a community discussion.",
            status=CommunityPost.Status.PUBLISHED,
        )

        CommunityPostTarget.objects.create(
            post=cls.post,
            target_type=CommunityPostTarget.TargetType.ALBUM,
            album=cls.album,
        )

    def test_returns_200(self):
        url = reverse("music_api:most-discussed-albums")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_discussed_album(self):
        url = reverse("music_api:most-discussed-albums")

        response = self.client.get(url)

        returned_slugs = [
            album["slug"]
            for album in response.data
        ]

        self.assertIn(
            "discussed-album",
            returned_slugs,
        )

    def test_excludes_albums_without_discussions(self):
        album = Album.objects.create(
            title="Undiscussed Album",
            slug="undiscussed-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        album.artists.add(self.artist)

        url = reverse("music_api:most-discussed-albums")

        response = self.client.get(url)

        returned_slugs = [
            album["slug"]
            for album in response.data
        ]

        self.assertNotIn(
            "undiscussed-album",
            returned_slugs,
        )


class MusicDiscoveryAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Featured Artist",
            slug="featured-artist",
            is_verified=True,
            is_active=True,
        )

        cls.song = Song.objects.create(
            title="Featured Song",
            slug="featured-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
            release_date=timezone.now().date(),
            is_featured=True,
        )
        cls.song.artists.add(cls.artist)

        cls.album = Album.objects.create(
            title="Featured Album",
            slug="featured-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
            release_date=timezone.now().date(),
            is_featured=True,
        )
        cls.album.artists.add(cls.artist)

    def test_returns_200(self):
        url = reverse("music_api:discovery")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_returns_all_discovery_sections(self):
        url = reverse("music_api:discovery")

        response = self.client.get(url)

        expected_sections = [
            "trending_songs",
            "trending_albums",
            "trending_artists",
            "most_discussed_songs",
            "most_discussed_albums",
            "most_favorited_songs",
            "most_favorited_albums",
            "top_rated_songs",
            "top_rated_albums",
            "featured_songs",
            "featured_albums",
            "featured_artists",
            "recently_released_songs",
            "recently_released_albums",
        ]

        for section in expected_sections:
            self.assertIn(
                section,
                response.data,
            )

    def test_featured_songs_are_included(self):
        url = reverse("music_api:discovery")

        response = self.client.get(url)

        returned_slugs = [
            song["slug"]
            for song in response.data["featured_songs"]
        ]

        self.assertIn(
            "featured-song",
            returned_slugs,
        )

    def test_featured_albums_are_included(self):
        url = reverse("music_api:discovery")

        response = self.client.get(url)

        returned_slugs = [
            album["slug"]
            for album in response.data["featured_albums"]
        ]

        self.assertIn(
            "featured-album",
            returned_slugs,
        )

    def test_featured_artists_are_included(self):
        url = reverse("music_api:discovery")

        response = self.client.get(url)

        returned_slugs = [
            artist["slug"]
            for artist in response.data["featured_artists"]
        ]

        self.assertIn(
            "featured-artist",
            returned_slugs,
        )

    def test_response_sections_are_lists(self):
        url = reverse("music_api:discovery")

        response = self.client.get(url)

        for section_name, section_data in response.data.items():
            self.assertIsInstance(
                section_data,
                list,
                msg=f"{section_name} should be a list.",
            )