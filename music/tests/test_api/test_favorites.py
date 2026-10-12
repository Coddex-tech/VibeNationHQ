from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from music.models import (
    Album,
    AlbumFavorite,
    MusicFeedInteraction,
    Song,
    SongFavorite,
)


User = get_user_model()


class SongFavoriteAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="song_favoriter",
            email="song_favoriter@example.com",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="another_song_favoriter",
            email="another_song_favoriter@example.com",
            password="testpass123",
        )

        self.song = Song.objects.create(
            title="Test Song",
            slug="test-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.url = reverse(
            "music_api:song-favorite",
            kwargs={"pk": self.song.id},
        )

    def test_anonymous_user_cannot_favorite_song(self):
        response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertFalse(
            SongFavorite.objects.filter(
                song=self.song,
            ).exists()
        )

    def test_authenticated_user_can_favorite_song(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["favorited"],
            True,
        )

        self.assertEqual(
            response.data["favorites_count"],
            1,
        )

        self.assertTrue(
            SongFavorite.objects.filter(
                user=self.user,
                song=self.song,
            ).exists()
        )

    def test_favorite_creates_song_feed_interaction(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        interaction = (
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType
                    .FAVORITE_SONG
                ),
                song=self.song,
            )
            .first()
        )

        self.assertIsNotNone(
            interaction,
        )

        self.assertIsNone(
            interaction.album,
        )

        self.assertIsNone(
            interaction.artist,
        )

        self.assertIsNone(
            interaction.community_post,
        )

        self.assertIsNone(
            interaction.editorial_article,
        )

    def test_favorite_response_contains_favorite_data(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertIn(
            "favorite",
            response.data,
        )

        self.assertEqual(
            response.data["favorite"]["song"]["id"],
            self.song.id,
        )

        self.assertEqual(
            response.data["favorite"]["user"],
            self.user.id,
        )

    def test_favorite_increments_favorites_count(self):
        self.client.force_authenticate(
            user=self.user
        )

        self.assertEqual(
            self.song.favorites_count,
            0,
        )

        response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.song.refresh_from_db()

        self.assertEqual(
            self.song.favorites_count,
            1,
        )

    def test_duplicate_favorite_is_rejected(self):
        self.client.force_authenticate(
            user=self.user
        )

        first_response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        second_response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            SongFavorite.objects.filter(
                user=self.user,
                song=self.song,
            ).count(),
            1,
        )

        self.song.refresh_from_db()

        self.assertEqual(
            self.song.favorites_count,
            1,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType
                    .FAVORITE_SONG
                ),
                song=self.song,
            ).count(),
            1,
        )

    def test_unpublished_song_cannot_be_favorited(self):
        self.song.status = Song.Status.DRAFT

        self.song.save(
            update_fields=["status"]
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            SongFavorite.objects.filter(
                song=self.song,
            ).exists()
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType
                    .FAVORITE_SONG
                ),
                song=self.song,
            ).exists()
        )

    def test_user_can_unfavorite_song(self):
        self.client.force_authenticate(
            user=self.user
        )

        self.client.post(
            self.url,
            {},
        )

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["favorited"],
            False,
        )

        self.assertFalse(
            SongFavorite.objects.filter(
                user=self.user,
                song=self.song,
            ).exists()
        )

    def test_unfavoriting_song_decrements_favorites_count(self):
        self.client.force_authenticate(
            user=self.user
        )

        self.client.post(
            self.url,
            {},
        )

        self.song.refresh_from_db()

        self.assertEqual(
            self.song.favorites_count,
            1,
        )

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.song.refresh_from_db()

        self.assertEqual(
            self.song.favorites_count,
            0,
        )

    def test_unfavoriting_without_existing_favorite_is_idempotent(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["favorited"],
            False,
        )

        self.assertEqual(
            response.data["favorites_count"],
            0,
        )

        self.song.refresh_from_db()

        self.assertEqual(
            self.song.favorites_count,
            0,
        )

    def test_user_can_favorite_song_again_after_unfavoriting(self):
        self.client.force_authenticate(
            user=self.user
        )

        first_response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.delete(
            self.url,
        )

        second_response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            second_response.data["favorited"],
            True,
        )

        self.song.refresh_from_db()

        self.assertEqual(
            self.song.favorites_count,
            1,
        )

        self.assertEqual(
            SongFavorite.objects.filter(
                user=self.user,
                song=self.song,
            ).count(),
            1,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType
                    .FAVORITE_SONG
                ),
                song=self.song,
            ).count(),
            2,
        )

    def test_anonymous_user_cannot_unfavorite_song(self):
        self.client.force_authenticate(
            user=self.user
        )

        self.client.post(
            self.url,
            {},
        )

        self.client.force_authenticate(
            user=None
        )

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertTrue(
            SongFavorite.objects.filter(
                user=self.user,
                song=self.song,
            ).exists()
        )

    def test_different_users_can_favorite_same_song(self):
        self.client.force_authenticate(
            user=self.user
        )

        first_response = self.client.post(
            self.url,
            {},
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
            {},
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.song.refresh_from_db()

        self.assertEqual(
            self.song.favorites_count,
            2,
        )

        self.assertEqual(
            SongFavorite.objects.filter(
                song=self.song,
            ).count(),
            2,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                interaction_type=(
                    MusicFeedInteraction.InteractionType
                    .FAVORITE_SONG
                ),
                song=self.song,
            ).count(),
            2,
        )

    def test_unfavoriting_song_only_removes_current_users_favorite(self):
        self.client.force_authenticate(
            user=self.user
        )

        self.client.post(
            self.url,
            {},
        )

        self.client.force_authenticate(
            user=self.other_user
        )

        self.client.post(
            self.url,
            {},
        )

        self.client.delete(
            self.url,
        )

        self.assertTrue(
            SongFavorite.objects.filter(
                user=self.user,
                song=self.song,
            ).exists()
        )

        self.assertFalse(
            SongFavorite.objects.filter(
                user=self.other_user,
                song=self.song,
            ).exists()
        )

        self.song.refresh_from_db()

        self.assertEqual(
            self.song.favorites_count,
            1,
        )


class AlbumFavoriteAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="album_favoriter",
            email="album_favoriter@example.com",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="another_album_favoriter",
            email="another_album_favoriter@example.com",
            password="testpass123",
        )

        self.album = Album.objects.create(
            title="Test Album",
            slug="test-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.url = reverse(
            "music_api:album-favorite",
            kwargs={"pk": self.album.id},
        )

    def test_anonymous_user_cannot_favorite_album(self):
        response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertFalse(
            AlbumFavorite.objects.filter(
                album=self.album,
            ).exists()
        )

    def test_authenticated_user_can_favorite_album(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["favorited"],
            True,
        )

        self.assertEqual(
            response.data["favorites_count"],
            1,
        )

        self.assertTrue(
            AlbumFavorite.objects.filter(
                user=self.user,
                album=self.album,
            ).exists()
        )

    def test_favorite_creates_album_feed_interaction(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        interaction = (
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType
                    .FAVORITE_ALBUM
                ),
                album=self.album,
            )
            .first()
        )

        self.assertIsNotNone(
            interaction,
        )

        self.assertIsNone(
            interaction.song,
        )

        self.assertIsNone(
            interaction.artist,
        )

        self.assertIsNone(
            interaction.community_post,
        )

        self.assertIsNone(
            interaction.editorial_article,
        )

    def test_favorite_response_contains_favorite_data(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertIn(
            "favorite",
            response.data,
        )

        self.assertEqual(
            response.data["favorite"]["album"]["id"],
            self.album.id,
        )

        self.assertEqual(
            response.data["favorite"]["user"],
            self.user.id,
        )

    def test_favorite_increments_favorites_count(self):
        self.client.force_authenticate(
            user=self.user
        )

        self.assertEqual(
            self.album.favorites_count,
            0,
        )

        response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.album.refresh_from_db()

        self.assertEqual(
            self.album.favorites_count,
            1,
        )

    def test_duplicate_favorite_is_rejected(self):
        self.client.force_authenticate(
            user=self.user
        )

        first_response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        second_response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            AlbumFavorite.objects.filter(
                user=self.user,
                album=self.album,
            ).count(),
            1,
        )

        self.album.refresh_from_db()

        self.assertEqual(
            self.album.favorites_count,
            1,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType
                    .FAVORITE_ALBUM
                ),
                album=self.album,
            ).count(),
            1,
        )

    def test_unpublished_album_cannot_be_favorited(self):
        self.album.status = Album.Status.DRAFT

        self.album.save(
            update_fields=["status"]
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            AlbumFavorite.objects.filter(
                album=self.album,
            ).exists()
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType
                    .FAVORITE_ALBUM
                ),
                album=self.album,
            ).exists()
        )

    def test_user_can_unfavorite_album(self):
        self.client.force_authenticate(
            user=self.user
        )

        self.client.post(
            self.url,
            {},
        )

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["favorited"],
            False,
        )

        self.assertFalse(
            AlbumFavorite.objects.filter(
                user=self.user,
                album=self.album,
            ).exists()
        )

    def test_unfavoriting_album_decrements_favorites_count(self):
        self.client.force_authenticate(
            user=self.user
        )

        self.client.post(
            self.url,
            {},
        )

        self.album.refresh_from_db()

        self.assertEqual(
            self.album.favorites_count,
            1,
        )

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.album.refresh_from_db()

        self.assertEqual(
            self.album.favorites_count,
            0,
        )

    def test_unfavoriting_without_existing_favorite_is_idempotent(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["favorited"],
            False,
        )

        self.assertEqual(
            response.data["favorites_count"],
            0,
        )

        self.album.refresh_from_db()

        self.assertEqual(
            self.album.favorites_count,
            0,
        )

    def test_user_can_favorite_album_again_after_unfavoriting(self):
        self.client.force_authenticate(
            user=self.user
        )

        first_response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.delete(
            self.url,
        )

        second_response = self.client.post(
            self.url,
            {},
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            second_response.data["favorited"],
            True,
        )

        self.album.refresh_from_db()

        self.assertEqual(
            self.album.favorites_count,
            1,
        )

        self.assertEqual(
            AlbumFavorite.objects.filter(
                user=self.user,
                album=self.album,
            ).count(),
            1,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType
                    .FAVORITE_ALBUM
                ),
                album=self.album,
            ).count(),
            2,
        )

    def test_anonymous_user_cannot_unfavorite_album(self):
        self.client.force_authenticate(
            user=self.user
        )

        self.client.post(
            self.url,
            {},
        )

        self.client.force_authenticate(
            user=None
        )

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertTrue(
            AlbumFavorite.objects.filter(
                user=self.user,
                album=self.album,
            ).exists()
        )

    def test_different_users_can_favorite_same_album(self):
        self.client.force_authenticate(
            user=self.user
        )

        first_response = self.client.post(
            self.url,
            {},
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
            {},
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.album.refresh_from_db()

        self.assertEqual(
            self.album.favorites_count,
            2,
        )

        self.assertEqual(
            AlbumFavorite.objects.filter(
                album=self.album,
            ).count(),
            2,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                interaction_type=(
                    MusicFeedInteraction.InteractionType
                    .FAVORITE_ALBUM
                ),
                album=self.album,
            ).count(),
            2,
        )

    def test_unfavoriting_album_only_removes_current_users_favorite(self):
        self.client.force_authenticate(
            user=self.user
        )

        self.client.post(
            self.url,
            {},
        )

        self.client.force_authenticate(
            user=self.other_user
        )

        self.client.post(
            self.url,
            {},
        )

        self.client.delete(
            self.url,
        )

        self.assertTrue(
            AlbumFavorite.objects.filter(
                user=self.user,
                album=self.album,
            ).exists()
        )

        self.assertFalse(
            AlbumFavorite.objects.filter(
                user=self.other_user,
                album=self.album,
            ).exists()
        )

        self.album.refresh_from_db()

        self.assertEqual(
            self.album.favorites_count,
            1,
        )