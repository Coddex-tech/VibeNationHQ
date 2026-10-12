from __future__ import annotations

from django.test import TestCase

from music.models import Genre
from music.services.genre_normalization import (
    GenreNormalizer,
)


class GenreNormalizerTests(TestCase):
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

        self.inactive = Genre.objects.create(
            name="Inactive Genre",
            slug="inactive-genre",
            is_active=False,
        )

    def test_normalize_name_trims_and_lowercases(self):
        result = GenreNormalizer.normalize_name(
            "  AfroBeats  ",
        )

        self.assertEqual(
            result,
            "afrobeats",
        )

    def test_normalize_name_normalizes_dash_variants(self):
        result = GenreNormalizer.normalize_name(
            "Afro-Pop",
        )

        self.assertEqual(
            result,
            "afro-pop",
        )

    def test_canonical_name_resolves_afro_pop_alias(self):
        result = GenreNormalizer.canonical_name(
            "Afro-Pop",
        )

        self.assertEqual(
            result,
            "Afrobeats",
        )

    def test_canonical_name_resolves_hiphop_alias(self):
        result = GenreNormalizer.canonical_name(
            "HipHop",
        )

        self.assertEqual(
            result,
            "Hip-Hop",
        )

    def test_canonical_name_resolves_rnb_alias(self):
        result = GenreNormalizer.canonical_name(
            "RnB",
        )

        self.assertEqual(
            result,
            "R&B",
        )

    def test_resolve_returns_matching_active_genres(self):
        genres = GenreNormalizer.resolve(
            [
                "Afrobeats",
                "Hip-Hop",
            ],
        )

        self.assertEqual(
            genres,
            [
                self.afrobeats,
                self.hip_hop,
            ],
        )

    def test_resolve_applies_aliases(self):
        genres = GenreNormalizer.resolve(
            [
                "Afro-Pop",
                "HipHop",
                "RnB",
            ],
        )

        self.assertEqual(
            genres,
            [
                self.afrobeats,
                self.hip_hop,
                self.rnb,
            ],
        )

    def test_resolve_ignores_unknown_genres(self):
        genres = GenreNormalizer.resolve(
            [
                "Afrobeats",
                "Completely Unknown Genre",
            ],
        )

        self.assertEqual(
            genres,
            [
                self.afrobeats,
            ],
        )

    def test_resolve_ignores_inactive_genres(self):
        genres = GenreNormalizer.resolve(
            [
                "Inactive Genre",
            ],
        )

        self.assertEqual(
            genres,
            [],
        )

    def test_resolve_deduplicates_genres(self):
        genres = GenreNormalizer.resolve(
            [
                "Afrobeats",
                "afro-pop",
                "AFROBEATS",
            ],
        )

        self.assertEqual(
            genres,
            [
                self.afrobeats,
            ],
        )

    def test_resolve_ignores_empty_values(self):
        genres = GenreNormalizer.resolve(
            [
                None,
                "",
                "   ",
                "Afrobeats",
            ],
        )

        self.assertEqual(
            genres,
            [
                self.afrobeats,
            ],
        )

    def test_resolve_does_not_create_genres(self):
        before_count = Genre.objects.count()

        GenreNormalizer.resolve(
            [
                "Afrobeats",
                "Brand New Genre",
                "Another Unknown Genre",
            ],
        )

        after_count = Genre.objects.count()

        self.assertEqual(
            after_count,
            before_count,
        )

    def test_resolve_returns_empty_for_empty_input(self):
        genres = GenreNormalizer.resolve([])

        self.assertEqual(
            genres,
            [],
        )