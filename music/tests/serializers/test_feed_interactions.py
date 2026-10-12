from __future__ import annotations

from uuid import uuid4

from django.test import SimpleTestCase

from music.models import MusicFeedInteraction
from music.serializers.feed_interactions import (
    MusicFeedInteractionSerializer,
)


class MusicFeedInteractionSerializerTests(
    SimpleTestCase,
):
    def test_valid_song_interactions(self):
        interaction_types = [
            MusicFeedInteraction.InteractionType.VIEW_SONG,
            MusicFeedInteraction.InteractionType.PLAY_PREVIEW,
            MusicFeedInteraction.InteractionType.FAVORITE_SONG,
            MusicFeedInteraction.InteractionType.RATE_SONG,
        ]

        for interaction_type in interaction_types:
            serializer = (
                MusicFeedInteractionSerializer(
                    data={
                        "interaction_type": interaction_type,
                        "target_type": "song",
                        "target_id": 1,
                    }
                )
            )

            self.assertTrue(
                serializer.is_valid(),
                serializer.errors,
            )

    def test_valid_album_interactions(self):
        interaction_types = [
            MusicFeedInteraction.InteractionType.VIEW_ALBUM,
            MusicFeedInteraction.InteractionType.FAVORITE_ALBUM,
            MusicFeedInteraction.InteractionType.RATE_ALBUM,
        ]

        for interaction_type in interaction_types:
            serializer = (
                MusicFeedInteractionSerializer(
                    data={
                        "interaction_type": interaction_type,
                        "target_type": "album",
                        "target_id": 1,
                    }
                )
            )

            self.assertTrue(
                serializer.is_valid(),
                serializer.errors,
            )

    def test_valid_artist_interactions(self):
        interaction_types = [
            MusicFeedInteraction.InteractionType.VIEW_ARTIST,
            MusicFeedInteraction.InteractionType.FOLLOW_ARTIST,
        ]

        for interaction_type in interaction_types:
            serializer = (
                MusicFeedInteractionSerializer(
                    data={
                        "interaction_type": interaction_type,
                        "target_type": "artist",
                        "target_id": 1,
                    }
                )
            )

            self.assertTrue(
                serializer.is_valid(),
                serializer.errors,
            )

    def test_valid_community_post_interactions(self):
        interaction_types = [
            MusicFeedInteraction.InteractionType.VIEW_COMMUNITY_POST,
            MusicFeedInteraction.InteractionType.LIKE_COMMUNITY_POST,
            MusicFeedInteraction.InteractionType.COMMENT_COMMUNITY_POST,
        ]

        for interaction_type in interaction_types:
            serializer = (
                MusicFeedInteractionSerializer(
                    data={
                        "interaction_type": interaction_type,
                        "target_type": "community_post",
                        "target_id": 1,
                    }
                )
            )

            self.assertTrue(
                serializer.is_valid(),
                serializer.errors,
            )

    def test_valid_editorial_interactions(self):
        interaction_types = [
            MusicFeedInteraction.InteractionType.VIEW_EDITORIAL,
            MusicFeedInteraction.InteractionType.LIKE_EDITORIAL,
        ]

        for interaction_type in interaction_types:
            serializer = (
                MusicFeedInteractionSerializer(
                    data={
                        "interaction_type": interaction_type,
                        "target_type": "editorial",
                        "target_id": 1,
                    }
                )
            )

            self.assertTrue(
                serializer.is_valid(),
                serializer.errors,
            )

    def test_song_interaction_cannot_target_album(self):
        serializer = (
            MusicFeedInteractionSerializer(
                data={
                    "interaction_type": "view_song",
                    "target_type": "album",
                    "target_id": 1,
                }
            )
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "target_type",
            serializer.errors,
        )

    def test_album_interaction_cannot_target_song(self):
        serializer = (
            MusicFeedInteractionSerializer(
                data={
                    "interaction_type": "view_album",
                    "target_type": "song",
                    "target_id": 1,
                }
            )
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "target_type",
            serializer.errors,
        )

    def test_artist_interaction_cannot_target_song(self):
        serializer = (
            MusicFeedInteractionSerializer(
                data={
                    "interaction_type": "follow_artist",
                    "target_type": "song",
                    "target_id": 1,
                }
            )
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "target_type",
            serializer.errors,
        )

    def test_community_interaction_cannot_target_editorial(self):
        serializer = (
            MusicFeedInteractionSerializer(
                data={
                    "interaction_type": "view_community_post",
                    "target_type": "editorial",
                    "target_id": 1,
                }
            )
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "target_type",
            serializer.errors,
        )

    def test_editorial_interaction_cannot_target_community_post(
        self,
    ):
        serializer = (
            MusicFeedInteractionSerializer(
                data={
                    "interaction_type": "view_editorial",
                    "target_type": "community_post",
                    "target_id": 1,
                }
            )
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "target_type",
            serializer.errors,
        )

    def test_target_id_must_be_positive(self):
        serializer = (
            MusicFeedInteractionSerializer(
                data={
                    "interaction_type": "view_song",
                    "target_type": "song",
                    "target_id": 0,
                }
            )
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "target_id",
            serializer.errors,
        )

    def test_target_id_cannot_be_negative(self):
        serializer = (
            MusicFeedInteractionSerializer(
                data={
                    "interaction_type": "view_song",
                    "target_type": "song",
                    "target_id": -5,
                }
            )
        )

        self.assertFalse(
            serializer.is_valid(),
        )

        self.assertIn(
            "target_id",
            serializer.errors,
        )

    def test_idempotency_key_is_optional(self):
        serializer = (
            MusicFeedInteractionSerializer(
                data={
                    "interaction_type": "view_song",
                    "target_type": "song",
                    "target_id": 1,
                }
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertIsNone(
            serializer.get_idempotency_key(),
        )

    def test_idempotency_key_accepts_uuid(self):
        key = uuid4()

        serializer = (
            MusicFeedInteractionSerializer(
                data={
                    "interaction_type": "view_song",
                    "target_type": "song",
                    "target_id": 1,
                    "idempotency_key": str(key),
                }
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertEqual(
            serializer.get_idempotency_key(),
            key,
        )

    def test_get_target_model_for_song(self):
        serializer = (
            MusicFeedInteractionSerializer(
                data={
                    "interaction_type": "view_song",
                    "target_type": "song",
                    "target_id": 42,
                }
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertEqual(
            serializer.get_target_model().__name__,
            "Song",
        )

    def test_get_target_model_for_album(self):
        serializer = (
            MusicFeedInteractionSerializer(
                data={
                    "interaction_type": "view_album",
                    "target_type": "album",
                    "target_id": 42,
                }
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertEqual(
            serializer.get_target_model().__name__,
            "Album",
        )

    def test_get_target_model_for_artist(self):
        serializer = (
            MusicFeedInteractionSerializer(
                data={
                    "interaction_type": "view_artist",
                    "target_type": "artist",
                    "target_id": 42,
                }
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertEqual(
            serializer.get_target_model().__name__,
            "Artist",
        )

    def test_get_target_model_for_community_post(self):
        serializer = (
            MusicFeedInteractionSerializer(
                data={
                    "interaction_type": "view_community_post",
                    "target_type": "community_post",
                    "target_id": 42,
                }
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertEqual(
            serializer.get_target_model().__name__,
            "CommunityPost",
        )

    def test_get_target_model_for_editorial(self):
        serializer = (
            MusicFeedInteractionSerializer(
                data={
                    "interaction_type": "view_editorial",
                    "target_type": "editorial",
                    "target_id": 42,
                }
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertEqual(
            serializer.get_target_model().__name__,
            "EditorialArticle",
        )

    def test_helper_methods_require_validation(self):
        serializer = MusicFeedInteractionSerializer(
            data={
                "interaction_type": "view_song",
                "target_type": "song",
                "target_id": 1,
            }
        )

        with self.assertRaises(RuntimeError):
            serializer.get_target_model()

        with self.assertRaises(RuntimeError):
            serializer.get_target_id()

        with self.assertRaises(RuntimeError):
            serializer.get_idempotency_key()

    def test_get_target_id_returns_validated_id(self):
        serializer = (
            MusicFeedInteractionSerializer(
                data={
                    "interaction_type": "view_song",
                    "target_type": "song",
                    "target_id": 123,
                }
            )
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertEqual(
            serializer.get_target_id(),
            123,
        )