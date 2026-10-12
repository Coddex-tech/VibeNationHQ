from __future__ import annotations

from dataclasses import replace

from .base import (
    MusicProviderError,
    MusicSearchQuery,
    MusicSearchResult,
)
from .ranking import MusicSearchRanker
from .registry import MusicProviderRegistry


class MusicSearchAggregator:
    """
    Combines search results from all registered music providers.

    Providers remain responsible for fetching and normalizing
    their own data. The aggregator combines those normalized
    results into one VibeNationHQ search result set.

    The aggregator is intentionally provider-agnostic so that
    additional providers can be added later without changing
    the search flow.
    """

    MAX_PROVIDER_RESULTS = 50
    PROVIDER_RESULT_MULTIPLIER = 3

    def __init__(
        self,
        registry: MusicProviderRegistry | None = None,
        ranker: MusicSearchRanker | None = None,
    ):
        self.registry = (
            registry
            if registry is not None
            else MusicProviderRegistry()
        )

        self.ranker = (
            ranker
            if ranker is not None
            else MusicSearchRanker()
        )

    def search(
        self,
        query: MusicSearchQuery,
    ) -> list[MusicSearchResult]:
        if not query.query.strip():
            return []

        provider_limit = min(
            max(
                query.limit
                * self.PROVIDER_RESULT_MULTIPLIER,
                query.limit,
            ),
            self.MAX_PROVIDER_RESULTS,
        )

        provider_query = replace(
            query,
            limit=provider_limit,
        )

        results: list[MusicSearchResult] = []

        for provider in self.registry.all():
            try:
                provider_results = provider.search(
                    provider_query
                )
            except MusicProviderError:
                # A single provider being unavailable should not
                # prevent other providers from returning results.
                continue

            results.extend(provider_results)

        deduplicated = self._deduplicate(results)

        ranked = self.ranker.rank(
            query=query,
            results=deduplicated,
        )

        return ranked[:query.limit]

    def _deduplicate(
        self,
        results: list[MusicSearchResult],
    ) -> list[MusicSearchResult]:
        deduplicated: list[MusicSearchResult] = []

        for result in results:
            duplicate_index = self._find_duplicate(
                result=result,
                existing=deduplicated,
            )

            if duplicate_index is None:
                deduplicated.append(result)
                continue

            existing = deduplicated[duplicate_index]

            deduplicated[duplicate_index] = (
                self._merge_results(
                    existing=existing,
                    incoming=result,
                )
            )

        return deduplicated

    def _find_duplicate(
        self,
        *,
        result: MusicSearchResult,
        existing: list[MusicSearchResult],
    ) -> int | None:
        for index, candidate in enumerate(existing):
            if result.entity_type != candidate.entity_type:
                continue

            if self._same_isrc(result, candidate):
                return index

            if self._same_recording(result, candidate):
                return index

        return None

    @staticmethod
    def _same_isrc(
        first: MusicSearchResult,
        second: MusicSearchResult,
    ) -> bool:
        if not first.isrc or not second.isrc:
            return False

        return (
            first.isrc.strip().upper()
            == second.isrc.strip().upper()
        )

    @staticmethod
    def _same_recording(
        first: MusicSearchResult,
        second: MusicSearchResult,
    ) -> bool:
        """
        Conservative fallback when an ISRC is unavailable.

        Results are only merged when the title, artist and
        duration are sufficiently aligned. This intentionally
        avoids aggressive fuzzy matching.
        """

        first_title = MusicSearchAggregator._normalize_text(
            first.title
        )
        second_title = MusicSearchAggregator._normalize_text(
            second.title
        )

        first_artist = MusicSearchAggregator._normalize_text(
            first.artist_name
        )
        second_artist = MusicSearchAggregator._normalize_text(
            second.artist_name
        )

        if not first_title or not second_title:
            return False

        if not first_artist or not second_artist:
            return False

        if first_title != second_title:
            return False

        if first_artist != second_artist:
            return False

        if (
            first.duration_seconds is None
            or second.duration_seconds is None
        ):
            return False

        return (
            abs(
                first.duration_seconds
                - second.duration_seconds
            )
            <= 2
        )

    @staticmethod
    def _normalize_text(
        value: str | None,
    ) -> str:
        if not value:
            return ""

        return " ".join(
            value.casefold().strip().split()
        )

    @staticmethod
    def _merge_results(
        *,
        existing: MusicSearchResult,
        incoming: MusicSearchResult,
    ) -> MusicSearchResult:
        """
        Keep the richer result while filling missing metadata
        from the other provider.

        The aggregator does not assume a specific provider is
        always preferred. Provider-specific quality decisions
        belong in the provider ranking layer.
        """

        preferred = MusicSearchAggregator._choose_preferred(
            existing,
            incoming,
        )

        secondary = (
            incoming
            if preferred is existing
            else existing
        )

        metadata = {
            **secondary.metadata,
            **preferred.metadata,
        }

        metadata["sources"] = sorted(
            {
                existing.provider.value,
                incoming.provider.value,
            }
        )

        return replace(
            preferred,
            artwork_url=(
                preferred.artwork_url
                or secondary.artwork_url
            ),
            release_date=(
                preferred.release_date
                or secondary.release_date
            ),
            duration_seconds=(
                preferred.duration_seconds
                if preferred.duration_seconds is not None
                else secondary.duration_seconds
            ),
            preview_url=(
                preferred.preview_url
                or secondary.preview_url
            ),
            spotify_url=(
                preferred.spotify_url
                or secondary.spotify_url
            ),
            apple_music_url=(
                preferred.apple_music_url
                or secondary.apple_music_url
            ),
            youtube_url=(
                preferred.youtube_url
                or secondary.youtube_url
            ),
            audiomack_url=(
                preferred.audiomack_url
                or secondary.audiomack_url
            ),
            boomplay_url=(
                preferred.boomplay_url
                or secondary.boomplay_url
            ),
            country=(
                preferred.country
                or secondary.country
            ),
            isrc=(
                preferred.isrc
                or secondary.isrc
            ),
            metadata=metadata,
        )

    @staticmethod
    def _choose_preferred(
        first: MusicSearchResult,
        second: MusicSearchResult,
    ) -> MusicSearchResult:
        """
        Select the richer result when duplicate entities
        are returned by different providers.

        With only one active provider today, this normally
        returns the first result unchanged. The method remains
        provider-agnostic so future provider quality rules
        can be introduced without changing the aggregation flow.
        """

        return first