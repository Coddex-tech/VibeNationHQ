from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from music.models import (
    Album,
    Artist,
    CommunityPost,
    EditorialArticle,
    MusicFeedInteraction,
    Song,
)


User = get_user_model()


class MusicFeedInteractionAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="feed@example.com",
            username="feeduser",
            password="StrongPassword123!",
        )

        cls.other_user = User.objects.create_user(
            email="other@example.com",
            username="otheruser",
            password="StrongPassword123!",
        )

        published_at = (
            timezone.now()
            - timedelta(days=1)
        )

        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
        )

        cls.album = Album.objects.create(
            title="Test Album",
            slug="test-album",
            status=Album.Status.PUBLISHED,
            published_at=published_at,
        )

        cls.album.artists.add(cls.artist)

        cls.song = Song.objects.create(
            title="Test Song",
            slug="test-song",
            album=cls.album,
            status=Song.Status.PUBLISHED,
            published_at=published_at,
        )

        cls.song.artists.add(cls.artist)

        cls.community_post = (
            CommunityPost.objects.create(
                user=cls.other_user,
                content="Test community post.",
                status=CommunityPost.Status.PUBLISHED,
            )
        )

        cls.editorial_article = (
            EditorialArticle.objects.create(
                title="Test Editorial",
                slug="test-editorial",
                excerpt="Test editorial excerpt.",
                content="Test editorial content.",
                author=cls.user,
                status=(
                    EditorialArticle.Status.PUBLISHED
                ),
                published_at=published_at,
            )
        )

    def setUp(self):
        self.client = APIClient()

        self.url = reverse(
            "music_api:music-feed-interaction",
        )

    def authenticate(self):
        self.client.force_authenticate(
            user=self.user,
        )

    def test_unauthenticated_user_cannot_record_interaction(
        self,
    ):
        response = self.client.post(
            self.url,
            {
                "interaction_type": "view_song",
                "target_type": "song",
                "target_id": self.song.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            0,
        )

    def test_authenticated_user_can_view_song(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": "view_song",
                "target_type": "song",
                "target_id": self.song.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            response.data["interaction_type"],
            "view_song",
        )

        self.assertEqual(
            response.data["target_type"],
            "song",
        )

        self.assertEqual(
            response.data["target_id"],
            self.song.id,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            1,
        )

    def test_authenticated_user_can_play_song_preview(
        self,
    ):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": "play_preview",
                "target_type": "song",
                "target_id": self.song.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            response.data["interaction_type"],
            "play_preview",
        )

    def test_authenticated_user_can_favorite_song(
        self,
    ):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": "favorite_song",
                "target_type": "song",
                "target_id": self.song.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertTrue(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type="favorite_song",
                song=self.song,
            ).exists(),
        )

    def test_authenticated_user_can_rate_song(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": "rate_song",
                "target_type": "song",
                "target_id": self.song.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_authenticated_user_can_view_album(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": "view_album",
                "target_type": "album",
                "target_id": self.album.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_authenticated_user_can_favorite_album(
        self,
    ):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": "favorite_album",
                "target_type": "album",
                "target_id": self.album.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_authenticated_user_can_rate_album(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": "rate_album",
                "target_type": "album",
                "target_id": self.album.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_authenticated_user_can_view_artist(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": "view_artist",
                "target_type": "artist",
                "target_id": self.artist.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_authenticated_user_can_follow_artist(
        self,
    ):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": "follow_artist",
                "target_type": "artist",
                "target_id": self.artist.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_authenticated_user_can_view_community_post(
        self,
    ):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": (
                    "view_community_post"
                ),
                "target_type": "community_post",
                "target_id": self.community_post.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_authenticated_user_can_like_community_post(
        self,
    ):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": (
                    "like_community_post"
                ),
                "target_type": "community_post",
                "target_id": self.community_post.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_authenticated_user_can_comment_on_community_post(
        self,
    ):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": (
                    "comment_community_post"
                ),
                "target_type": "community_post",
                "target_id": self.community_post.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_authenticated_user_can_view_editorial(
        self,
    ):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": "view_editorial",
                "target_type": "editorial",
                "target_id": (
                    self.editorial_article.id
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_authenticated_user_can_like_editorial(
        self,
    ):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": "like_editorial",
                "target_type": "editorial",
                "target_id": (
                    self.editorial_article.id
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_invalid_target_type_returns_400(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": "view_song",
                "target_type": "album",
                "target_id": self.album.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "target_type",
            response.data,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            0,
        )

    def test_missing_target_id_returns_400(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": "view_song",
                "target_type": "song",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "target_id",
            response.data,
        )

    def test_invalid_target_id_returns_400(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": "view_song",
                "target_type": "song",
                "target_id": 0,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "target_id",
            response.data,
        )

    def test_missing_target_returns_404(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "interaction_type": "view_song",
                "target_type": "song",
                "target_id": 999999,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            0,
        )

    def test_idempotency_key_returns_same_interaction(
        self,
    ):
        self.authenticate()

        key = uuid4()

        payload = {
            "interaction_type": "view_song",
            "target_type": "song",
            "target_id": self.song.id,
            "idempotency_key": str(key),
        }

        first_response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        second_response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            201,
        )

        self.assertEqual(
            second_response.status_code,
            201,
        )

        self.assertEqual(
            first_response.data["id"],
            second_response.data["id"],
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                idempotency_key=key,
            ).count(),
            1,
        )

    def test_idempotency_key_is_scoped_to_existing_event(
        self,
    ):
        self.authenticate()

        key = uuid4()

        first_response = self.client.post(
            self.url,
            {
                "interaction_type": "view_song",
                "target_type": "song",
                "target_id": self.song.id,
                "idempotency_key": str(key),
            },
            format="json",
        )

        second_response = self.client.post(
            self.url,
            {
                "interaction_type": "view_album",
                "target_type": "album",
                "target_id": self.album.id,
                "idempotency_key": str(key),
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            201,
        )

        self.assertEqual(
            second_response.status_code,
            201,
        )

        self.assertEqual(
            first_response.data["id"],
            second_response.data["id"],
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            1,
        )

    def test_empty_payload_returns_400(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "interaction_type",
            response.data,
        )

        self.assertIn(
            "target_type",
            response.data,
        )

        self.assertIn(
            "target_id",
            response.data,
        )