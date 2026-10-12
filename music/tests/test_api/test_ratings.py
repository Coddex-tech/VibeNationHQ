from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from music.models import (
    Album,
    AlbumRating,
    MusicFeedInteraction,
    Song,
    SongRating,
)


User = get_user_model()


class SongRatingAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="song_rater",
            email="song_rater@example.com",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="another_song_rater",
            email="another_song_rater@example.com",
            password="testpass123",
        )

        self.song = Song.objects.create(
            title="Test Song",
            slug="test-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.url = reverse(
            "music_api:song-rating",
            kwargs={"pk": self.song.id},
        )

    def test_anonymous_user_cannot_rate_song(self):
        response = self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertFalse(
            SongRating.objects.filter(
                song=self.song,
            ).exists()
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                interaction_type=MusicFeedInteraction.InteractionType.RATE_SONG,
                song=self.song,
            ).exists()
        )

    def test_authenticated_user_can_rate_song(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["rating"],
            "4.50",
        )

        self.assertTrue(
            SongRating.objects.filter(
                user=self.user,
                song=self.song,
            ).exists()
        )

    def test_rating_creates_song_feed_interaction(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=MusicFeedInteraction.InteractionType.RATE_SONG,
                song=self.song,
            ).count(),
            1,
        )

    def test_rating_increments_ratings_count(self):
        self.client.force_authenticate(user=self.user)

        self.assertEqual(self.song.ratings_count, 0)

        response = self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.song.refresh_from_db()

        self.assertEqual(
            self.song.ratings_count,
            1,
        )

    def test_duplicate_rating_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        first_response = self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        second_response = self.client.post(
            self.url,
            {"rating": "3.5"},
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            SongRating.objects.filter(
                user=self.user,
                song=self.song,
            ).count(),
            1,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=MusicFeedInteraction.InteractionType.RATE_SONG,
                song=self.song,
            ).count(),
            1,
        )

        self.song.refresh_from_db()

        self.assertEqual(
            self.song.ratings_count,
            1,
        )

    def test_user_can_update_existing_rating(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(
            self.url,
            {"rating": "3.5"},
        )

        response = self.client.patch(
            self.url,
            {"rating": "5.0"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["rating"],
            "5.00",
        )

        rating = SongRating.objects.get(
            user=self.user,
            song=self.song,
        )

        self.assertEqual(
            rating.rating,
            Decimal("5.0"),
        )

    def test_updating_rating_creates_new_song_feed_interaction(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(
            self.url,
            {"rating": "3.5"},
        )

        response = self.client.patch(
            self.url,
            {"rating": "5.0"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=MusicFeedInteraction.InteractionType.RATE_SONG,
                song=self.song,
            ).count(),
            2,
        )

    def test_updating_rating_does_not_change_ratings_count(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(
            self.url,
            {"rating": "3.5"},
        )

        self.song.refresh_from_db()

        self.assertEqual(
            self.song.ratings_count,
            1,
        )

        response = self.client.patch(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.song.refresh_from_db()

        self.assertEqual(
            self.song.ratings_count,
            1,
        )

    def test_update_without_existing_rating_returns_404(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=MusicFeedInteraction.InteractionType.RATE_SONG,
                song=self.song,
            ).exists()
        )

    def test_user_can_delete_existing_rating(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            SongRating.objects.filter(
                user=self.user,
                song=self.song,
            ).exists()
        )

    def test_deleting_rating_does_not_create_interaction(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.client.delete(self.url)

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=MusicFeedInteraction.InteractionType.RATE_SONG,
                song=self.song,
            ).count(),
            1,
        )

    def test_deleting_rating_decrements_ratings_count(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.song.refresh_from_db()

        self.assertEqual(
            self.song.ratings_count,
            1,
        )

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.song.refresh_from_db()

        self.assertEqual(
            self.song.ratings_count,
            0,
        )

    def test_deleting_without_existing_rating_is_idempotent(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.song.refresh_from_db()

        self.assertEqual(
            self.song.ratings_count,
            0,
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=MusicFeedInteraction.InteractionType.RATE_SONG,
                song=self.song,
            ).exists()
        )

    def test_different_users_can_rate_same_song(self):
        self.client.force_authenticate(user=self.user)

        first_response = self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.force_authenticate(user=self.other_user)

        second_response = self.client.post(
            self.url,
            {"rating": "3.5"},
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.song.refresh_from_db()

        self.assertEqual(
            self.song.ratings_count,
            2,
        )

        self.assertEqual(
            SongRating.objects.filter(
                song=self.song,
            ).count(),
            2,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                interaction_type=MusicFeedInteraction.InteractionType.RATE_SONG,
                song=self.song,
            ).count(),
            2,
        )

    def test_unpublished_song_cannot_be_rated(self):
        self.song.status = Song.Status.DRAFT
        self.song.save(update_fields=["status"])

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=MusicFeedInteraction.InteractionType.RATE_SONG,
                song=self.song,
            ).exists()
        )

    def test_invalid_rating_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {"rating": "4.7"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            SongRating.objects.filter(
                song=self.song,
            ).exists()
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=MusicFeedInteraction.InteractionType.RATE_SONG,
                song=self.song,
            ).exists()
        )


class AlbumRatingAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="album_rater",
            email="album_rater@example.com",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="another_album_rater",
            email="another_album_rater@example.com",
            password="testpass123",
        )

        self.album = Album.objects.create(
            title="Test Album",
            slug="test-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.url = reverse(
            "music_api:album-rating",
            kwargs={"pk": self.album.id},
        )

    def test_anonymous_user_cannot_rate_album(self):
        response = self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertFalse(
            AlbumRating.objects.filter(
                album=self.album
            ).exists()
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                interaction_type=MusicFeedInteraction.InteractionType.RATE_ALBUM,
                album=self.album,
            ).exists()
        )

    def test_authenticated_user_can_rate_album(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["rating"],
            "4.50",
        )

        self.assertTrue(
            AlbumRating.objects.filter(
                user=self.user,
                album=self.album,
            ).exists()
        )

    def test_rating_creates_album_feed_interaction(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=MusicFeedInteraction.InteractionType.RATE_ALBUM,
                album=self.album,
            ).count(),
            1,
        )

    def test_rating_increments_ratings_count(self):
        self.client.force_authenticate(user=self.user)

        self.assertEqual(
            self.album.ratings_count,
            0,
        )

        response = self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.album.refresh_from_db()

        self.assertEqual(
            self.album.ratings_count,
            1,
        )

    def test_duplicate_rating_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        first_response = self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        second_response = self.client.post(
            self.url,
            {"rating": "3.5"},
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            AlbumRating.objects.filter(
                user=self.user,
                album=self.album,
            ).count(),
            1,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=MusicFeedInteraction.InteractionType.RATE_ALBUM,
                album=self.album,
            ).count(),
            1,
        )

        self.album.refresh_from_db()

        self.assertEqual(
            self.album.ratings_count,
            1,
        )

    def test_user_can_update_existing_rating(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(
            self.url,
            {"rating": "3.5"},
        )

        response = self.client.patch(
            self.url,
            {"rating": "5.0"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["rating"],
            "5.00",
        )

        rating = AlbumRating.objects.get(
            user=self.user,
            album=self.album,
        )

        self.assertEqual(
            rating.rating,
            Decimal("5.0"),
        )

    def test_updating_rating_creates_new_album_feed_interaction(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(
            self.url,
            {"rating": "3.5"},
        )

        response = self.client.patch(
            self.url,
            {"rating": "5.0"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=MusicFeedInteraction.InteractionType.RATE_ALBUM,
                album=self.album,
            ).count(),
            2,
        )

    def test_updating_rating_does_not_change_ratings_count(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(
            self.url,
            {"rating": "3.5"},
        )

        self.album.refresh_from_db()

        self.assertEqual(
            self.album.ratings_count,
            1,
        )

        response = self.client.patch(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.album.refresh_from_db()

        self.assertEqual(
            self.album.ratings_count,
            1,
        )

    def test_update_without_existing_rating_returns_404(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=MusicFeedInteraction.InteractionType.RATE_ALBUM,
                album=self.album,
            ).exists()
        )

    def test_user_can_delete_existing_rating(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            AlbumRating.objects.filter(
                user=self.user,
                album=self.album,
            ).exists()
        )

    def test_deleting_rating_does_not_create_interaction(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.client.delete(self.url)

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=MusicFeedInteraction.InteractionType.RATE_ALBUM,
                album=self.album,
            ).count(),
            1,
        )

    def test_deleting_rating_decrements_ratings_count(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.album.refresh_from_db()

        self.assertEqual(
            self.album.ratings_count,
            1,
        )

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.album.refresh_from_db()

        self.assertEqual(
            self.album.ratings_count,
            0,
        )

    def test_deleting_without_existing_rating_is_idempotent(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.album.refresh_from_db()

        self.assertEqual(
            self.album.ratings_count,
            0,
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=MusicFeedInteraction.InteractionType.RATE_ALBUM,
                album=self.album,
            ).exists()
        )

    def test_different_users_can_rate_same_album(self):
        self.client.force_authenticate(user=self.user)

        first_response = self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.force_authenticate(
            user=self.other_user
        )

        second_response = self.client.post(
            self.url,
            {"rating": "3.5"},
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.album.refresh_from_db()

        self.assertEqual(
            self.album.ratings_count,
            2,
        )

        self.assertEqual(
            AlbumRating.objects.filter(
                album=self.album
            ).count(),
            2,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                interaction_type=MusicFeedInteraction.InteractionType.RATE_ALBUM,
                album=self.album,
            ).count(),
            2,
        )

    def test_unpublished_album_cannot_be_rated(self):
        self.album.status = Album.Status.DRAFT
        self.album.save(
            update_fields=["status"]
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {"rating": "4.5"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=MusicFeedInteraction.InteractionType.RATE_ALBUM,
                album=self.album,
            ).exists()
        )

    def test_invalid_rating_is_rejected(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {"rating": "4.7"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            AlbumRating.objects.filter(
                album=self.album
            ).exists()
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=MusicFeedInteraction.InteractionType.RATE_ALBUM,
                album=self.album,
            ).exists()
        )