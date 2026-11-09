
from django.test import TestCase

from music.models import Album, Artist, MusicProviderIdentity
from music.providers.base import (
    MusicEntityType,
    MusicProviderName,
    MusicSearchResult,
)
from music.services.provider_import import (
    MusicImportError,
    MusicProviderImportService,
)


class ProviderImportRegressionTests(TestCase):
    """Regression tests for canonical provider imports."""

    def setUp(self):
        self.service = MusicProviderImportService()

    def make_album_result(
        self,
        *,
        provider_id,
        title,
        artist_name,
        artist_provider_id,
    ):
        return MusicSearchResult(
            provider=MusicProviderName.ITUNES,
            provider_id=provider_id,
            entity_type=MusicEntityType.ALBUM,
            title=title,
            artist_name=artist_name,
            metadata={
                "artist_id": artist_provider_id,
                "genre": "Afrobeats",
            },
        )

    def test_same_album_title_by_different_artists_stays_separate(self):
        """An album must not be reused merely because its title matches."""

        first_result = self.make_album_result(
            provider_id="album-artist-a",
            title="The Journey",
            artist_name="Artist A",
            artist_provider_id="artist-a",
        )
        second_result = self.make_album_result(
            provider_id="album-artist-b",
            title="The Journey",
            artist_name="Artist B",
            artist_provider_id="artist-b",
        )

        first_import = self.service.import_result(first_result)
        second_import = self.service.import_result(second_result)

        self.assertNotEqual(
            first_import.object.pk,
            second_import.object.pk,
        )
        self.assertEqual(
            Album.objects.filter(title="The Journey").count(),
            2,
        )
        self.assertEqual(
            Artist.objects.filter(name__in=["Artist A", "Artist B"]).count(),
            2,
        )

    def test_reimporting_same_provider_album_is_idempotent(self):
        """Repeated imports must reuse the canonical album."""

        result = self.make_album_result(
            provider_id="album-repeat-001",
            title="One Album",
            artist_name="One Artist",
            artist_provider_id="artist-repeat-001",
        )

        first_import = self.service.import_result(result)
        second_import = self.service.import_result(result)

        self.assertEqual(
            first_import.object.pk,
            second_import.object.pk,
        )
        self.assertEqual(
            Album.objects.filter(title="One Album").count(),
            1,
        )
        self.assertEqual(
            MusicProviderIdentity.objects.filter(
                provider=MusicProviderName.ITUNES,
                entity_type=MusicEntityType.ALBUM,
                provider_id="album-repeat-001",
            ).count(),
            1,
        )
