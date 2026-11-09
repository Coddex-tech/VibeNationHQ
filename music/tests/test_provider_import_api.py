
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from music.models import Album, MusicProviderIdentity


User = get_user_model()


class MusicProviderImportAPITests(APITestCase):
    """API tests for authenticated music-provider imports."""

    endpoint_name = "music_api:provider-import"

    def setUp(self):
        self.user = User.objects.create_user(
            email="musicimport@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse(self.endpoint_name)

    def album_payload(self, provider_id="api-album-001"):
        return {
            "provider": "itunes",
            "provider_id": provider_id,
            "entity_type": "album",
            "title": "The Journey",
            "artist_name": "Test Artist",
            "metadata": {
                "artist_id": "api-artist-001",
                "genre": "Afrobeats",
            },
        }

    def test_authenticated_user_can_import_album(self):
        response = self.client.post(
            self.url,
            self.album_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data["entity_type"], "album")
        self.assertTrue(response.data["created"])
        self.assertEqual(response.data["title"], "The Journey")
        self.assertEqual(response.data["object_type"], "album")
        self.assertTrue(response.data["object_id"])
        self.assertTrue(response.data["identity_id"])

        self.assertEqual(Album.objects.filter(title="The Journey").count(), 1)

        self.assertTrue(
            MusicProviderIdentity.objects.filter(
                provider="itunes",
                provider_id="api-album-001",
            ).exists()
        )

    def test_repeated_import_reuses_existing_album(self):
        payload = self.album_payload()

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
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(first_response.data["created"])
        self.assertFalse(second_response.data["created"])

        self.assertEqual(
            first_response.data["object_id"],
            second_response.data["object_id"],
        )
        self.assertEqual(
            Album.objects.filter(title="The Journey").count(),
            1,
        )
        self.assertEqual(
            MusicProviderIdentity.objects.filter(
                provider="itunes",
                provider_id="api-album-001",
            ).count(),
            1,
        )

    def test_unauthenticated_user_cannot_import_album(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.url,
            self.album_payload(),
            format="json",
        )

        self.assertIn(
            response.status_code,
            (
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ),
        )
        self.assertEqual(Album.objects.count(), 0)

    def test_missing_provider_id_returns_bad_request(self):
        payload = self.album_payload()
        payload.pop("provider_id")

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Album.objects.count(), 0)

    def test_missing_title_returns_bad_request(self):
        payload = self.album_payload()
        payload.pop("title")

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Album.objects.count(), 0)

    def test_invalid_provider_returns_bad_request(self):
        payload = self.album_payload()
        payload["provider"] = "invalid-provider"

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Album.objects.count(), 0)

    def test_invalid_entity_type_returns_bad_request(self):
        payload = self.album_payload()
        payload["entity_type"] = "invalid-entity"

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Album.objects.count(), 0)
