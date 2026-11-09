from __future__ import annotations

import re
import unicodedata
from dataclasses import replace

from .base import (
    MusicEntityType,
    MusicProviderError,
    MusicSearchQuery,
    MusicSearchResult,
)
from .ranking import MusicSearchRanker
from .registry import MusicProviderRegistry


class MusicSearchAggregator:
    """
    Combines normalized search results from registered music providers.

    Responsibilities:
    - Query registered providers independently.
    - Continue when an individual provider fails.
    - Deduplicate equivalent songs, albums, and artists.
    - Merge useful metadata from duplicate results.
    - Rank the combined results.
    - Respect the requested result limit.
    """

    MAX_PROVIDER_RESULTS = 50

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

        normalized_limit = min(
            max(query.limit, 1),
            self.MAX_PROVIDER_RESULTS,
        )

        provider_query = replace(
            query,
            limit=normalized_limit,
        )

        results: list[MusicSearchResult] = []

        for provider in self.registry.all():
            try:
                provider_results = provider.search(provider_query)
            except MusicProviderError:
                # A single provider being unavailable should not
                # prevent other providers from returning results.
                continue

            if provider_results:
                results.extend(provider_results)

        deduplicated = self._deduplicate(results)

        ranked = self.ranker.rank(
            query=query,
            results=deduplicated,
        )

        return ranked[:normalized_limit]

    def _deduplicate(
        self,
        results: list[MusicSearchResult],
    ) -> list[MusicSearchResult]:
        """
        Deduplicate results using indexed candidate keys.

        Candidate indexes avoid comparing every incoming result
        against every result already collected. Final duplicate
        decisions still use entity-specific matching rules.
        """

        deduplicated: list[MusicSearchResult] = []

        indexes: dict[tuple[str, ...], list[int]] = {}

        for result in results:
            candidate_indexes: set[int] = set()

            for key in self._duplicate_keys(result):
                candidate_indexes.update(indexes.get(key, []))

            duplicate_index = next(
                (
                    index
                    for index in sorted(candidate_indexes)
                    if self._are_duplicates(
                        result,
                        deduplicated[index],
                    )
                ),
                None,
            )

            if duplicate_index is None:
                result_index = len(deduplicated)
                deduplicated.append(result)
            else:
                result_index = duplicate_index

                deduplicated[result_index] = self._merge_results(
                    existing=deduplicated[result_index],
                    incoming=result,
                )

            # Index both the incoming result and the merged result.
            # This preserves lookup paths if the preferred metadata
            # comes from a different provider.
            for indexed_result in (
                result,
                deduplicated[result_index],
            ):
                for key in self._duplicate_keys(indexed_result):
                    bucket = indexes.setdefault(key, [])

                    if result_index not in bucket:
                        bucket.append(result_index)

        return deduplicated

    @classmethod
    def _duplicate_keys(
        cls,
        result: MusicSearchResult,
    ) -> list[tuple[str, ...]]:
        """
        Generate conservative keys for finding possible duplicates.

        Keys identify candidates only; _are_duplicates() makes the
        final decision.
        """

        keys: list[tuple[str, ...]] = []
        entity_type = result.entity_type

        if result.isrc:
            normalized_isrc = result.isrc.strip().upper()

            if normalized_isrc:
                keys.append(
                    ("isrc", str(entity_type), normalized_isrc)
                )

        title = cls._normalize_text(result.title)
        artist = cls._normalize_text(result.artist_name)

        if entity_type == MusicEntityType.SONG:
            if title and artist:
                keys.append(
                    ("song", title, artist)
                )

        elif entity_type == MusicEntityType.ALBUM:
            if title and artist:
                keys.append(
                    ("album", title, artist)
                )

        elif entity_type == MusicEntityType.ARTIST:
            # Artist providers commonly put the artist's name in
            # the normalized result's title field.
            artist_title = title or artist

            if artist_title:
                keys.append(
                    ("artist", artist_title)
                )

        return keys

    @classmethod
    def _are_duplicates(
        cls,
        first: MusicSearchResult,
        second: MusicSearchResult,
    ) -> bool:
        """Apply entity-specific rules to candidate duplicates."""

        if first.entity_type != second.entity_type:
            return False

        if cls._same_isrc(first, second):
            return True

        if first.entity_type == MusicEntityType.SONG:
            return cls._same_recording(first, second)

        if first.entity_type == MusicEntityType.ALBUM:
            return cls._same_album(first, second)

        if first.entity_type == MusicEntityType.ARTIST:
            return cls._same_artist(first, second)

        return False

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

    @classmethod
    def _same_recording(
        cls,
        first: MusicSearchResult,
        second: MusicSearchResult,
    ) -> bool:
        """
        Match songs conservatively when an ISRC is unavailable.

        Require the same normalized title, artist credit, and
        durations within two seconds.
        """

        first_title = cls._normalize_text(first.title)
        second_title = cls._normalize_text(second.title)

        first_artist = cls._normalize_text(first.artist_name)
        second_artist = cls._normalize_text(second.artist_name)

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

    @classmethod
    def _same_album(
        cls,
        first: MusicSearchResult,
        second: MusicSearchResult,
    ) -> bool:
        """
        Match albums by normalized title and artist.

        Album duration is deliberately not used because providers
        can report different durations or omit them entirely.
        """

        first_title = cls._normalize_text(first.title)
        second_title = cls._normalize_text(second.title)

        first_artist = cls._normalize_text(first.artist_name)
        second_artist = cls._normalize_text(second.artist_name)

        if not first_title or not second_title:
            return False

        if not first_artist or not second_artist:
            return False

        return (
            first_title == second_title
            and first_artist == second_artist
        )

    @classmethod
    def _same_artist(
        cls,
        first: MusicSearchResult,
        second: MusicSearchResult,
    ) -> bool:
        """Match artist entities by their normalized display names."""

        first_name = cls._normalize_text(
            first.title or first.artist_name
        )
        second_name = cls._normalize_text(
            second.title or second.artist_name
        )

        return bool(
            first_name
            and second_name
            and first_name == second_name
        )

    @staticmethod
    def _normalize_text(
        value: str | None,
    ) -> str:
        if not value:
            return ""

        value = unicodedata.normalize(
            "NFKC",
            value,
        ).casefold()

        value = re.sub(
            r"[^\w\s]",
            " ",
            value,
            flags=re.UNICODE,
        )

        return " ".join(value.split())

    @staticmethod
    def _merge_results(
        *,
        existing: MusicSearchResult,
        incoming: MusicSearchResult,
    ) -> MusicSearchResult:
        """
        Prefer the result with more useful metadata while filling
        missing fields from the other provider.
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
    def _result_completeness(
        result: MusicSearchResult,
    ) -> int:
        """Estimate metadata completeness for merge selection."""

        values = (
            result.artist_name,
            result.album_name,
            result.artwork_url,
            result.release_date,
            result.duration_seconds,
            result.preview_url,
            result.spotify_url,
            result.apple_music_url,
            result.youtube_url,
            result.audiomack_url,
            result.boomplay_url,
            result.isrc,
        )

        completeness = sum(
            value is not None and value != ""
            for value in values
        )

        return completeness + len(result.metadata)

    @staticmethod
    def _choose_preferred(
        first: MusicSearchResult,
        second: MusicSearchResult,
    ) -> MusicSearchResult:
        """
        Select the result with more available metadata.

        Equal scores retain the first result for deterministic
        selection.
        """

        first_score = MusicSearchAggregator._result_completeness(
            first
        )
        second_score = MusicSearchAggregator._result_completeness(
            second
        )

        if second_score > first_score:
            return second

        return first