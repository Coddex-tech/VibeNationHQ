from __future__ import annotations

from datetime import date

from django.test import TestCase

from music.models import Album, Artist, Song
from music.serializers.catalog_search import (
    MusicCatalogSearchResultSerializer,
)
from music.services.catalog_search import (
    CatalogSearchResult,
)


class MusicCatalogSearchResultSerializerTests(
    TestCase,
):
    def setUp(self):
        self.burna_boy = Artist.objects.create(
            name="Burna Boy",
            slug="burna-boy",
            country="Nigeria",
        )

        self.tems = Artist.objects.create(
            name="Tems",
            slug="tems",
            country="Nigeria",
        )

        self.album = Album.objects.create(
            title="Love, Damini",
            slug="love-damini",
            release_date=date(2022, 7, 8),
        )

        self.album.artists.add(
            self.burna_boy,
        )

        self.song = Song.objects.create(
            title="Last Last",
            slug="last-last",
            album=self.album,
            release_date=date(2022, 5, 13),
            duration_seconds=175,
        )

        self.song.artists.add(
            self.burna_boy,
        )

        self.song.featured_artists.add(
            self.tems,
        )

    def serialize(self, result):
        serializer = (
            MusicCatalogSearchResultSerializer(
                result,
            )
        )

        return serializer.data

    def test_song_result_is_serialized(self):
        result = CatalogSearchResult(
            entity_type="song",
            object=self.song,
        )

        data = self.serialize(result)

        self.assertEqual(
            data["entity_type"],
            "song",
        )
        self.assertEqual(
            data["id"],
            self.song.id,
        )
        self.assertEqual(
            data["title"],
            "Last Last",
        )
        self.assertEqual(
            data["slug"],
            "last-last",
        )

    def test_song_result_includes_primary_artist(self):
        result = CatalogSearchResult(
            entity_type="song",
            object=self.song,
        )

        data = self.serialize(result)

        self.assertEqual(
            data["artist"]["id"],
            self.burna_boy.id,
        )
        self.assertEqual(
            data["artist"]["name"],
            "Burna Boy",
        )
        self.assertEqual(
            data["artist"]["slug"],
            "burna-boy",
        )

    def test_song_result_includes_all_artists(self):
        result = CatalogSearchResult(
            entity_type="song",
            object=self.song,
        )

        data = self.serialize(result)

        artist_ids = {
            artist["id"]
            for artist in data["artists"]
        }

        self.assertEqual(
            artist_ids,
            {self.burna_boy.id},
        )

    def test_song_result_includes_album(self):
        result = CatalogSearchResult(
            entity_type="song",
            object=self.song,
        )

        data = self.serialize(result)

        self.assertEqual(
            data["album"]["id"],
            self.album.id,
        )
        self.assertEqual(
            data["album"]["title"],
            "Love, Damini",
        )
        self.assertEqual(
            data["album"]["slug"],
            "love-damini",
        )

    def test_song_without_album_returns_null_album(self):
        song = Song.objects.create(
            title="Standalone Song",
            slug="standalone-song",
        )
        song.artists.add(
            self.burna_boy,
        )

        result = CatalogSearchResult(
            entity_type="song",
            object=song,
        )

        data = self.serialize(result)

        self.assertIsNone(
            data["album"],
        )

    def test_artist_result_is_serialized(self):
        result = CatalogSearchResult(
            entity_type="artist",
            object=self.burna_boy,
        )

        data = self.serialize(result)

        self.assertEqual(
            data["entity_type"],
            "artist",
        )
        self.assertEqual(
            data["id"],
            self.burna_boy.id,
        )
        self.assertEqual(
            data["title"],
            "Burna Boy",
        )
        self.assertEqual(
            data["slug"],
            "burna-boy",
        )

    def test_artist_result_includes_itself_in_artists(self):
        result = CatalogSearchResult(
            entity_type="artist",
            object=self.burna_boy,
        )

        data = self.serialize(result)

        self.assertEqual(
            data["artists"],
            [
                {
                    "id": self.burna_boy.id,
                    "name": "Burna Boy",
                    "slug": "burna-boy",
                }
            ],
        )

    def test_artist_result_has_no_primary_artist(self):
        result = CatalogSearchResult(
            entity_type="artist",
            object=self.burna_boy,
        )

        data = self.serialize(result)

        self.assertIsNone(
            data["artist"],
        )

    def test_album_result_is_serialized(self):
        result = CatalogSearchResult(
            entity_type="album",
            object=self.album,
        )

        data = self.serialize(result)

        self.assertEqual(
            data["entity_type"],
            "album",
        )
        self.assertEqual(
            data["id"],
            self.album.id,
        )
        self.assertEqual(
            data["title"],
            "Love, Damini",
        )
        self.assertEqual(
            data["slug"],
            "love-damini",
        )

    def test_album_result_includes_artists(self):
        result = CatalogSearchResult(
            entity_type="album",
            object=self.album,
        )

        data = self.serialize(result)

        self.assertEqual(
            data["artists"],
            [
                {
                    "id": self.burna_boy.id,
                    "name": "Burna Boy",
                    "slug": "burna-boy",
                }
            ],
        )

    def test_album_result_uses_first_artist_as_primary_artist(
        self,
    ):
        result = CatalogSearchResult(
            entity_type="album",
            object=self.album,
        )

        data = self.serialize(result)

        self.assertEqual(
            data["artist"]["id"],
            self.burna_boy.id,
        )

    def test_artist_and_album_without_artwork_return_null(
        self,
    ):
        artist_result = CatalogSearchResult(
            entity_type="artist",
            object=self.burna_boy,
        )

        album_result = CatalogSearchResult(
            entity_type="album",
            object=self.album,
        )

        artist_data = self.serialize(
            artist_result,
        )
        album_data = self.serialize(
            album_result,
        )

        self.assertIsNone(
            artist_data["artwork"],
        )
        self.assertIsNone(
            album_data["artwork"],
        )

    def test_song_without_artwork_returns_null(self):
        result = CatalogSearchResult(
            entity_type="song",
            object=self.song,
        )

        data = self.serialize(result)

        self.assertIsNone(
            data["artwork"],
        )