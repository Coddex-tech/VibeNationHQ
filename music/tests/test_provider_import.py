
from unittest.mock import patch

from django.test import TestCase

from music.models import (
    Album,
    AlbumTrack,
    Artist,
    MusicProviderIdentity,
    Song,
)
from music.providers.base import (
    MusicEntityType,
    MusicProviderName,
    MusicProviderResponseError,
    MusicSearchResult,
)
from music.services.provider_import import (
    MusicProviderImportService,
)


class AlbumTracklistImportTests(TestCase):
    def setUp(self):
        self.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=False,
        )

        self.album = Album.objects.create(
            title="Test Album",
            slug="test-album",
        )
        self.album.artists.add(self.artist)

        self.album_result = MusicSearchResult(
            provider=MusicProviderName.ITUNES,
            provider_id="12345",
            entity_type=MusicEntityType.ALBUM,
            title="Test Album",
            artist_name="Test Artist",
            album_name="Test Album",
            artwork_url=None,
            release_date="2024-01-01",
            duration_seconds=None,
            preview_url=None,
            spotify_url=None,
            apple_music_url="https://music.apple.com/album/test/12345",
            youtube_url=None,
            audiomack_url=None,
            boomplay_url=None,
            country="NG",
            isrc=None,
            metadata={
                "collection_id": 12345,
                "track_count": 3,
                "artist_id": 67890,
            },
        )

        self.track_results = [
            self.make_track("101", "First Song", 1),
            self.make_track("102", "Second Song", 2),
            self.make_track("103", "Third Song", 3),
        ]

    def make_track(self, provider_id, title, track_number):
        return MusicSearchResult(
            provider=MusicProviderName.ITUNES,
            provider_id=provider_id,
            entity_type=MusicEntityType.SONG,
            title=title,
            artist_name="Test Artist",
            album_name="Test Album",
            artwork_url=None,
            release_date="2024-01-01",
            duration_seconds=180,
            preview_url=None,
            spotify_url=None,
            apple_music_url=None,
            youtube_url=None,
            audiomack_url=None,
            boomplay_url=None,
            country="NG",
            isrc=None,
            metadata={
                "artist_id": 67890,
                "collection_id": 12345,
                "track_number": track_number,
                "disc_number": 1,
            },
        )

    def make_existing_tracklist(self):
        from django.utils import timezone

        songs = []

        for index, title in enumerate(
            ["Existing One", "Existing Two"],
            start=1,
        ):
            song = Song.objects.create(
                title=title,
                slug=f"existing-song-{index}",
                status=Song.Status.PUBLISHED,
                published_at=timezone.now(),
            )
            song.artists.add(self.artist)
            songs.append(song)

            AlbumTrack.objects.create(
                album=self.album,
                song=song,
                track_number=index,
            )

        return songs

    def import_album_with_tracks(self, tracks):
        with (
            patch(
                "music.services.provider_import."
                "MusicProviderRegistry"
            ) as registry_class,
            patch.object(
                MusicProviderImportService,
                "_download_artwork",
                return_value=None,
            ),
        ):
            provider = registry_class.return_value.get.return_value
            provider.get_album_tracks.return_value = tracks

            result = MusicProviderImportService.import_result(
                self.album_result
            )

        return result, provider

    def test_new_album_import_creates_ordered_tracklist(self):
        Album.objects.filter(pk=self.album.pk).delete()

        result, provider = self.import_album_with_tracks(
            self.track_results
        )

        imported_album = result.object

        self.assertIsInstance(imported_album, Album)
        self.assertTrue(result.created)
        self.assertEqual(imported_album.title, "Test Album")

        entries = list(
            AlbumTrack.objects.filter(
                album=imported_album,
            ).order_by("track_number")
        )

        self.assertEqual(len(entries), 3)
        self.assertEqual(
            [entry.track_number for entry in entries],
            [1, 2, 3],
        )
        self.assertEqual(
            [entry.song.title for entry in entries],
            ["First Song", "Second Song", "Third Song"],
        )

        provider.get_album_tracks.assert_called_once_with(
            album_provider_id="12345",
            country="NG",
        )

    def test_existing_album_import_synchronizes_tracklist(self):
        old_songs = self.make_existing_tracklist()

        MusicProviderIdentity.objects.create(
            provider=MusicProviderName.ITUNES,
            entity_type=MusicEntityType.ALBUM,
            provider_id="12345",
            album=self.album,
            metadata={},
        )

        result, _ = self.import_album_with_tracks(
            self.track_results
        )

        self.assertFalse(result.created)
        self.assertEqual(result.object.pk, self.album.pk)

        entries = list(
            AlbumTrack.objects.filter(
                album=self.album,
            ).order_by("track_number")
        )

        self.assertEqual(len(entries), 3)
        self.assertEqual(
            [entry.song.title for entry in entries],
            ["First Song", "Second Song", "Third Song"],
        )

        self.assertFalse(
            AlbumTrack.objects.filter(
                album=self.album,
                song__in=old_songs,
            ).exists()
        )

    def test_failed_provider_request_preserves_existing_tracklist(self):
        old_songs = self.make_existing_tracklist()

        MusicProviderIdentity.objects.create(
            provider=MusicProviderName.ITUNES,
            entity_type=MusicEntityType.ALBUM,
            provider_id="12345",
            album=self.album,
            metadata={},
        )

        with (
            patch(
                "music.services.provider_import."
                "MusicProviderRegistry"
            ) as registry_class,
            patch.object(
                MusicProviderImportService,
                "_download_artwork",
                return_value=None,
            ),
        ):
            provider = registry_class.return_value.get.return_value
            provider.get_album_tracks.side_effect = (
                MusicProviderResponseError("Provider unavailable")
            )

            result = MusicProviderImportService.import_result(
                self.album_result
            )

        self.assertEqual(result.object.pk, self.album.pk)

        entries = list(
            AlbumTrack.objects.filter(
                album=self.album,
            ).order_by("track_number")
        )

        self.assertEqual(
            [entry.song_id for entry in entries],
            [song.pk for song in old_songs],
        )

    def test_empty_provider_tracklist_preserves_existing_tracklist(self):
        old_songs = self.make_existing_tracklist()

        MusicProviderIdentity.objects.create(
            provider=MusicProviderName.ITUNES,
            entity_type=MusicEntityType.ALBUM,
            provider_id="12345",
            album=self.album,
            metadata={},
        )

        result, _ = self.import_album_with_tracks([])

        self.assertEqual(result.object.pk, self.album.pk)

        entries = list(
            AlbumTrack.objects.filter(
                album=self.album,
            ).order_by("track_number")
        )

        self.assertEqual(
            [entry.song_id for entry in entries],
            [song.pk for song in old_songs],
        )

    def test_mismatched_expected_count_preserves_existing_tracklist(self):
        old_songs = self.make_existing_tracklist()

        MusicProviderIdentity.objects.create(
            provider=MusicProviderName.ITUNES,
            entity_type=MusicEntityType.ALBUM,
            provider_id="12345",
            album=self.album,
            metadata={},
        )

        incomplete_tracks = self.track_results[:2]

        result, _ = self.import_album_with_tracks(
            incomplete_tracks
        )

        self.assertEqual(result.object.pk, self.album.pk)

        entries = list(
            AlbumTrack.objects.filter(
                album=self.album,
            ).order_by("track_number")
        )

        self.assertEqual(
            [entry.song_id for entry in entries],
            [song.pk for song in old_songs],
        )

    def test_duplicate_canonical_songs_preserve_existing_tracklist(self):
        old_songs = self.make_existing_tracklist()

        MusicProviderIdentity.objects.create(
            provider=MusicProviderName.ITUNES,
            entity_type=MusicEntityType.ALBUM,
            provider_id="12345",
            album=self.album,
            metadata={},
        )

        first_track = self.make_track(
            "201",
            "Same Song",
            1,
        )
        second_track = self.make_track(
            "202",
            "Same Song",
            2,
        )

        # Both provider IDs resolve to the same canonical song.
        from django.utils import timezone

        existing_song = Song.objects.create(
            title="Same Song",
            slug="same-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        existing_song.artists.add(self.artist)

        for provider_id in ("201", "202"):
            MusicProviderIdentity.objects.create(
                provider=MusicProviderName.ITUNES,
                entity_type=MusicEntityType.SONG,
                provider_id=provider_id,
                song=existing_song,
                metadata={},
            )

        from dataclasses import replace

        duplicate_album_result = replace(
            self.album_result,
            metadata={
                **self.album_result.metadata,
                "track_count": 2,
            },
        )

        with (
            patch(
                "music.services.provider_import.MusicProviderRegistry"
            ) as registry_class,
            patch.object(
                MusicProviderImportService,
                "_download_artwork",
                return_value=None,
            ),
        ):
            provider = registry_class.return_value.get.return_value
            provider.get_album_tracks.return_value = [
                first_track,
                second_track,
            ]

            result = MusicProviderImportService.import_result(
                duplicate_album_result
            )

        self.assertEqual(result.object.pk, self.album.pk)

        entries = list(
            AlbumTrack.objects.filter(
                album=self.album,
            ).order_by("track_number")
        )

        self.assertEqual(
            [entry.song_id for entry in entries],
            [song.pk for song in old_songs],
        )
