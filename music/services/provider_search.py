from __future__ import annotations

from music.providers.aggregator import MusicSearchAggregator
from music.providers.base import (
    MusicEntityType,
    MusicSearchQuery,
    MusicSearchResult,
)


class MusicProviderSearchService:
    """
    Search external music providers.

    This service is separate from MusicSearchService, which searches
    VibeNationHQ's own internal music catalog.

    External provider results are fetched, deduplicated, and ranked
    by MusicSearchAggregator.
    """

    DEFAULT_LIMIT = 10
    MAX_LIMIT = 20
    MAX_QUERY_LENGTH = 200

    def __init__(
        self,
        aggregator: MusicSearchAggregator | None = None,
    ):
        self.aggregator = (
            aggregator
            if aggregator is not None
            else MusicSearchAggregator()
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
        Search external music providers.

        Provider-specific API calls, normalization, deduplication,
        and ranking are handled by the aggregator.
        """

        normalized_query = query.strip()

        if not normalized_query:
            return []

        if len(normalized_query) > self.MAX_QUERY_LENGTH:
            raise ValueError(
                "Search query is too long."
            )

        normalized_country = country.strip().upper()

        if len(normalized_country) != 2:
            raise ValueError(
                "Country must be a 2-letter country code."
            )

        normalized_limit = min(
            max(limit, 1),
            self.MAX_LIMIT,
        )

        search_query = MusicSearchQuery(
            query=normalized_query,
            entity_type=entity_type,
            country=normalized_country,
            limit=normalized_limit,
        )

        return self.aggregator.search(
            search_query
        )