from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework import status

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
            onboarding_completed=True,
        )

        cls.other_user = User.objects.create_user(
            email="other@example.com",
            username="otheruser",
            password="StrongPassword123!",
            onboarding_completed=True,
        )

        published_at = (
            timezone.now()
            - timedelta(days=1)
        )

        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
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
                status=EditorialArticle.Status.PUBLISHED,
                published_at=published_at,
            )
        )

    def setUp(self):
        self.client = APIClient()

        self.url = reverse(
            "music_api:music-feed-interaction",
        )

    def authenticate(self, user=None):
        self.client.force_authenticate(
            user=user or self.user,
        )

    def post_interaction(
        self,
        *,
        interaction_type,
        target_type,
        target_id,
        idempotency_key=None,
    ):
        payload = {
            "interaction_type": interaction_type,
            "target_type": target_type,
            "target_id": target_id,
        }

        if idempotency_key is not None:
            payload["idempotency_key"] = str(
                idempotency_key,
            )

        return self.client.post(
            self.url,
            payload,
            format="json",
        )

    # ========================================================
    # Authentication and permissions
    # ========================================================

    def test_unauthenticated_user_cannot_record_interaction(
        self,
    ):
        response = self.post_interaction(
            interaction_type="view_song",
            target_type="song",
            target_id=self.song.id,
        )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            0,
        )

    def test_incomplete_onboarding_user_cannot_record_interaction(
        self,
    ):
        incomplete_user = User.objects.create_user(
            email="incomplete@example.com",
            username="incompleteuser",
            password="StrongPassword123!",
            onboarding_completed=False,
        )

        self.authenticate(incomplete_user)

        response = self.post_interaction(
            interaction_type="view_song",
            target_type="song",
            target_id=self.song.id,
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            0,
        )

    def test_staff_user_cannot_record_interaction(self):
        staff_user = User.objects.create_superuser(
            email="staff@example.com",
            password="TestPassword123!",
        )

        self.client.force_authenticate(user=staff_user)

        response = self.client.post(
            self.url,
            {
                "interaction_type": "view_community_post",
                "target_type": "community_post",
                "target_id": self.community_post.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=staff_user,
            ).exists()
        )

    # ========================================================
    # Accepted passive interactions
    # ========================================================

    def test_authenticated_user_can_record_all_passive_interactions(
        self,
    ):
        self.authenticate()

        interactions = [
            {
                "interaction_type": "view_song",
                "target_type": "song",
                "target_id": self.song.id,
            },
            {
                "interaction_type": "play_preview",
                "target_type": "song",
                "target_id": self.song.id,
            },
            {
                "interaction_type": "view_album",
                "target_type": "album",
                "target_id": self.album.id,
            },
            {
                "interaction_type": "view_artist",
                "target_type": "artist",
                "target_id": self.artist.id,
            },
            {
                "interaction_type": "view_community_post",
                "target_type": "community_post",
                "target_id": self.community_post.id,
            },
            {
                "interaction_type": "view_editorial",
                "target_type": "editorial",
                "target_id": self.editorial_article.id,
            },
        ]

        for interaction in interactions:
            with self.subTest(
                interaction_type=interaction[
                    "interaction_type"
                ],
            ):
                response = self.client.post(
                    self.url,
                    interaction,
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    201,
                    response.data,
                )

                self.assertEqual(
                    response.data["interaction_type"],
                    interaction["interaction_type"],
                )

                self.assertEqual(
                    response.data["target_type"],
                    interaction["target_type"],
                )

                self.assertEqual(
                    response.data["target_id"],
                    interaction["target_id"],
                )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
            ).count(),
            6,
        )

    # ========================================================
    # Rejected engagement interactions
    # ========================================================

    def test_engagement_interactions_are_rejected(
        self,
    ):
        self.authenticate()

        rejected_interactions = [
            ("favorite_song", "song", self.song.id),
            ("rate_song", "song", self.song.id),
            ("favorite_album", "album", self.album.id),
            ("rate_album", "album", self.album.id),
            ("follow_artist", "artist", self.artist.id),
            (
                "like_community_post",
                "community_post",
                self.community_post.id,
            ),
            (
                "comment_community_post",
                "community_post",
                self.community_post.id,
            ),
            (
                "favorite_community_post",
                "community_post",
                self.community_post.id,
            ),
            (
                "like_editorial",
                "editorial",
                self.editorial_article.id,
            ),
            (
                "favorite_editorial",
                "editorial",
                self.editorial_article.id,
            ),
        ]

        for interaction_type, target_type, target_id in (
            rejected_interactions
        ):
            with self.subTest(
                interaction_type=interaction_type,
            ):
                response = self.post_interaction(
                    interaction_type=interaction_type,
                    target_type=target_type,
                    target_id=target_id,
                )

                self.assertEqual(
                    response.status_code,
                    400,
                )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            0,
        )

    # ========================================================
    # Target type and ID validation
    # ========================================================

    def test_invalid_target_type_returns_400(self):
        self.authenticate()

        response = self.post_interaction(
            interaction_type="view_song",
            target_type="album",
            target_id=self.album.id,
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

        response = self.post_interaction(
            interaction_type="view_song",
            target_type="song",
            target_id=0,
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

        response = self.post_interaction(
            interaction_type="view_song",
            target_type="song",
            target_id=999999,
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            0,
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

    # ========================================================
    # Target publication and visibility
    # ========================================================

    def test_draft_song_cannot_receive_view_interaction(
        self,
    ):
        self.authenticate()

        self.song.status = Song.Status.DRAFT
        self.song.save(update_fields=["status"])

        response = self.post_interaction(
            interaction_type="view_song",
            target_type="song",
            target_id=self.song.id,
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            0,
        )

    def test_archived_song_cannot_receive_view_interaction(
        self,
    ):
        self.authenticate()

        self.song.status = Song.Status.ARCHIVED
        self.song.save(update_fields=["status"])

        response = self.post_interaction(
            interaction_type="view_song",
            target_type="song",
            target_id=self.song.id,
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_draft_album_cannot_receive_view_interaction(
        self,
    ):
        self.authenticate()

        self.album.status = Album.Status.DRAFT
        self.album.save(update_fields=["status"])

        response = self.post_interaction(
            interaction_type="view_album",
            target_type="album",
            target_id=self.album.id,
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_archived_album_cannot_receive_view_interaction(
        self,
    ):
        self.authenticate()

        self.album.status = Album.Status.ARCHIVED
        self.album.save(update_fields=["status"])

        response = self.post_interaction(
            interaction_type="view_album",
            target_type="album",
            target_id=self.album.id,
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_inactive_artist_cannot_receive_view_interaction(
        self,
    ):
        self.authenticate()

        self.artist.is_active = False
        self.artist.save(update_fields=["is_active"])

        response = self.post_interaction(
            interaction_type="view_artist",
            target_type="artist",
            target_id=self.artist.id,
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_hidden_community_post_cannot_receive_view_interaction(
        self,
    ):
        self.authenticate()

        self.community_post.status = (
            CommunityPost.Status.HIDDEN
        )
        self.community_post.save(
            update_fields=["status"],
        )

        response = self.post_interaction(
            interaction_type="view_community_post",
            target_type="community_post",
            target_id=self.community_post.id,
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_removed_community_post_cannot_receive_view_interaction(
        self,
    ):
        self.authenticate()

        self.community_post.status = (
            CommunityPost.Status.REMOVED
        )
        self.community_post.save(
            update_fields=["status"],
        )

        response = self.post_interaction(
            interaction_type="view_community_post",
            target_type="community_post",
            target_id=self.community_post.id,
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_draft_editorial_cannot_receive_view_interaction(
        self,
    ):
        self.authenticate()

        self.editorial_article.status = (
            EditorialArticle.Status.DRAFT
        )
        self.editorial_article.save(
            update_fields=["status"],
        )

        response = self.post_interaction(
            interaction_type="view_editorial",
            target_type="editorial",
            target_id=self.editorial_article.id,
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_archived_editorial_cannot_receive_view_interaction(
        self,
    ):
        self.authenticate()

        self.editorial_article.status = (
            EditorialArticle.Status.ARCHIVED
        )
        self.editorial_article.save(
            update_fields=["status"],
        )

        response = self.post_interaction(
            interaction_type="view_editorial",
            target_type="editorial",
            target_id=self.editorial_article.id,
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    # ========================================================
    # Idempotency
    # ========================================================

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

    def test_idempotency_key_cannot_be_reused_for_another_event(
        self,
    ):
        self.authenticate()

        key = uuid4()

        first_response = self.post_interaction(
            interaction_type="view_song",
            target_type="song",
            target_id=self.song.id,
            idempotency_key=key,
        )

        second_response = self.post_interaction(
            interaction_type="view_album",
            target_type="album",
            target_id=self.album.id,
            idempotency_key=key,
        )

        self.assertEqual(
            first_response.status_code,
            201,
        )

        self.assertEqual(
            second_response.status_code,
            400,
        )

        self.assertIn(
            "idempotency_key",
            second_response.data,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                idempotency_key=key,
            ).count(),
            1,
        )

    def test_idempotency_key_cannot_be_reused_by_another_user(
        self,
    ):
        self.authenticate()

        key = uuid4()

        first_response = self.post_interaction(
            interaction_type="view_song",
            target_type="song",
            target_id=self.song.id,
            idempotency_key=key,
        )

        self.authenticate(self.other_user)

        second_response = self.post_interaction(
            interaction_type="view_song",
            target_type="song",
            target_id=self.song.id,
            idempotency_key=key,
        )

        self.assertEqual(
            first_response.status_code,
            201,
        )

        self.assertEqual(
            second_response.status_code,
            400,
        )

        self.assertIn(
            "idempotency_key",
            second_response.data,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                idempotency_key=key,
            ).count(),
            1,
        )

    def test_retry_after_target_is_unpublished_returns_404(
        self,
    ):
        self.authenticate()

        key = uuid4()

        first_response = self.post_interaction(
            interaction_type="view_song",
            target_type="song",
            target_id=self.song.id,
            idempotency_key=key,
        )

        self.song.status = Song.Status.ARCHIVED
        self.song.save(update_fields=["status"])

        second_response = self.post_interaction(
            interaction_type="view_song",
            target_type="song",
            target_id=self.song.id,
            idempotency_key=key,
        )

        self.assertEqual(
            first_response.status_code,
            201,
        )

        self.assertEqual(
            second_response.status_code,
            404,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                idempotency_key=key,
            ).count(),
            1,
        )
