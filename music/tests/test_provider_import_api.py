from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from music.models import (
    Album,
    Artist,
    MusicProviderIdentity,
    Song,
)
from music.services.provider_import import MusicImportError


class MusicProviderImportAPITests(APITestCase):
    """
    API-level tests for explicit music provider imports.

    These tests verify the HTTP boundary between the frontend
    and MusicProviderImportService.

    Provider searching never creates catalog records.
    Records are created only when an authenticated client
    explicitly imports a selected provider result.
    """

    endpoint = "/api/v1/music/import/"

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="musicimport@example.com",
            password="testpass123",
        )

    def authenticate(self):
        self.client.force_authenticate(
            user=self.user,
        )

    def make_song_payload(
        self,
        *,
        provider_id: str = "123456789",
    ) -> dict:
        return {
            "provider": "itunes",
            "provider_id": provider_id,
            "entity_type": "song",
            "title": "Last Last",
            "artist_name": "Burna Boy",
            "album_name": "Love, Damini",
            "artwork_url": (
                "https://example.com/artwork.jpg"
            ),
            "release_date": "2022-05-13",
            "duration_seconds": 175,
            "preview_url": (
                "https://example.com/preview.m4a"
            ),
            "apple_music_url": (
                "https://music.apple.com/ng/song/example"
            ),
            "country": "NG",
            "isrc": "USAT22200001",
            "metadata": {
                "itunes_artist_id": 1001,
                "itunes_collection_id": 1002,
                "itunes_track_id": 1003,
            },
        }

    def make_artist_payload(
        self,
        *,
        provider_id: str = "artist-123",
    ) -> dict:
        return {
            "provider": "itunes",
            "provider_id": provider_id,
            "entity_type": "artist",
            "title": "Burna Boy",
            "artwork_url": (
                "https://example.com/burna.jpg"
            ),
            "country": "NG",
            "metadata": {
                "itunes_artist_id": 1001,
            },
        }

    def make_album_payload(
        self,
        *,
        provider_id: str = "album-123",
    ) -> dict:
        return {
            "provider": "itunes",
            "provider_id": provider_id,
            "entity_type": "album",
            "title": "Love, Damini",
            "artist_name": "Burna Boy",
            "artwork_url": (
                "https://example.com/album.jpg"
            ),
            "release_date": "2022-07-08",
            "country": "NG",
            "metadata": {
                "itunes_artist_id": 1001,
                "itunes_collection_id": 1002,
            },
        }

    def test_unauthenticated_user_cannot_import(self):
        response = self.client.post(
            self.endpoint,
            self.make_song_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(
            Song.objects.count(),
            0,
        )

        self.assertEqual(
            Artist.objects.count(),
            0,
        )

        self.assertEqual(
            Album.objects.count(),
            0,
        )

    def test_authenticated_user_can_import_song(self):
        self.authenticate()

        response = self.client.post(
            self.endpoint,
            self.make_song_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["entity_type"],
            "song",
        )

        self.assertTrue(
            response.data["created"],
        )

        self.assertEqual(
            response.data["object_type"],
            "song",
        )

        self.assertEqual(
            response.data["title"],
            "Last Last",
        )

        self.assertIsNotNone(
            response.data["song"],
        )

        self.assertEqual(
            response.data["song"]["title"],
            "Last Last",
        )

        self.assertEqual(
            Song.objects.count(),
            1,
        )

        self.assertEqual(
            Artist.objects.count(),
            1,
        )

        self.assertEqual(
            Album.objects.count(),
            1,
        )

        self.assertEqual(
            MusicProviderIdentity.objects.count(),
            1,
        )

    def test_importing_same_provider_result_twice_is_idempotent(self):
        self.authenticate()

        payload = self.make_song_payload()

        first_response = self.client.post(
            self.endpoint,
            payload,
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        second_response = self.client.post(
            self.endpoint,
            payload,
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            second_response.data["created"],
        )

        self.assertEqual(
            first_response.data["object_id"],
            second_response.data["object_id"],
        )

        self.assertEqual(
            Song.objects.count(),
            1,
        )

        self.assertEqual(
            Artist.objects.count(),
            1,
        )

        self.assertEqual(
            Album.objects.count(),
            1,
        )

        self.assertEqual(
            MusicProviderIdentity.objects.count(),
            1,
        )

    def test_authenticated_user_can_import_artist(self):
        self.authenticate()

        response = self.client.post(
            self.endpoint,
            self.make_artist_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["entity_type"],
            "artist",
        )

        self.assertEqual(
            response.data["object_type"],
            "artist",
        )

        self.assertEqual(
            response.data["title"],
            "Burna Boy",
        )

        self.assertIsNotNone(
            response.data["artist"],
        )

        self.assertEqual(
            response.data["artist"]["name"],
            "Burna Boy",
        )

        self.assertEqual(
            Artist.objects.count(),
            1,
        )

        self.assertEqual(
            MusicProviderIdentity.objects.count(),
            1,
        )

    def test_authenticated_user_can_import_album(self):
        self.authenticate()

        response = self.client.post(
            self.endpoint,
            self.make_album_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["entity_type"],
            "album",
        )

        self.assertEqual(
            response.data["object_type"],
            "album",
        )

        self.assertEqual(
            response.data["title"],
            "Love, Damini",
        )

        self.assertIsNotNone(
            response.data["album"],
        )

        self.assertEqual(
            response.data["album"]["title"],
            "Love, Damini",
        )

        self.assertEqual(
            Album.objects.count(),
            1,
        )

        self.assertEqual(
            Artist.objects.count(),
            1,
        )

        self.assertEqual(
            MusicProviderIdentity.objects.count(),
            1,
        )

    def test_invalid_provider_is_rejected(self):
        self.authenticate()

        payload = self.make_song_payload()

        payload["provider"] = "invalid-provider"

        response = self.client.post(
            self.endpoint,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "provider",
            response.data,
        )

        self.assertEqual(
            Song.objects.count(),
            0,
        )

        self.assertEqual(
            MusicProviderIdentity.objects.count(),
            0,
        )

    def test_missing_provider_id_is_rejected(self):
        self.authenticate()

        payload = self.make_song_payload()

        del payload["provider_id"]

        response = self.client.post(
            self.endpoint,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "provider_id",
            response.data,
        )

        self.assertEqual(
            Song.objects.count(),
            0,
        )

        self.assertEqual(
            MusicProviderIdentity.objects.count(),
            0,
        )

    def test_invalid_metadata_is_rejected(self):
        self.authenticate()

        payload = self.make_song_payload()

        payload["metadata"] = [
            "this",
            "must",
            "be",
            "an",
            "object",
        ]

        response = self.client.post(
            self.endpoint,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "metadata",
            response.data,
        )

        self.assertEqual(
            Song.objects.count(),
            0,
        )

        self.assertEqual(
            MusicProviderIdentity.objects.count(),
            0,
        )

    @patch(
        "music.api.views.provider_import."
        "MusicProviderImportService.import_result"
    )
    def test_import_service_error_returns_400(
        self,
        mock_import_result,
    ):
        self.authenticate()

        mock_import_result.side_effect = (
            MusicImportError(
                "The provider result could not be imported."
            )
        )

        response = self.client.post(
            self.endpoint,
            self.make_song_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            response.data["detail"],
            "The provider result could not be imported.",
        )

        mock_import_result.assert_called_once()

        self.assertEqual(
            Song.objects.count(),
            0,
        )

        self.assertEqual(
            Artist.objects.count(),
            0,
        )

        self.assertEqual(
            Album.objects.count(),
            0,
        )

        self.assertEqual(
            MusicProviderIdentity.objects.count(),
            0,
        )