from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from music.models import (
    Album,
    AlbumFavorite,
    AlbumRating,
    Artist,
    CommunityPost,
    CommunityPostTarget,
    Song,
    SongFavorite,
    SongRating,
)
from music.services.discovery import DiscoveryService


User = get_user_model()


class DiscoveryServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="test-password",
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="test-password",
        )

        self.artist = Artist.objects.create(
            name="Burna Boy",
            slug="burna-boy",
            is_active=True,
        )

        self.second_artist = Artist.objects.create(
            name="Wizkid",
            slug="wizkid",
            is_active=True,
        )

        self.album = Album.objects.create(
            title="Love, Damini",
            slug="love-damini",
            status=Album.Status.PUBLISHED,
            release_date=timezone.now().date(),
            published_at=timezone.now(),
        )

        self.album.artists.add(self.artist)

        self.song = Song.objects.create(
            title="Last Last",
            slug="last-last",
            status=Song.Status.PUBLISHED,
            release_date=timezone.now().date(),
            published_at=timezone.now(),
            album=self.album,
        )

        self.song.artists.add(self.artist)

        self.second_song = Song.objects.create(
            title="Essence",
            slug="essence",
            status=Song.Status.PUBLISHED,
            release_date=(
                timezone.now().date()
                - timedelta(days=1)
            ),
            published_at=(
                timezone.now()
                - timedelta(days=1)
            ),
        )

        self.second_song.artists.add(
            self.second_artist,
        )

    # ========================================================
    # TRENDING SONGS
    # ========================================================

    def test_trending_songs_returns_recently_engaged_songs(self):
        SongFavorite.objects.create(
            user=self.user,
            song=self.song,
        )

        results = list(
            DiscoveryService.trending_songs()
        )

        self.assertIn(
            self.song,
            results,
        )

    def test_trending_songs_ignores_old_engagement(self):
        favorite = SongFavorite.objects.create(
            user=self.user,
            song=self.song,
        )

        SongFavorite.objects.filter(
            pk=favorite.pk,
        ).update(
            created_at=(
                timezone.now()
                - timedelta(days=DiscoveryService.TRENDING_DAYS + 1)
            )
        )

        results = list(
            DiscoveryService.trending_songs()
        )

        self.assertNotIn(
            self.song,
            results,
        )

    def test_trending_songs_ignores_unpublished_songs(self):
        self.song.status = Song.Status.DRAFT
        self.song.save(
            update_fields=["status"],
        )

        SongFavorite.objects.create(
            user=self.user,
            song=self.song,
        )

        results = list(
            DiscoveryService.trending_songs()
        )

        self.assertNotIn(
            self.song,
            results,
        )

    def test_trending_songs_uses_recent_discussions(self):
        post = CommunityPost.objects.create(
            user=self.user,
            content="Great song.",
            status=CommunityPost.Status.PUBLISHED,
        )

        CommunityPostTarget.objects.create(
            post=post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=self.song,
        )

        results = list(
            DiscoveryService.trending_songs()
        )

        self.assertIn(
            self.song,
            results,
        )

    # ========================================================
    # TRENDING ALBUMS
    # ========================================================

    def test_trending_albums_returns_recently_engaged_albums(self):
        AlbumFavorite.objects.create(
            user=self.user,
            album=self.album,
        )

        results = list(
            DiscoveryService.trending_albums()
        )

        self.assertIn(
            self.album,
            results,
        )

    def test_trending_albums_ignores_unpublished_albums(self):
        self.album.status = Album.Status.DRAFT
        self.album.save(
            update_fields=["status"],
        )

        AlbumFavorite.objects.create(
            user=self.user,
            album=self.album,
        )

        results = list(
            DiscoveryService.trending_albums()
        )

        self.assertNotIn(
            self.album,
            results,
        )

    # ========================================================
    # TRENDING ARTISTS
    # ========================================================

    def test_trending_artists_returns_recently_followed_artists(self):
        self.artist.followers.create(
            user=self.user,
        )

        results = list(
            DiscoveryService.trending_artists()
        )

        self.assertIn(
            self.artist,
            results,
        )

    def test_trending_artists_ignores_inactive_artists(self):
        self.artist.is_active = False
        self.artist.save(
            update_fields=["is_active"],
        )

        self.artist.followers.create(
            user=self.user,
        )

        results = list(
            DiscoveryService.trending_artists()
        )

        self.assertNotIn(
            self.artist,
            results,
        )

    # ========================================================
    # MOST DISCUSSED
    # ========================================================

    def test_most_discussed_songs_returns_discussed_songs(self):
        post = CommunityPost.objects.create(
            user=self.user,
            content="Let's discuss this track.",
            status=CommunityPost.Status.PUBLISHED,
        )

        CommunityPostTarget.objects.create(
            post=post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=self.song,
        )

        results = list(
            DiscoveryService.most_discussed_songs()
        )

        self.assertIn(
            self.song,
            results,
        )

    def test_most_discussed_songs_ignores_unpublished_posts(self):
        post = CommunityPost.objects.create(
            user=self.user,
            content="Hidden discussion.",
            status=CommunityPost.Status.HIDDEN,
        )

        CommunityPostTarget.objects.create(
            post=post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=self.song,
        )

        results = list(
            DiscoveryService.most_discussed_songs()
        )

        self.assertNotIn(
            self.song,
            results,
        )

    def test_most_discussed_albums_returns_discussed_albums(self):
        post = CommunityPost.objects.create(
            user=self.user,
            content="Album discussion.",
            status=CommunityPost.Status.PUBLISHED,
        )

        CommunityPostTarget.objects.create(
            post=post,
            target_type=CommunityPostTarget.TargetType.ALBUM,
            album=self.album,
        )

        results = list(
            DiscoveryService.most_discussed_albums()
        )

        self.assertIn(
            self.album,
            results,
        )

    # ========================================================
    # MOST FAVOURITED
    # ========================================================

    def test_most_favorited_songs_returns_favorited_songs(self):
        SongFavorite.objects.create(
            user=self.user,
            song=self.song,
        )

        results = list(
            DiscoveryService.most_favorited_songs()
        )

        self.assertIn(
            self.song,
            results,
        )

    def test_most_favorited_songs_uses_actual_favorite_count(self):
        SongFavorite.objects.create(
            user=self.user,
            song=self.song,
        )

        self.song.favorites_count = 0
        self.song.save(
            update_fields=["favorites_count"],
        )

        results = list(
            DiscoveryService.most_favorited_songs()
        )

        self.assertIn(
            self.song,
            results,
        )

    def test_most_favorited_albums_returns_favorited_albums(self):
        AlbumFavorite.objects.create(
            user=self.user,
            album=self.album,
        )

        results = list(
            DiscoveryService.most_favorited_albums()
        )

        self.assertIn(
            self.album,
            results,
        )

    # ========================================================
    # TOP RATED
    # ========================================================

    def test_top_rated_songs_requires_minimum_ratings(self):
        for index in range(
            DiscoveryService.MIN_RATINGS_FOR_TOP_RATED
        ):
            user = User.objects.create_user(
                email=f"rating-{index}@example.com",
                password="test-password",
            )

            SongRating.objects.create(
                user=user,
                song=self.song,
                rating=5,
            )

        results = list(
            DiscoveryService.top_rated_songs()
        )

        self.assertIn(
            self.song,
            results,
        )

    def test_top_rated_songs_excludes_songs_below_rating_threshold(
        self,
    ):
        SongRating.objects.create(
            user=self.user,
            song=self.song,
            rating=5,
        )

        results = list(
            DiscoveryService.top_rated_songs()
        )

        self.assertNotIn(
            self.song,
            results,
        )

    def test_top_rated_albums_requires_minimum_ratings(self):
        for index in range(
            DiscoveryService.MIN_RATINGS_FOR_TOP_RATED
        ):
            user = User.objects.create_user(
                email=f"album-rating-{index}@example.com",
                password="test-password",
            )

            AlbumRating.objects.create(
                user=user,
                album=self.album,
                rating=5,
            )

        results = list(
            DiscoveryService.top_rated_albums()
        )

        self.assertIn(
            self.album,
            results,
        )

    # ========================================================
    # FEATURED
    # ========================================================

    def test_featured_songs_returns_only_featured_published_songs(
        self,
    ):
        self.song.is_featured = True
        self.song.save(
            update_fields=["is_featured"],
        )

        results = list(
            DiscoveryService.featured_songs()
        )

        self.assertIn(
            self.song,
            results
        )

        self.second_song.is_featured = False
        self.second_song.save(
            update_fields=["is_featured"],
        )

    def test_featured_songs_excludes_unpublished_featured_songs(
        self,
    ):
        self.song.is_featured = True
        self.song.status = Song.Status.DRAFT
        self.song.save(
            update_fields=[
                "is_featured",
                "status",
            ],
        )

        results = list(
            DiscoveryService.featured_songs()
        )

        self.assertNotIn(
            self.song,
            results,
        )

    def test_featured_albums_returns_only_featured_published_albums(
        self,
    ):
        self.album.is_featured = True
        self.album.save(
            update_fields=["is_featured"],
        )

        results = list(
            DiscoveryService.featured_albums()
        )

        self.assertIn(
            self.album,
            results,
        )

    def test_featured_artists_returns_only_verified_active_artists(
        self,
    ):
        self.artist.is_verified = True
        self.artist.save(
            update_fields=["is_verified"],
        )

        results = list(
            DiscoveryService.featured_artists()
        )

        self.assertIn(
            self.artist,
            results,
        )

    def test_featured_artists_excludes_unverified_artists(self):
        self.artist.is_verified = False
        self.artist.save(
            update_fields=["is_verified"],
        )

        results = list(
            DiscoveryService.featured_artists()
        )

        self.assertNotIn(
            self.artist,
            results,
        )

    # ========================================================
    # RECENTLY RELEASED
    # ========================================================

    def test_recently_released_songs_returns_songs_with_release_dates(
        self,
    ):
        results = list(
            DiscoveryService.recently_released_songs()
        )

        self.assertIn(
            self.song,
            results,
        )

        self.assertIn(
            self.second_song,
            results,
        )

    def test_recently_released_songs_orders_newest_first(self):
        results = list(
            DiscoveryService.recently_released_songs()
        )

        self.assertEqual(
            results[0],
            self.song,
        )

    def test_recently_released_albums_returns_albums_with_release_dates(
        self,
    ):
        results = list(
            DiscoveryService.recently_released_albums()
        )

        self.assertIn(
            self.album,
            results,
        )

    def test_recently_released_songs_excludes_songs_without_release_date(
        self,
    ):
        song = Song.objects.create(
            title="No Release Date",
            slug="no-release-date",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        song.artists.add(
            self.artist,
        )

        results = list(
            DiscoveryService.recently_released_songs()
        )

        self.assertNotIn(
            song,
            results,
        )

    # ========================================================
    # LIMITS
    # ========================================================

    def test_discovery_result_limit_is_respected(self):
        for index in range(
            DiscoveryService.RESULT_LIMIT + 5
        ):
            song = Song.objects.create(
                title=f"Song {index}",
                slug=f"song-{index}",
                status=Song.Status.PUBLISHED,
                release_date=timezone.now().date(),
                published_at=timezone.now(),
            )

            song.artists.add(
                self.artist,
            )

            SongFavorite.objects.create(
                user=self.user,
                song=song,
            )

        results = list(
            DiscoveryService.most_favorited_songs()
        )

        self.assertLessEqual(
            len(results),
            DiscoveryService.RESULT_LIMIT,
        )