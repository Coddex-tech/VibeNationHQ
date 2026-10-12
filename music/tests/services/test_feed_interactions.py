from __future__ import annotations

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from music.models import (
    Album,
    Artist,
    CommunityPost,
    EditorialArticle,
    MusicFeedInteraction,
    Song,
)
from music.services.feed_interactions import (
    MusicFeedInteractionService,
)


User = get_user_model()


class MusicFeedInteractionServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        published_at = timezone.now() - timedelta(
            days=1,
        )

        cls.user = User.objects.create_user(
            username="interaction-user",
            email="interaction@example.com",
            password="test-password-123",
        )

        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
        )

        cls.artist_two = Artist.objects.create(
            name="Second Artist",
            slug="second-artist",
        )

        cls.album = Album.objects.create(
            title="Test Album",
            slug="test-album",
            status=Album.Status.PUBLISHED,
            published_at=published_at,
        )

        cls.song = Song.objects.create(
            title="Test Song",
            slug="test-song",
            album=cls.album,
            status=Song.Status.PUBLISHED,
            published_at=published_at,
        )

        cls.community_post = CommunityPost.objects.create(
            user=cls.user,
            content="This is a test community post.",
            status=CommunityPost.Status.PUBLISHED,
        )

        cls.editorial_article = EditorialArticle.objects.create(
            title="Test Editorial",
            slug="test-editorial",
            excerpt="Test editorial excerpt.",
            content="Test editorial content.",
            author=cls.user,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=published_at,
        )

    def setUp(self):
        MusicFeedInteraction.objects.all().delete()

    # ========================================================
    # Song interactions
    # ========================================================

    def test_record_song_view(self):
        interaction = (
            MusicFeedInteractionService.record_song_view(
                user=self.user,
                song=self.song,
            )
        )

        self.assertEqual(
            interaction.user,
            self.user,
        )

        self.assertEqual(
            interaction.interaction_type,
            MusicFeedInteraction.InteractionType.VIEW_SONG,
        )

        self.assertEqual(
            interaction.song,
            self.song,
        )

        self.assertIsNone(interaction.album)
        self.assertIsNone(interaction.artist)
        self.assertIsNone(interaction.community_post)
        self.assertIsNone(
            interaction.editorial_article,
        )

    def test_record_preview_play(self):
        interaction = (
            MusicFeedInteractionService.record_preview_play(
                user=self.user,
                song=self.song,
            )
        )

        self.assertEqual(
            interaction.interaction_type,
            MusicFeedInteraction.InteractionType.PLAY_PREVIEW,
        )

        self.assertEqual(
            interaction.song,
            self.song,
        )

    def test_record_song_favorite(self):
        interaction = (
            MusicFeedInteractionService.record_song_favorite(
                user=self.user,
                song=self.song,
            )
        )

        self.assertEqual(
            interaction.interaction_type,
            MusicFeedInteraction.InteractionType.FAVORITE_SONG,
        )

        self.assertEqual(
            interaction.song,
            self.song,
        )

    def test_record_song_rating(self):
        interaction = (
            MusicFeedInteractionService.record_song_rating(
                user=self.user,
                song=self.song,
            )
        )

        self.assertEqual(
            interaction.interaction_type,
            MusicFeedInteraction.InteractionType.RATE_SONG,
        )

        self.assertEqual(
            interaction.song,
            self.song,
        )

    # ========================================================
    # Album interactions
    # ========================================================

    def test_record_album_view(self):
        interaction = (
            MusicFeedInteractionService.record_album_view(
                user=self.user,
                album=self.album,
            )
        )

        self.assertEqual(
            interaction.interaction_type,
            MusicFeedInteraction.InteractionType.VIEW_ALBUM,
        )

        self.assertEqual(
            interaction.album,
            self.album,
        )

    def test_record_album_favorite(self):
        interaction = (
            MusicFeedInteractionService.record_album_favorite(
                user=self.user,
                album=self.album,
            )
        )

        self.assertEqual(
            interaction.interaction_type,
            MusicFeedInteraction.InteractionType.FAVORITE_ALBUM,
        )

        self.assertEqual(
            interaction.album,
            self.album,
        )

    def test_record_album_rating(self):
        interaction = (
            MusicFeedInteractionService.record_album_rating(
                user=self.user,
                album=self.album,
            )
        )

        self.assertEqual(
            interaction.interaction_type,
            MusicFeedInteraction.InteractionType.RATE_ALBUM,
        )

        self.assertEqual(
            interaction.album,
            self.album,
        )

    # ========================================================
    # Artist interactions
    # ========================================================

    def test_record_artist_view(self):
        interaction = (
            MusicFeedInteractionService.record_artist_view(
                user=self.user,
                artist=self.artist,
            )
        )

        self.assertEqual(
            interaction.interaction_type,
            MusicFeedInteraction.InteractionType.VIEW_ARTIST,
        )

        self.assertEqual(
            interaction.artist,
            self.artist,
        )

    def test_record_artist_follow(self):
        interaction = (
            MusicFeedInteractionService.record_artist_follow(
                user=self.user,
                artist=self.artist,
            )
        )

        self.assertEqual(
            interaction.interaction_type,
            MusicFeedInteraction.InteractionType.FOLLOW_ARTIST,
        )

        self.assertEqual(
            interaction.artist,
            self.artist,
        )

    # ========================================================
    # Community interactions
    # ========================================================

    def test_record_community_post_view(self):
        interaction = (
            MusicFeedInteractionService
            .record_community_post_view(
                user=self.user,
                post=self.community_post,
            )
        )

        self.assertEqual(
            interaction.interaction_type,
            (
                MusicFeedInteraction.InteractionType
                .VIEW_COMMUNITY_POST
            ),
        )

        self.assertEqual(
            interaction.community_post,
            self.community_post,
        )

    def test_record_community_post_like(self):
        interaction = (
            MusicFeedInteractionService
            .record_community_post_like(
                user=self.user,
                post=self.community_post,
            )
        )

        self.assertEqual(
            interaction.interaction_type,
            (
                MusicFeedInteraction.InteractionType
                .LIKE_COMMUNITY_POST
            ),
        )

        self.assertEqual(
            interaction.community_post,
            self.community_post,
        )

    def test_record_community_post_comment(self):
        interaction = (
            MusicFeedInteractionService
            .record_community_post_comment(
                user=self.user,
                post=self.community_post,
            )
        )

        self.assertEqual(
            interaction.interaction_type,
            (
                MusicFeedInteraction.InteractionType
                .COMMENT_COMMUNITY_POST
            ),
        )

        self.assertEqual(
            interaction.community_post,
            self.community_post,
        )

    # ========================================================
    # Editorial interactions
    # ========================================================

    def test_record_editorial_view(self):
        interaction = (
            MusicFeedInteractionService
            .record_editorial_view(
                user=self.user,
                article=self.editorial_article,
            )
        )

        self.assertEqual(
            interaction.interaction_type,
            MusicFeedInteraction.InteractionType.VIEW_EDITORIAL,
        )

        self.assertEqual(
            interaction.editorial_article,
            self.editorial_article,
        )

    def test_record_editorial_like(self):
        interaction = (
            MusicFeedInteractionService
            .record_editorial_like(
                user=self.user,
                article=self.editorial_article,
            )
        )

        self.assertEqual(
            interaction.interaction_type,
            MusicFeedInteraction.InteractionType.LIKE_EDITORIAL,
        )

        self.assertEqual(
            interaction.editorial_article,
            self.editorial_article,
        )

    # ========================================================
    # Repeated interactions
    # ========================================================

    def test_repeated_interactions_are_allowed(self):
        first = (
            MusicFeedInteractionService.record_song_view(
                user=self.user,
                song=self.song,
            )
        )

        second = (
            MusicFeedInteractionService.record_song_view(
                user=self.user,
                song=self.song,
            )
        )

        self.assertNotEqual(
            first.id,
            second.id,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            2,
        )

    # ========================================================
    # Idempotency
    # ========================================================

    def test_same_idempotency_key_returns_existing_interaction(
        self,
    ):
        idempotency_key = uuid.uuid4()

        first = (
            MusicFeedInteractionService.record_song_view(
                user=self.user,
                song=self.song,
                idempotency_key=idempotency_key,
            )
        )

        second = (
            MusicFeedInteractionService.record_song_view(
                user=self.user,
                song=self.song,
                idempotency_key=idempotency_key,
            )
        )

        self.assertEqual(
            first.id,
            second.id,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            1,
        )

    def test_different_idempotency_keys_create_different_interactions(
        self,
    ):
        first = (
            MusicFeedInteractionService.record_song_view(
                user=self.user,
                song=self.song,
                idempotency_key=uuid.uuid4(),
            )
        )

        second = (
            MusicFeedInteractionService.record_song_view(
                user=self.user,
                song=self.song,
                idempotency_key=uuid.uuid4(),
            )
        )

        self.assertNotEqual(
            first.id,
            second.id,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            2,
        )

    # ========================================================
    # Database constraint
    # ========================================================

    def test_invalid_target_combination_is_rejected(self):
        interaction = MusicFeedInteraction(
            user=self.user,
            interaction_type=(
                MusicFeedInteraction.InteractionType.VIEW_SONG
            ),
            song=self.song,
            album=self.album,
        )

        with self.assertRaises(Exception):
            interaction.full_clean()