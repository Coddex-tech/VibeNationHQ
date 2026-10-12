from __future__ import annotations

from datetime import date

from django.test import TestCase

from music.models import Album, Artist, Genre, Song
from music.services.catalog_search import (
    MusicCatalogSearchService,
)


class MusicCatalogSearchServiceTests(TestCase):
    def setUp(self):
        self.service = MusicCatalogSearchService()

        self.burna_boy = Artist.objects.create(
            name="Burna Boy",
            slug="burna-boy",
            country="Nigeria",
        )

        self.wizkid = Artist.objects.create(
            name="Wizkid",
            slug="wizkid",
            country="Nigeria",
        )

        self.tems = Artist.objects.create(
            name="Tems",
            slug="tems",
            country="Nigeria",
        )

        self.love_damini = Album.objects.create(
            title="Love, Damini",
            slug="love-damini",
            release_date=date(2022, 7, 8),
        )
        self.love_damini.artists.add(
            self.burna_boy,
        )

        self.made_in_lagos = Album.objects.create(
            title="Made in Lagos",
            slug="made-in-lagos",
            release_date=date(2020, 10, 30),
        )
        self.made_in_lagos.artists.add(
            self.wizkid,
        )

        self.for_broken_ears = Album.objects.create(
            title="For Broken Ears",
            slug="for-broken-ears",
            release_date=date(2020, 9, 25),
        )
        self.for_broken_ears.artists.add(
            self.tems,
        )

        self.last_last = Song.objects.create(
            title="Last Last",
            slug="last-last",
            album=self.love_damini,
            release_date=date(2022, 5, 13),
            duration_seconds=175,
        )
        self.last_last.artists.add(
            self.burna_boy,
        )

        self.essence = Song.objects.create(
            title="Essence",
            slug="essence",
            album=self.made_in_lagos,
            release_date=date(2020, 10, 30),
            duration_seconds=244,
        )
        self.essence.artists.add(
            self.wizkid,
        )
        self.essence.featured_artists.add(
            self.tems,
        )

        self.free_mind = Song.objects.create(
            title="Free Mind",
            slug="free-mind",
            album=self.for_broken_ears,
            release_date=date(2020, 9, 25),
            duration_seconds=240,
        )
        self.free_mind.artists.add(
            self.tems,
        )

    def test_search_songs_by_title(self):
        results = self.service.search(
            query="Last Last",
            entity_type="song",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].entity_type,
            "song",
        )
        self.assertEqual(
            results[0].object,
            self.last_last,
        )

    def test_search_songs_by_artist(self):
        results = self.service.search(
            query="Burna Boy",
            entity_type="song",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].object,
            self.last_last,
        )

    def test_search_songs_by_featured_artist(self):
        results = self.service.search(
            query="Tems",
            entity_type="song",
        )

        result_ids = {
            result.object.id
            for result in results
        }

        self.assertIn(
            self.essence.id,
            result_ids,
        )
        self.assertIn(
            self.free_mind.id,
            result_ids,
        )

    def test_search_songs_by_album(self):
        results = self.service.search(
            query="Love, Damini",
            entity_type="song",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].object,
            self.last_last,
        )

    def test_search_artists_by_name(self):
        results = self.service.search(
            query="Burna",
            entity_type="artist",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].object,
            self.burna_boy,
        )

    def test_search_artists_by_slug(self):
        results = self.service.search(
            query="wizkid",
            entity_type="artist",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].object,
            self.wizkid,
        )

    def test_search_albums_by_title(self):
        results = self.service.search(
            query="Made in Lagos",
            entity_type="album",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].object,
            self.made_in_lagos,
        )

    def test_search_albums_by_artist(self):
        results = self.service.search(
            query="Tems",
            entity_type="album",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].object,
            self.for_broken_ears,
        )

    def test_search_all_entity_types(self):
        results = self.service.search(
            query="Burna",
        )

        result_types = {
            result.entity_type
            for result in results
        }

        self.assertIn("song", result_types)
        self.assertIn("artist", result_types)
        self.assertIn("album", result_types)

    def test_empty_query_returns_no_results(self):
        initial_counts = {
            "artists": Artist.objects.count(),
            "albums": Album.objects.count(),
            "songs": Song.objects.count(),
        }

        results = self.service.search(
            query="   ",
            entity_type="song",
        )

        self.assertEqual(results, [])

        self.assertEqual(
            Artist.objects.count(),
            initial_counts["artists"],
        )
        self.assertEqual(
            Album.objects.count(),
            initial_counts["albums"],
        )
        self.assertEqual(
            Song.objects.count(),
            initial_counts["songs"],
        )

    def test_query_longer_than_maximum_is_rejected(self):
        query = "a" * (
            self.service.MAX_QUERY_LENGTH + 1
        )

        with self.assertRaisesMessage(
            ValueError,
            "Search query is too long.",
        ):
            self.service.search(
                query=query,
                entity_type="song",
            )

    def test_limit_is_applied(self):
        results = self.service.search(
            query="",
            entity_type="song",
            limit=1,
        )

        self.assertEqual(results, [])

        results = self.service.search(
            query="e",
            entity_type="song",
            limit=1,
        )

        self.assertEqual(len(results), 1)

    def test_limit_cannot_exceed_maximum(self):
        results = self.service.search(
            query="e",
            entity_type="song",
            limit=1000,
        )

        self.assertLessEqual(
            len(results),
            self.service.MAX_LIMIT,
        )

    def test_limit_is_at_least_one(self):
        results = self.service.search(
            query="e",
            entity_type="song",
            limit=0,
        )

        self.assertLessEqual(
            len(results),
            self.service.DEFAULT_LIMIT,
        )

    def test_unsupported_entity_type_is_rejected(self):
        with self.assertRaisesMessage(
            ValueError,
            "Unsupported catalog entity type",
        ):
            self.service.search(
                query="Burna",
                entity_type="playlist",
            )

    def test_search_does_not_create_records(self):
        artist_count = Artist.objects.count()
        album_count = Album.objects.count()
        song_count = Song.objects.count()
        genre_count = Genre.objects.count()

        self.service.search(
            query="Burna Boy",
        )

        self.assertEqual(
            Artist.objects.count(),
            artist_count,
        )
        self.assertEqual(
            Album.objects.count(),
            album_count,
        )
        self.assertEqual(
            Song.objects.count(),
            song_count,
        )
        self.assertEqual(
            Genre.objects.count(),
            genre_count,
        )