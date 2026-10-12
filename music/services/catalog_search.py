from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from django.db.models import Q, QuerySet

from music.models import Album, Artist, Song


CatalogEntityType = Literal[
    "song",
    "album",
    "artist",
]


@dataclass(frozen=True, slots=True)
class CatalogSearchResult:
    """
    A normalized result from the internal VibeNationHQ
    music catalog.
    """

    entity_type: CatalogEntityType
    object: Song | Album | Artist


class MusicCatalogSearchService:
    """
    Searches the canonical VibeNationHQ music catalog.

    This service only reads existing catalog records.
    It never imports or creates provider records.
    """

    DEFAULT_LIMIT = 10
    MAX_LIMIT = 20
    MAX_QUERY_LENGTH = 200

    def search(
        self,
        *,
        query: str,
        entity_type: CatalogEntityType | None = None,
        limit: int = DEFAULT_LIMIT,
    ) -> list[CatalogSearchResult]:
        normalized_query = query.strip()

        if not normalized_query:
            return []

        if len(normalized_query) > self.MAX_QUERY_LENGTH:
            raise ValueError(
                "Search query is too long."
            )

        normalized_limit = min(
            max(limit, 1),
            self.MAX_LIMIT,
        )

        if entity_type is None:
            return self._search_all(
                normalized_query,
                normalized_limit,
            )

        if entity_type == "song":
            return self._search_songs(
                normalized_query,
                normalized_limit,
            )

        if entity_type == "album":
            return self._search_albums(
                normalized_query,
                normalized_limit,
            )

        if entity_type == "artist":
            return self._search_artists(
                normalized_query,
                normalized_limit,
            )

        raise ValueError(
            f"Unsupported catalog entity type: "
            f"'{entity_type}'."
        )

    def _search_all(
        self,
        query: str,
        limit: int,
    ) -> list[CatalogSearchResult]:
        """
        Search each canonical entity type independently.

        The limit applies to each entity type so that a query
        does not cause one model to consume the entire result set.
        """
        results: list[CatalogSearchResult] = []

        results.extend(
            self._search_songs(
                query,
                limit,
            )
        )

        results.extend(
            self._search_artists(
                query,
                limit,
            )
        )

        results.extend(
            self._search_albums(
                query,
                limit,
            )
        )

        return results

    def _search_songs(
        self,
        query: str,
        limit: int,
    ) -> list[CatalogSearchResult]:
        queryset: QuerySet[Song] = (
            Song.objects
            .filter(
                Q(title__icontains=query)
                | Q(
                    artists__name__icontains=query,
                )
                | Q(
                    featured_artists__name__icontains=query,
                )
                | Q(
                    album__title__icontains=query,
                )
            )
            .distinct()
            .prefetch_related(
                "artists",
                "featured_artists",
            )
            .select_related("album")
            .order_by("title", "id")[:limit]
        )

        return [
            CatalogSearchResult(
                entity_type="song",
                object=song,
            )
            for song in queryset
        ]

    def _search_artists(
        self,
        query: str,
        limit: int,
    ) -> list[CatalogSearchResult]:
        queryset: QuerySet[Artist] = (
            Artist.objects
            .filter(
                Q(name__icontains=query)
                | Q(slug__icontains=query)
            )
            .order_by("name", "id")[:limit]
        )

        return [
            CatalogSearchResult(
                entity_type="artist",
                object=artist,
            )
            for artist in queryset
        ]

    def _search_albums(
        self,
        query: str,
        limit: int,
    ) -> list[CatalogSearchResult]:
        queryset: QuerySet[Album] = (
            Album.objects
            .filter(
                Q(title__icontains=query)
                | Q(
                    artists__name__icontains=query,
                )
            )
            .distinct()
            .prefetch_related("artists")
            .order_by("title", "id")[:limit]
        )

        return [
            CatalogSearchResult(
                entity_type="album",
                object=album,
            )
            for album in queryset
        ]