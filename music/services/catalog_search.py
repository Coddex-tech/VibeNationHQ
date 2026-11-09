from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Literal

from django.db.models import Q, QuerySet

from music.models import Album, Artist, Song


CatalogEntityType = Literal["song", "album", "artist"]


@dataclass(frozen=True, slots=True)
class CatalogSearchResult:
    """A normalized result from the internal music catalog."""

    entity_type: CatalogEntityType
    object: Song | Album | Artist


class MusicCatalogSearchService:
    """
    Searches the canonical VibeNationHQ music catalog.

    Search behavior:
    - Recognizes song, track, album, and artist entity hints.
    - Removes entity hints before matching catalog fields.
    - Gives explicit API entity types precedence over query hints.
    - Treats conflicting hints as ambiguous.
    - Prioritizes exact titles and artist-plus-title matches.
    - Uses album information as supporting context for songs.
    - Requires every meaningful query token to match a complete
      token in at least one searchable field.
    - Supports relevance-ranked offset pagination.
    - Supports optional public-catalog visibility filtering.
    - Keeps the service read-only.
    """

    DEFAULT_LIMIT = 10
    MAX_LIMIT = 20
    MAX_QUERY_LENGTH = 200
    MAX_CANDIDATES = 500

    ENTITY_HINTS: dict[str, CatalogEntityType] = {
        "song": "song",
        "songs": "song",
        "track": "song",
        "tracks": "song",
        "album": "album",
        "albums": "album",
        "artist": "artist",
        "artists": "artist",
    }

    ENTITY_TYPE_PRIORITY: dict[CatalogEntityType, int] = {
        "album": 0,
        "song": 1,
        "artist": 2,
    }

    def search(
        self,
        *,
        query: str,
        entity_type: CatalogEntityType | None = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
        public_only: bool = False,
    ) -> list[CatalogSearchResult]:
        """
        Search the canonical catalog.

        Args:
            query:
                Search phrase.

            entity_type:
                Optional entity restriction.

            limit:
                Maximum number of results to return.

            offset:
                Number of relevance-ranked results to skip.

            public_only:
                When True, return only publicly visible catalog
                records. Existing callers retain their previous
                behavior because this defaults to False.
        """

        if len(query.strip()) > self.MAX_QUERY_LENGTH:
            raise ValueError("Search query is too long.")

        if entity_type not in (None, "song", "album", "artist"):
            raise ValueError(
                f"Unsupported catalog entity type: '{entity_type}'."
            )

        if offset < 0:
            raise ValueError("Search offset cannot be negative.")

        normalized_query = self._normalize_text(query)

        if not normalized_query:
            return []

        normalized_query, inferred_entity_type = (
            self._extract_entity_hint(normalized_query)
        )

        if not normalized_query:
            return []

        effective_entity_type = (
            entity_type
            if entity_type is not None
            else inferred_entity_type
        )

        normalized_limit = min(max(limit, 1), self.MAX_LIMIT)

        if effective_entity_type == "song":
            return self._search_songs(
                normalized_query,
                normalized_limit,
                offset=offset,
                public_only=public_only,
            )

        if effective_entity_type == "album":
            return self._search_albums(
                normalized_query,
                normalized_limit,
                offset=offset,
                public_only=public_only,
            )

        if effective_entity_type == "artist":
            return self._search_artists(
                normalized_query,
                normalized_limit,
                offset=offset,
                public_only=public_only,
            )

        results: list[CatalogSearchResult] = []

        results.extend(
            self._search_songs(
                normalized_query,
                normalized_limit,
                public_only=public_only,
            )
        )
        results.extend(
            self._search_artists(
                normalized_query,
                normalized_limit,
                public_only=public_only,
            )
        )
        results.extend(
            self._search_albums(
                normalized_query,
                normalized_limit,
                public_only=public_only,
            )
        )

        results.sort(
            key=lambda result: (
                -self._score_result(normalized_query, result),
                self._entity_type_priority(result.entity_type),
                self._object_name(result.object).casefold(),
                result.object.pk,
            )
        )

        start = offset
        end = offset + (normalized_limit * 3)

        return results[start:end]

    def search_with_count(
        self,
        *,
        query: str,
        entity_type: CatalogEntityType,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
        public_only: bool = False,
    ) -> tuple[list[CatalogSearchResult], int]:
        """
        Search one catalog category and return its results
        alongside the total number of relevance-matched candidates.

        This method is intended for independently paginated
        category searches, such as global search.

        The count is bounded by MAX_CANDIDATES, matching the
        catalog service's existing candidate-evaluation limit.
        """

        if len(query.strip()) > self.MAX_QUERY_LENGTH:
            raise ValueError("Search query is too long.")

        if entity_type not in ("song", "album", "artist"):
            raise ValueError(
                f"Unsupported catalog entity type: '{entity_type}'."
            )

        if offset < 0:
            raise ValueError("Search offset cannot be negative.")

        normalized_query = self._normalize_text(query)

        if not normalized_query:
            return [], 0

        normalized_query, _ = self._extract_entity_hint(
            normalized_query,
        )

        if not normalized_query:
            return [], 0

        normalized_limit = min(max(limit, 1), self.MAX_LIMIT)

        if entity_type == "song":
            queryset = Song.objects.filter(
                self._candidate_filter(
                    normalized_query,
                    (
                        "title",
                        "artists__name",
                        "featured_artists__name",
                        "album__title",
                    ),
                )
            )

            if public_only:
                queryset = queryset.filter(
                    status=Song.Status.PUBLISHED,
                )

            queryset = (
                queryset
                .distinct()
                .select_related("album")
                .prefetch_related(
                    "artists",
                    "featured_artists",
                )
                .order_by("pk")[: self.MAX_CANDIDATES]
            )

        elif entity_type == "album":
            queryset = Album.objects.filter(
                self._candidate_filter(
                    normalized_query,
                    (
                        "title",
                        "artists__name",
                    ),
                )
            )

            if public_only:
                queryset = queryset.filter(
                    status=Album.Status.PUBLISHED,
                )

            queryset = (
                queryset
                .distinct()
                .prefetch_related("artists")
                .order_by("pk")[: self.MAX_CANDIDATES]
            )

        else:
            queryset = Artist.objects.filter(
                self._candidate_filter(
                    normalized_query,
                    ("name",),
                )
            )

            if public_only:
                queryset = queryset.filter(
                    is_active=True,
                )

            queryset = queryset.order_by("pk")[
                : self.MAX_CANDIDATES
            ]

        return self._rank_candidates_with_count(
            query=normalized_query,
            objects=queryset,
            entity_type=entity_type,
            limit=normalized_limit,
            offset=offset,
        )

    @classmethod
    def _extract_entity_hint(
        cls,
        query: str,
    ) -> tuple[str, CatalogEntityType | None]:
        """
        Remove entity hints without allowing the last hint to win
        when the query contains conflicting entity types.
        """

        remaining_tokens: list[str] = []
        recognized_types: set[CatalogEntityType] = set()

        for token in query.split():
            entity_hint = cls.ENTITY_HINTS.get(token)

            if entity_hint is None:
                remaining_tokens.append(token)
            else:
                recognized_types.add(entity_hint)

        inferred_entity_type = (
            next(iter(recognized_types))
            if len(recognized_types) == 1
            else None
        )

        return " ".join(remaining_tokens), inferred_entity_type

    @staticmethod
    def _entity_type_priority(
        entity_type: CatalogEntityType,
    ) -> int:
        return MusicCatalogSearchService.ENTITY_TYPE_PRIORITY[
            entity_type
        ]

    def _search_songs(
        self,
        query: str,
        limit: int,
        *,
        offset: int = 0,
        public_only: bool = False,
    ) -> list[CatalogSearchResult]:
        queryset = Song.objects.filter(
            self._candidate_filter(
                query,
                (
                    "title",
                    "artists__name",
                    "featured_artists__name",
                    "album__title",
                ),
            )
        )

        if public_only:
            queryset = queryset.filter(
                status=Song.Status.PUBLISHED,
            )

        queryset = (
            queryset
            .distinct()
            .select_related("album")
            .prefetch_related("artists", "featured_artists")
            .order_by("pk")[: self.MAX_CANDIDATES]
        )

        return self._rank_candidates(
            query=query,
            objects=queryset,
            entity_type="song",
            limit=limit,
            offset=offset,
        )

    def _search_albums(
        self,
        query: str,
        limit: int,
        *,
        offset: int = 0,
        public_only: bool = False,
    ) -> list[CatalogSearchResult]:
        queryset = Album.objects.filter(
            self._candidate_filter(
                query,
                ("title", "artists__name"),
            )
        )

        if public_only:
            queryset = queryset.filter(
                status=Album.Status.PUBLISHED,
            )

        queryset = (
            queryset
            .distinct()
            .prefetch_related("artists")
            .order_by("pk")[: self.MAX_CANDIDATES]
        )

        return self._rank_candidates(
            query=query,
            objects=queryset,
            entity_type="album",
            limit=limit,
            offset=offset,
        )

    def _search_artists(
        self,
        query: str,
        limit: int,
        *,
        offset: int = 0,
        public_only: bool = False,
    ) -> list[CatalogSearchResult]:
        queryset = Artist.objects.filter(
            self._candidate_filter(query, ("name",))
        )

        if public_only:
            queryset = queryset.filter(
                is_active=True,
            )

        queryset = queryset.order_by("pk")[
            : self.MAX_CANDIDATES
        ]

        return self._rank_candidates(
            query=query,
            objects=queryset,
            entity_type="artist",
            limit=limit,
            offset=offset,
        )

    @classmethod
    def _candidate_filter(
        cls,
        query: str,
        fields: tuple[str, ...],
    ) -> Q:
        """
        Build a broad database candidate filter.

        icontains is used to avoid excluding legitimate candidates
        before Python performs stricter complete-token matching.
        """

        tokens = set(cls._tokenize(query))

        if not tokens:
            return Q(pk__in=[])

        combined_filter = Q()

        for token in sorted(tokens):
            token_filter = Q()

            for field in fields:
                token_filter |= Q(
                    **{f"{field}__icontains": token}
                )

            combined_filter &= token_filter

        return combined_filter

    @classmethod
    def _rank_candidates(
        cls,
        *,
        query: str,
        objects: QuerySet,
        entity_type: CatalogEntityType,
        limit: int,
        offset: int = 0,
    ) -> list[CatalogSearchResult]:
        """
        Rank the bounded candidate set before applying pagination.

        Applying offset before ranking would produce incorrect
        relevance ordering.
        """

        ranked = [
            (
                cls._score_object(query, obj, entity_type),
                obj,
            )
            for obj in objects
        ]

        ranked = [
            item
            for item in ranked
            if item[0] > 0
        ]

        ranked.sort(
            key=lambda item: (
                -item[0],
                cls._object_name(item[1]).casefold(),
                item[1].pk,
            )
        )

        paginated = ranked[offset:offset + limit]

        return [
            CatalogSearchResult(
                entity_type=entity_type,
                object=obj,
            )
            for _, obj in paginated
        ]

    @classmethod
    def _rank_candidates_with_count(
        cls,
        *,
        query: str,
        objects: QuerySet,
        entity_type: CatalogEntityType,
        limit: int,
        offset: int = 0,
    ) -> tuple[list[CatalogSearchResult], int]:
        """
        Rank candidates, calculate the total matching count,
        and then apply offset pagination.

        Ranking always happens before pagination.
        """

        ranked = [
            (
                cls._score_object(
                    query,
                    obj,
                    entity_type,
                ),
                obj,
            )
            for obj in objects
        ]

        ranked = [
            item
            for item in ranked
            if item[0] > 0
        ]

        ranked.sort(
            key=lambda item: (
                -item[0],
                cls._object_name(item[1]).casefold(),
                item[1].pk,
            )
        )

        total_count = len(ranked)

        paginated = ranked[offset:offset + limit]

        results = [
            CatalogSearchResult(
                entity_type=entity_type,
                object=obj,
            )
            for _, obj in paginated
        ]

        return results, total_count

    @classmethod
    def _score_result(
        cls,
        query: str,
        result: CatalogSearchResult,
    ) -> float:
        return cls._score_object(
            query,
            result.object,
            result.entity_type,
        )

    @classmethod
    def _score_object(
        cls,
        query: str,
        obj: Song | Album | Artist,
        entity_type: CatalogEntityType,
    ) -> float:
        """
        Score catalog results using complete tokens rather than
        arbitrary substrings.
        """

        normalized_query = cls._normalize_text(query)
        query_tokens = set(cls._tokenize(normalized_query))

        if not query_tokens:
            return 0.0

        if entity_type == "artist":
            name_tokens = set(cls._tokenize(obj.name))

            if not query_tokens.issubset(name_tokens):
                return 0.0

            return cls._field_score(normalized_query, obj.name)

        title = obj.title
        title_tokens = set(cls._tokenize(title))
        title_matches = query_tokens & title_tokens

        if isinstance(obj, Song):
            artist_names = [
                artist.name
                for artist in obj.artists.all()
            ]
            artist_names.extend(
                artist.name
                for artist in obj.featured_artists.all()
            )
            album_name = obj.album.title if obj.album else ""
        else:
            artist_names = [
                artist.name
                for artist in obj.artists.all()
            ]
            album_name = ""

        artist_token_sets = [
            set(cls._tokenize(name))
            for name in artist_names
            if name
        ]

        combined_artist_tokens: set[str] = set()

        for tokens in artist_token_sets:
            combined_artist_tokens.update(tokens)

        album_tokens = set(cls._tokenize(album_name))

        searchable_tokens = (
            title_tokens
            | combined_artist_tokens
            | album_tokens
        )

        if not query_tokens.issubset(searchable_tokens):
            return 0.0

        score = 0.0

        if normalized_query == cls._normalize_text(title):
            score += 1000.0
        elif query_tokens.issubset(title_tokens):
            score += 700.0
        elif title_matches:
            score += (
                len(title_matches) / len(query_tokens)
            ) * 420.0

        if title_tokens and title_tokens.issubset(query_tokens):
            score += 60.0

        matching_artist_scores = [
            cls._field_score(normalized_query, artist_name)
            for artist_name in artist_names
            if query_tokens.issubset(
                set(cls._tokenize(artist_name))
            )
        ]

        if matching_artist_scores:
            score += 650.0
            score += max(matching_artist_scores) * 0.2
        else:
            artist_matches = query_tokens & combined_artist_tokens

            if artist_matches:
                score += (
                    len(artist_matches) / len(query_tokens)
                ) * 350.0

        if title_matches and (
            query_tokens & combined_artist_tokens
        ):
            score += 250.0

        if album_tokens:
            album_matches = query_tokens & album_tokens

            if query_tokens.issubset(album_tokens):
                score += 250.0
            elif album_matches:
                score += (
                    len(album_matches) / len(query_tokens)
                ) * 100.0

        return score

    @classmethod
    def _field_score(
        cls,
        query: str,
        value: str | None,
    ) -> float:
        """Score exact and complete-token field matches."""

        normalized_query = cls._normalize_text(query)
        normalized_value = cls._normalize_text(value)

        if not normalized_query or not normalized_value:
            return 0.0

        if normalized_value == normalized_query:
            return 1000.0

        query_tokens = set(cls._tokenize(normalized_query))
        value_tokens = set(cls._tokenize(normalized_value))

        if (
            not query_tokens
            or not query_tokens.issubset(value_tokens)
        ):
            return 0.0

        if normalized_value.startswith(normalized_query):
            return 800.0

        return 500.0

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

    @classmethod
    def _tokenize(
        cls,
        value: str,
    ) -> list[str]:
        return [
            token
            for token in cls._normalize_text(value).split()
            if token
        ]

    @staticmethod
    def _object_name(
        obj: Song | Album | Artist,
    ) -> str:
        return obj.name if isinstance(obj, Artist) else obj.title