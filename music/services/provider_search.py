from __future__ import annotations

import re

from music.providers.aggregator import MusicSearchAggregator
from music.providers.base import (
    MusicEntityType,
    MusicSearchQuery,
    MusicSearchResult,
)
from music.services.provider_catalog_match import (
    MusicProviderCatalogMatcher,
)


class MusicProviderSearchService:
    """
    Search external providers and exclude results already represented
    in the canonical VibeNationHQ catalog.

    Entity hints in the query are interpreted before provider search.
    For example, "Davido 5ive album" searches for "Davido 5ive"
    with album intent.

    Searching remains read-only. Importing a provider result is still
    an explicit, separate operation.
    """

    DEFAULT_LIMIT = 10
    MAX_LIMIT = 20
    MAX_QUERY_LENGTH = 200
    CANDIDATE_MULTIPLIER = 3
    MAX_CANDIDATES = 50

    ENTITY_HINTS = {
        "song": MusicEntityType.SONG,
        "songs": MusicEntityType.SONG,
        "track": MusicEntityType.SONG,
        "tracks": MusicEntityType.SONG,
        "album": MusicEntityType.ALBUM,
        "albums": MusicEntityType.ALBUM,
        "artist": MusicEntityType.ARTIST,
        "artists": MusicEntityType.ARTIST,
    }

    ENTITY_HINT_PATTERN = re.compile(
        r"\b(?:songs?|tracks?|albums?|artists?)\b",
        flags=re.IGNORECASE,
    )

    def __init__(
        self,
        aggregator: MusicSearchAggregator | None = None,
        catalog_matcher: MusicProviderCatalogMatcher | None = None,
    ):
        self.aggregator = (
            aggregator
            if aggregator is not None
            else MusicSearchAggregator()
        )

        self.catalog_matcher = (
            catalog_matcher
            if catalog_matcher is not None
            else MusicProviderCatalogMatcher()
        )

    def search(
        self,
        *,
        query: str,
        entity_type: MusicEntityType | None = None,
        country: str = "NG",
        limit: int = DEFAULT_LIMIT,
    ) -> list[MusicSearchResult]:
        """
        Search external providers, rank their results, and remove
        conservative matches against the canonical catalog.

        Entity hints are removed from the text sent to providers.
        An explicitly supplied entity_type takes precedence over
        any entity type inferred from the query.

        Extra candidates are fetched before catalog filtering so
        duplicates do not unnecessarily leave the result list underfilled.
        """

        normalized_query = query.strip()

        if not normalized_query:
            return []

        if len(normalized_query) > self.MAX_QUERY_LENGTH:
            raise ValueError("Search query is too long.")

        normalized_country = country.strip().upper()

        if (
            len(normalized_country) != 2
            or not normalized_country.isalpha()
        ):
            raise ValueError(
                "Country must be a 2-letter country code."
            )

        normalized_limit = min(
            max(limit, 1),
            self.MAX_LIMIT,
        )

        candidate_limit = min(
            normalized_limit * self.CANDIDATE_MULTIPLIER,
            self.MAX_CANDIDATES,
        )

        cleaned_query, inferred_entity_type = (
            self._extract_entity_hint(normalized_query)
        )

        # A query consisting only of entity hints does not identify
        # an artist, album, or song to search for.
        if not cleaned_query:
            return []

        effective_entity_type = (
            entity_type
            if entity_type is not None
            else inferred_entity_type
        )

        search_query = MusicSearchQuery(
            query=cleaned_query,
            entity_type=effective_entity_type,
            country=normalized_country,
            limit=candidate_limit,
        )

        provider_results = self.aggregator.search(
            search_query
        )

        filtered_results = self.catalog_matcher.filter_existing(
            provider_results
        )

        return filtered_results[:normalized_limit]

    @classmethod
    def _extract_entity_hint(
        cls,
        query: str,
    ) -> tuple[str, MusicEntityType | None]:
        """
        Remove entity-hint words and infer a requested entity type.

        Examples:
            "Davido 5ive album" -> ("Davido 5ive", ALBUM)
            "Wizkid songs"      -> ("Wizkid", SONG)
            "Tems artist"       -> ("Tems", ARTIST)

        If conflicting entity hints are present, no entity type is
        inferred. The caller's explicit entity_type still takes
        precedence over the inferred value.
        """

        hint_types = {
            cls.ENTITY_HINTS[match.group(0).casefold()]
            for match in cls.ENTITY_HINT_PATTERN.finditer(query)
        }

        cleaned_query = cls.ENTITY_HINT_PATTERN.sub(
            " ",
            query,
        )

        # Collapse extra whitespace left behind by removed hints.
        cleaned_query = " ".join(cleaned_query.split())

        inferred_entity_type = (
            next(iter(hint_types))
            if len(hint_types) == 1
            else None
        )

        return cleaned_query, inferred_entity_type