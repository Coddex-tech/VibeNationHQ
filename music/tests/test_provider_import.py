from __future__ import annotations

from django.test import TestCase

from music.models import (
    Album,
    Artist,
    Genre,
    MusicProviderIdentity,
    Song,
)
from music.providers.base import (
    MusicEntityType,
    MusicProviderName,
    MusicSearchResult,
)
from music.services.provider_import import (
    MusicImportError,
    MusicProviderImportService,
)


class MusicProviderImportServiceTests(TestCase):
    def setUp(self):
        self.afrobeats = Genre.objects.create(
            name="Afrobeats",
            slug="afrobeats",
        )

        self.hip_hop = Genre.objects.create(
            name="Hip-Hop",
            slug="hip-hop",
        )

        self.rnb = Genre.objects.create(
            name="R&B",
            slug="rnb",
        )

    def make_song_result(
        self,
        *,
        provider_id: str = "1612345678",
        title: str = "Last Last",
        artist_name: str = "Burna Boy",
        album_name: str = "Love, Damini",
        genre: str = "Afrobeats",
        metadata_overrides: dict | None = None,
    ) -> MusicSearchResult:
        metadata = {
            "artist_provider_id": "278873",
            "album_provider_id": "1612345000",
            "genre": genre,
        }

        if metadata_overrides:
            metadata.update(
                metadata_overrides,
            )

        return MusicSearchResult(
            provider=MusicProviderName.ITUNES,
            provider_id=provider_id,
            entity_type=MusicEntityType.SONG,
            title=title,
            artist_name=artist_name,
            album_name=album_name,
            artwork_url=(
                "https://example.com/last-last.jpg"
            ),
            release_date="2022-05-13T00:00:00Z",
            duration_seconds=168000,
            preview_url=(
                "https://example.com/last-last-preview.m4a"
            ),
            spotify_url=(
                "https://open.spotify.com/track/example"
            ),
            apple_music_url=(
                "https://music.apple.com/ng/song/example"
            ),
            metadata=metadata,
        )

    def make_artist_result(
        self,
        *,
        provider_id: str = "278873",
        name: str = "Burna Boy",
    ) -> MusicSearchResult:
        return MusicSearchResult(
            provider=MusicProviderName.ITUNES,
            provider_id=provider_id,
            entity_type=MusicEntityType.ARTIST,
            title=name,
            artwork_url=(
                "https://example.com/burna-boy.jpg"
            ),
            apple_music_url=(
                "https://music.apple.com/ng/artist/example"
            ),
            metadata={
                "artist_provider_id": provider_id,
            },
        )

    def make_album_result(
        self,
        *,
        provider_id: str = "1612345000",
        title: str = "Love, Damini",
        artist_name: str = "Burna Boy",
    ) -> MusicSearchResult:
        return MusicSearchResult(
            provider=MusicProviderName.ITUNES,
            provider_id=provider_id,
            entity_type=MusicEntityType.ALBUM,
            title=title,
            artist_name=artist_name,
            artwork_url=(
                "https://example.com/love-damini.jpg"
            ),
            release_date="2022-07-08T00:00:00Z",
            apple_music_url=(
                "https://music.apple.com/ng/album/example"
            ),
            metadata={
                "artist_provider_id": "278873",
            },
        )

    def test_imports_new_song_with_artist_and_album(self):
        result = (
            MusicProviderImportService.import_result(
                self.make_song_result()
            )
        )

        self.assertEqual(
            result.entity_type,
            MusicEntityType.SONG,
        )
        self.assertTrue(result.created)

        song = result.object

        self.assertIsInstance(song, Song)
        self.assertEqual(
            song.title,
            "Last Last",
        )
        self.assertEqual(
            song.duration_seconds,
            168000,
        )

        self.assertEqual(
            song.artists.count(),
            1,
        )

        artist = song.artists.get()

        self.assertEqual(
            artist.name,
            "Burna Boy",
        )

        self.assertIsNotNone(
            song.album,
        )

        self.assertEqual(
            song.album.title,
            "Love, Damini",
        )

        self.assertEqual(
            song.genres.count(),
            1,
        )

        self.assertEqual(
            song.genres.get(),
            self.afrobeats,
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
            Song.objects.count(),
            1,
        )

        self.assertEqual(
            MusicProviderIdentity.objects.count(),
            3,
        )

    def test_song_identity_stores_provider_specific_metadata(self):
        result = (
            MusicProviderImportService.import_result(
                self.make_song_result()
            )
        )

        identity = result.identity

        self.assertEqual(
            identity.provider,
            MusicProviderName.ITUNES,
        )

        self.assertEqual(
            identity.entity_type,
            MusicEntityType.SONG,
        )

        self.assertEqual(
            identity.provider_id,
            "1612345678",
        )

        self.assertEqual(
            identity.preview_url,
            "https://example.com/last-last-preview.m4a",
        )

        self.assertEqual(
            identity.artwork_url,
            "https://example.com/last-last.jpg",
        )

        self.assertEqual(
            identity.apple_music_url,
            "https://music.apple.com/ng/song/example",
        )

        self.assertEqual(
            identity.metadata["genre"],
            "Afrobeats",
        )

    def test_provider_genre_is_resolved_to_canonical_genre(self):
        result = (
            MusicProviderImportService.import_result(
                self.make_song_result(
                    genre="Afrobeats",
                )
            )
        )

        song = result.object

        self.assertEqual(
            list(song.genres.all()),
            [self.afrobeats],
        )

        self.assertEqual(
            Genre.objects.count(),
            3,
        )

    def test_provider_genre_alias_is_resolved_to_canonical_genre(
        self,
    ):
        result = (
            MusicProviderImportService.import_result(
                self.make_song_result(
                    genre="Afro-Pop",
                )
            )
        )

        song = result.object

        self.assertEqual(
            list(song.genres.all()),
            [self.afrobeats],
        )

        self.assertEqual(
            result.identity.metadata["genre"],
            "Afro-Pop",
        )

    def test_unknown_provider_genre_is_not_created(self):
        result = (
            MusicProviderImportService.import_result(
                self.make_song_result(
                    genre="Completely Unknown Genre",
                )
            )
        )

        song = result.object

        self.assertEqual(
            song.genres.count(),
            0,
        )

        self.assertEqual(
            Genre.objects.count(),
            3,
        )

        self.assertEqual(
            result.identity.metadata["genre"],
            "Completely Unknown Genre",
        )

    def test_multiple_provider_genres_are_attached(self):
        result = (
            MusicProviderImportService.import_result(
                self.make_song_result(
                    genre="Afrobeats",
                    metadata_overrides={
                        "genres": [
                            "Hip-Hop",
                            "R&B",
                        ],
                    },
                )
            )
        )

        song = result.object

        self.assertEqual(
            set(
                song.genres.values_list(
                    "pk",
                    flat=True,
                )
            ),
            {
                self.afrobeats.pk,
                self.hip_hop.pk,
                self.rnb.pk,
            },
        )

        self.assertEqual(
            song.genres.count(),
            3,
        )

    def test_duplicate_provider_genres_do_not_duplicate_song_relationships(
        self,
    ):
        result = (
            MusicProviderImportService.import_result(
                self.make_song_result(
                    genre="Afrobeats",
                    metadata_overrides={
                        "genres": [
                            "Afro-Pop",
                            "AFROBEATS",
                            "afrobeats",
                        ],
                    },
                )
            )
        )

        song = result.object

        self.assertEqual(
            song.genres.count(),
            1,
        )

        self.assertEqual(
            song.genres.get(),
            self.afrobeats,
        )

    def test_existing_song_can_gain_genre_from_new_provider_identity(
        self,
    ):
        first_result = (
            MusicProviderImportService.import_result(
                self.make_song_result(
                    provider_id="1612345678",
                    genre="Afrobeats",
                )
            )
        )

        second_result = (
            MusicProviderImportService.import_result(
                self.make_song_result(
                    provider_id="9876543210",
                    genre="Hip-Hop",
                )
            )
        )

        song = first_result.object

        self.assertEqual(
            song.pk,
            second_result.object.pk,
        )

        self.assertEqual(
            set(
                song.genres.values_list(
                    "pk",
                    flat=True,
                )
            ),
            {
                self.afrobeats.pk,
                self.hip_hop.pk,
            },
        )

        self.assertEqual(
            song.genres.count(),
            2,
        )

        self.assertEqual(
            MusicProviderIdentity.objects.filter(
                entity_type=MusicEntityType.SONG,
            ).count(),
            2,
        )

    def test_importing_same_provider_result_twice_does_not_duplicate(
        self,
    ):
        first = (
            MusicProviderImportService.import_result(
                self.make_song_result()
            )
        )

        second = (
            MusicProviderImportService.import_result(
                self.make_song_result()
            )
        )

        self.assertTrue(first.created)
        self.assertFalse(second.created)

        self.assertEqual(
            first.object.pk,
            second.object.pk,
        )

        self.assertEqual(
            first.identity.pk,
            second.identity.pk,
        )

        self.assertEqual(
            first.object.genres.count(),
            1,
        )

        self.assertEqual(
            first.object.genres.get(),
            self.afrobeats,
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
            Song.objects.count(),
            1,
        )

        self.assertEqual(
            MusicProviderIdentity.objects.count(),
            3,
        )

    def test_reuses_existing_canonical_song_for_new_provider_identity(
        self,
    ):
        first_result = (
            MusicProviderImportService.import_result(
                self.make_song_result(
                    provider_id="1612345678",
                    genre="Afrobeats",
                )
            )
        )

        second_result = (
            MusicProviderImportService.import_result(
                self.make_song_result(
                    provider_id="9876543210",
                    genre="Hip-Hop",
                )
            )
        )

        self.assertTrue(first_result.created)
        self.assertFalse(second_result.created)

        self.assertEqual(
            first_result.object.pk,
            second_result.object.pk,
        )

        self.assertNotEqual(
            first_result.identity.pk,
            second_result.identity.pk,
        )

        self.assertEqual(
            set(
                first_result.object.genres.values_list(
                    "pk",
                    flat=True,
                )
            ),
            {
                self.afrobeats.pk,
                self.hip_hop.pk,
            },
        )

        self.assertEqual(
            Song.objects.count(),
            1,
        )

        self.assertEqual(
            MusicProviderIdentity.objects.filter(
                entity_type=MusicEntityType.SONG,
            ).count(),
            2,
        )

    def test_imports_standalone_artist(self):
        result = (
            MusicProviderImportService.import_result(
                self.make_artist_result()
            )
        )

        self.assertTrue(result.created)

        self.assertIsInstance(
            result.object,
            Artist,
        )

        self.assertEqual(
            result.object.name,
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

        identity = result.identity

        self.assertEqual(
            identity.artist_id,
            result.object.pk,
        )

        self.assertIsNone(
            identity.song_id,
        )

        self.assertIsNone(
            identity.album_id,
        )

    def test_imports_standalone_album(self):
        result = (
            MusicProviderImportService.import_result(
                self.make_album_result()
            )
        )

        self.assertTrue(result.created)

        self.assertIsInstance(
            result.object,
            Album,
        )

        self.assertEqual(
            result.object.title,
            "Love, Damini",
        )

        self.assertEqual(
            result.object.artists.count(),
            1,
        )

        self.assertEqual(
            result.object.artists.first().name,
            "Burna Boy",
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
            2,
        )

    def test_reuses_existing_artist_by_normalized_name(self):
        artist = Artist.objects.create(
            name="Burna Boy",
            slug="burna-boy",
        )

        result = (
            MusicProviderImportService.import_result(
                self.make_artist_result(
                    name="  burna boy  ",
                )
            )
        )

        self.assertFalse(result.created)

        self.assertEqual(
            result.object.pk,
            artist.pk,
        )

        self.assertEqual(
            Artist.objects.count(),
            1,
        )

        self.assertEqual(
            MusicProviderIdentity.objects.count(),
            1,
        )

    def test_reuses_existing_album_for_same_artist(self):
        artist = Artist.objects.create(
            name="Burna Boy",
            slug="burna-boy",
        )

        album = Album.objects.create(
            title="Love, Damini",
            slug="love-damini",
        )

        album.artists.add(artist)

        result = (
            MusicProviderImportService.import_result(
                self.make_album_result()
            )
        )

        self.assertFalse(result.created)

        self.assertEqual(
            result.object.pk,
            album.pk,
        )

        self.assertEqual(
            Album.objects.count(),
            1,
        )

        self.assertEqual(
            Artist.objects.count(),
            1,
        )

    def test_rejects_missing_provider_id(self):
        result = self.make_song_result(
            provider_id="",
        )

        with self.assertRaises(MusicImportError):
            MusicProviderImportService.import_result(
                result
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
            Song.objects.count(),
            0,
        )

        self.assertEqual(
            MusicProviderIdentity.objects.count(),
            0,
        )

    def test_rejects_missing_title(self):
        result = self.make_song_result(
            title="",
        )

        with self.assertRaises(MusicImportError):
            MusicProviderImportService.import_result(
                result
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
            Song.objects.count(),
            0,
        )

        self.assertEqual(
            MusicProviderIdentity.objects.count(),
            0,
        )

    def test_rejects_song_without_artist(self):
        result = self.make_song_result()

        result = MusicSearchResult(
            provider=result.provider,
            provider_id=result.provider_id,
            entity_type=result.entity_type,
            title=result.title,
            artist_name=None,
            album_name=result.album_name,
            artwork_url=result.artwork_url,
            release_date=result.release_date,
            duration_seconds=result.duration_seconds,
            preview_url=result.preview_url,
            spotify_url=result.spotify_url,
            apple_music_url=result.apple_music_url,
            youtube_url=result.youtube_url,
            audiomack_url=result.audiomack_url,
            boomplay_url=result.boomplay_url,
            metadata=result.metadata,
        )

        with self.assertRaises(MusicImportError):
            MusicProviderImportService.import_result(
                result
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
            Song.objects.count(),
            0,
        )

        self.assertEqual(
            MusicProviderIdentity.objects.count(),
            0,
        )