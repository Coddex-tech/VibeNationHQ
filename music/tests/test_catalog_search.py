
from django.test import TestCase
from django.utils import timezone

from music.models import Album, Artist, Song
from music.services.catalog_search import MusicCatalogSearchService


class MusicCatalogSearchServiceTests(TestCase):
    def setUp(self):
        self.service = MusicCatalogSearchService()

        self.artist = Artist.objects.create(
            name="Davido",
            slug="davido",
            is_active=True,
        )

        self.inactive_artist = Artist.objects.create(
            name="Inactive Artist",
            slug="inactive-artist",
            is_active=False,
        )

        self.album = self.create_album(
            title="Timeless",
            slug="timeless",
            artist=self.artist,
            status=Album.Status.PUBLISHED,
        )

    # ========================================================
    # Test data helpers
    # ========================================================

    def create_song(
        self,
        *,
        title,
        slug,
        artist=None,
        album=None,
        status=Song.Status.DRAFT,
    ):
        published_at = (
            timezone.now()
            if status == Song.Status.PUBLISHED
            else None
        )

        song = Song.objects.create(
            title=title,
            slug=slug,
            album=album,
            status=status,
            published_at=published_at,
        )

        if artist is not None:
            song.artists.add(artist)

        return song

    def create_album(
        self,
        *,
        title,
        slug,
        artist=None,
        status=Album.Status.DRAFT,
    ):
        published_at = (
            timezone.now()
            if status == Album.Status.PUBLISHED
            else None
        )

        album = Album.objects.create(
            title=title,
            slug=slug,
            status=status,
            published_at=published_at,
        )

        if artist is not None:
            album.artists.add(artist)

        return album

    def get_result_ids(self, results):
        return [
            result.object.pk
            for result in results
        ]

    # ========================================================
    # Basic search behavior
    # ========================================================

    def test_search_returns_matching_song(self):
        song = self.create_song(
            title="Unavailable",
            slug="unavailable",
            artist=self.artist,
        )

        results = self.service.search(
            query="Unavailable",
            entity_type="song",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].object, song)
        self.assertEqual(results[0].entity_type, "song")

    def test_exact_title_ranks_above_partial_title_match(self):
        exact_match = self.create_song(
            title="Golden",
            slug="golden",
            artist=self.artist,
        )

        partial_match = self.create_song(
            title="Golden Hour",
            slug="golden-hour",
            artist=self.artist,
        )

        results = self.service.search(
            query="Golden",
            entity_type="song",
        )

        self.assertEqual(
            self.get_result_ids(results),
            [
                exact_match.pk,
                partial_match.pk,
            ],
        )

    def test_search_supports_artist_and_title_matches(self):
        song = self.create_song(
            title="Unavailable",
            slug="davido-unavailable",
            artist=self.artist,
        )

        results = self.service.search(
            query="Davido Unavailable",
            entity_type="song",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].object, song)

    def test_search_requires_complete_token_matches(self):
        song = self.create_song(
            title="Lil5ive",
            slug="lil5ive",
            artist=self.artist,
        )

        results = self.service.search(
            query="5ive",
            entity_type="song",
        )

        self.assertNotIn(
            song.pk,
            self.get_result_ids(results),
        )

    def test_search_is_case_insensitive(self):
        song = self.create_song(
            title="Unavailable",
            slug="unavailable",
            artist=self.artist,
        )

        results = self.service.search(
            query="UNAVAILABLE",
            entity_type="song",
        )

        self.assertEqual(
            self.get_result_ids(results),
            [song.pk],
        )

    # ========================================================
    # Entity hints
    # ========================================================

    def test_search_recognizes_song_entity_hint(self):
        song = self.create_song(
            title="Unavailable",
            slug="unavailable",
            artist=self.artist,
        )

        results = self.service.search(
            query="song Unavailable",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].entity_type, "song")
        self.assertEqual(results[0].object, song)

    def test_explicit_entity_type_overrides_query_hint(self):
        album = self.create_album(
            title="Unavailable",
            slug="unavailable-album",
            artist=self.artist,
        )

        results = self.service.search(
            query="song Unavailable",
            entity_type="album",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].entity_type, "album")
        self.assertEqual(results[0].object, album)

    def test_conflicting_entity_hints_do_not_select_last_hint(self):
        song = self.create_song(
            title="Unavailable",
            slug="unavailable",
            artist=self.artist,
        )

        results = self.service.search(
            query="song artist Unavailable",
        )

        self.assertEqual(
            {result.entity_type for result in results},
            {"song"},
        )

        self.assertEqual(
            self.get_result_ids(results),
            [song.pk],
        )

    # ========================================================
    # Pagination
    # ========================================================

    def test_offset_returns_next_batch_without_duplicates(self):
        songs = [
            self.create_song(
                title=title,
                slug=slug,
                artist=self.artist,
            )
            for title, slug in (
                ("Golden", "golden"),
                ("Golden Hour", "golden-hour"),
                ("Golden Nights", "golden-nights"),
            )
        ]

        first_page = self.service.search(
            query="Golden",
            entity_type="song",
            limit=2,
            offset=0,
        )

        second_page = self.service.search(
            query="Golden",
            entity_type="song",
            limit=2,
            offset=2,
        )

        first_ids = self.get_result_ids(first_page)
        second_ids = self.get_result_ids(second_page)

        self.assertEqual(len(first_page), 2)
        self.assertEqual(len(second_page), 1)

        self.assertEqual(
            first_ids + second_ids,
            [song.pk for song in songs],
        )

        self.assertTrue(
            set(first_ids).isdisjoint(second_ids)
        )

    def test_zero_offset_returns_first_page(self):
        song = self.create_song(
            title="Unavailable",
            slug="unavailable",
            artist=self.artist,
        )

        results = self.service.search(
            query="Unavailable",
            entity_type="song",
            limit=10,
            offset=0,
        )

        self.assertEqual(
            self.get_result_ids(results),
            [song.pk],
        )

    def test_negative_offset_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.search(
                query="Unavailable",
                entity_type="song",
                offset=-1,
            )

    # ========================================================
    # Public catalog visibility
    # ========================================================

    def test_public_song_search_excludes_drafts_and_archived_songs(self):
        published_song = self.create_song(
            title="Unavailable",
            slug="published-unavailable",
            artist=self.artist,
            status=Song.Status.PUBLISHED,
        )

        self.create_song(
            title="Unavailable",
            slug="draft-unavailable",
            artist=self.artist,
            status=Song.Status.DRAFT,
        )

        self.create_song(
            title="Unavailable",
            slug="archived-unavailable",
            artist=self.artist,
            status=Song.Status.ARCHIVED,
        )

        results = self.service.search(
            query="Unavailable",
            entity_type="song",
            public_only=True,
        )

        self.assertEqual(
            self.get_result_ids(results),
            [published_song.pk],
        )

    def test_public_album_search_excludes_drafts_and_archived_albums(self):
        published_album = self.create_album(
            title="Timeless Deluxe",
            slug="timeless-deluxe",
            artist=self.artist,
            status=Album.Status.PUBLISHED,
        )

        self.create_album(
            title="Timeless Deluxe",
            slug="timeless-deluxe-draft",
            artist=self.artist,
            status=Album.Status.DRAFT,
        )

        self.create_album(
            title="Timeless Deluxe",
            slug="timeless-deluxe-archived",
            artist=self.artist,
            status=Album.Status.ARCHIVED,
        )

        results = self.service.search(
            query="Timeless Deluxe",
            entity_type="album",
            public_only=True,
        )

        self.assertEqual(
            self.get_result_ids(results),
            [published_album.pk],
        )

    def test_public_artist_search_excludes_inactive_artists(self):
        active_artist = Artist.objects.create(
            name="Test Performer",
            slug="test-performer",
            is_active=True,
        )

        Artist.objects.create(
            name="Test Performer",
            slug="inactive-test-performer",
            is_active=False,
        )

        results = self.service.search(
            query="Test Performer",
            entity_type="artist",
            public_only=True,
        )

        self.assertEqual(
            self.get_result_ids(results),
            [active_artist.pk],
        )

    def test_default_search_does_not_apply_public_visibility_filter(self):
        draft_song = self.create_song(
            title="Private Release",
            slug="private-release",
            artist=self.artist,
            status=Song.Status.DRAFT,
        )

        results = self.service.search(
            query="Private Release",
            entity_type="song",
        )

        self.assertEqual(
            self.get_result_ids(results),
            [draft_song.pk],
        )

    # ========================================================
    # Validation and empty searches
    # ========================================================

    def test_empty_query_returns_no_results(self):
        results = self.service.search(query="   ")

        self.assertEqual(results, [])

    def test_query_longer_than_maximum_length_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.search(
                query="a" * (
                    self.service.MAX_QUERY_LENGTH + 1
                ),
            )

    def test_unsupported_entity_type_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.search(
                query="Unavailable",
                entity_type="community_post",
            )
    
    def test_search_with_count_returns_matching_total(self):
        results, count = self.service.search_with_count(
            query="Davido",
            entity_type="artist",
            limit=10,
        )

        self.assertEqual(count, 1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].entity_type, "artist")
        self.assertEqual(results[0].object, self.artist)

    def test_search_with_count_applies_offset_after_ranking(self):
        first_page, total_count = self.service.search_with_count(
            query="Davido",
            entity_type="artist",
            limit=1,
            offset=0,
        )

        second_page, second_count = self.service.search_with_count(
            query="Davido",
            entity_type="artist",
            limit=1,
            offset=1,
        )

        self.assertEqual(total_count, 1)
        self.assertEqual(total_count, second_count)

        self.assertEqual(len(first_page), 1)
        self.assertEqual(len(second_page), 0)

        self.assertEqual(first_page[0].object, self.artist)

    def test_search_with_count_excludes_unpublished_songs(self):
        published_song = self.create_song(
            title="Unavailable",
            slug="published-unavailable",
            artist=self.artist,
            status=Song.Status.PUBLISHED,
        )

        self.create_song(
            title="Unavailable",
            slug="draft-unavailable",
            artist=self.artist,
            status=Song.Status.DRAFT,
        )

        self.create_song(
            title="Unavailable",
            slug="archived-unavailable",
            artist=self.artist,
            status=Song.Status.ARCHIVED,
        )

        results, count = self.service.search_with_count(
            query="Unavailable",
            entity_type="song",
            public_only=True,
        )

        self.assertEqual(count, 1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].object, published_song)

    def test_search_with_count_rejects_negative_offset(self):
        with self.assertRaises(ValueError):
            MusicCatalogSearchService().search_with_count(
                query="Burna Boy",
                entity_type="artist",
                offset=-1,
            )

