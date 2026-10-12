from __future__ import annotations

import re

from music.models import Genre


class GenreNormalizer:
    """
    Normalizes external/provider genre names into VibeNationHQ's
    canonical Genre records.

    External providers never create Genre records. Only genres
    already configured in the VibeNationHQ catalog are returned.
    """

    ALIASES: dict[str, str] = {
        "afro pop": "Afrobeats",
        "afropop": "Afrobeats",
        "afro-pop": "Afrobeats",
        "afro beat": "Afrobeats",
        "afrobeats": "Afrobeats",
        "afro-beats": "Afrobeats",
        "hip hop": "Hip-Hop",
        "hip-hop": "Hip-Hop",
        "hiphop": "Hip-Hop",
        "r&b": "R&B",
        "rnb": "R&B",
        "rhythm and blues": "R&B",
    }

    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        """
        Normalize a provider genre name for matching.

        This does not determine the canonical Genre record.
        It only produces a stable comparison value.
        """
        value = value.strip().lower()

        value = re.sub(
            r"[\u2010-\u2015\u2212]",
            "-",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value

    @classmethod
    def canonical_name(
        cls,
        value: str,
    ) -> str:
        """
        Convert a provider genre name into the canonical name
        expected by the VibeNationHQ Genre table.
        """
        normalized = cls.normalize_name(value)

        return cls.ALIASES.get(
            normalized,
            value.strip(),
        )

    @classmethod
    def resolve(
        cls,
        values: list[str | None],
    ) -> list[Genre]:
        """
        Resolve provider genre names to active canonical Genre
        records.

        Unknown genres are ignored.

        Duplicate canonical genres are returned only once.
        """
        names: list[str] = []

        for value in values:
            if not value:
                continue

            canonical = cls.canonical_name(value)

            if not canonical:
                continue

            names.append(canonical)

        if not names:
            return []

        genres = Genre.objects.filter(
            is_active=True,
        )

        resolved: list[Genre] = []
        seen_ids: set[int] = set()

        canonical_lookup = {
            cls.normalize_name(genre.name): genre
            for genre in genres
        }

        for name in names:
            normalized = cls.normalize_name(name)

            genre = canonical_lookup.get(normalized)

            if genre is None:
                continue

            if genre.id in seen_ids:
                continue

            seen_ids.add(genre.id)
            resolved.append(genre)

        return resolved