
from __future__ import annotations

import re
import unicodedata

from django.db.models import Q, QuerySet

from music.models import (
    Album,
    Artist,
    MusicProviderIdentity,
    Song,
)
from music.providers.base import MusicSearchResult


class MusicProviderCatalogMatcher:
    """
    Removes external search results already represented in the
    canonical VibeNationHQ catalog.

    Matching priority:
    1. Exact provider identity.
    2. Exact normalized title and artist credits.

    Matching is deliberately conservative: a title match alone,
    or a match against a featured artist alone, is insufficient
    to suppress a provider result.
    """

    MAX_TITLE_CANDIDATES = 500

    _CREDIT_SEPARATOR = re.compile(
        r"\s+(?:feat(?:uring)?\.?|ft\.?|with|and|x)\s+"
        r"|\s*&\s*"
        r"|\s*,\s*"
        r"|\s*;\s*",
        flags=re.IGNORECASE,
    )

    def filter_existing(
        self,
        results: list[MusicSearchResult],
    ) -> list[MusicSearchResult]:
        if not results:
            return []

        known_identities = self._known_provider_identities(results)
        visible_results: list[MusicSearchResult] = []

        for result in results:
            identity_key = (
                result.provider.value,
                result.entity_type.value,
                result.provider_id,
            )

            if identity_key in known_identities:
                continue

            if self._matches_catalog_record(result):
                continue

            visible_results.append(result)

        return visible_results

    @staticmethod
    def _known_provider_identities(
        results: list[MusicSearchResult],
    ) -> set[tuple[str, str, str]]:
        identity_filter = Q()

        for result in results:
            identity_filter |= Q(
                provider=result.provider.value,
                entity_type=result.entity_type.value,
                provider_id=result.provider_id,
            )

        if not identity_filter:
            return set()

        return set(
            MusicProviderIdentity.objects.filter(
                identity_filter
            ).values_list(
                "provider",
                "entity_type",
                "provider_id",
            )
        )

    def _matches_catalog_record(
        self,
        result: MusicSearchResult,
    ) -> bool:
        entity_type = result.entity_type.value

        if entity_type == "artist":
            return self._matches_artist(result)

        if entity_type == "album":
            return self._matches_album(result)

        if entity_type == "song":
            return self._matches_song(result)

        return False

    def _matches_artist(
        self,
        result: MusicSearchResult,
    ) -> bool:
        external_name = self._normalize(result.title)

        if not external_name:
            return False

        return any(
            self._normalize(candidate.name) == external_name
            for candidate in self._artist_candidates(
                name=result.title
            )
        )

    def _matches_album(
        self,
        result: MusicSearchResult,
    ) -> bool:
        external_title = self._normalize(result.title)
        external_artists = self._artist_credits(
            result.artist_name
        )

        if not external_title or not external_artists:
            return False

        for album in self._album_candidates(title=result.title):
            if self._normalize(album.title) != external_title:
                continue

            canonical_artists = {
                self._normalize(artist.name)
                for artist in album.artists.all()
            }
            canonical_artists.discard("")

            if external_artists == canonical_artists:
                return True

        return False

    def _matches_song(
        self,
        result: MusicSearchResult,
    ) -> bool:
        external_title = self._normalize(result.title)
        external_artists = self._artist_credits(
            result.artist_name
        )

        if not external_title or not external_artists:
            return False

        for song in self._song_candidates(title=result.title):
            if self._normalize(song.title) != external_title:
                continue

            primary_artists = {
                self._normalize(artist.name)
                for artist in song.artists.all()
            }
            primary_artists.discard("")

            featured_artists = {
                self._normalize(artist.name)
                for artist in song.featured_artists.all()
            }
            featured_artists.discard("")

            # A provider's single-artist credit should match the
            # canonical primary-artist credit, not merely a feature.
            if external_artists == primary_artists:
                return True

            # For collaborations, require the complete credited set.
            canonical_credits = primary_artists | featured_artists

            if (
                len(external_artists) > 1
                and external_artists == canonical_credits
            ):
                return True

        return False

    def _artist_candidates(
        self,
        *,
        name: str,
    ) -> QuerySet[Artist]:
        tokens = self._candidate_tokens(name)

        if not tokens:
            return Artist.objects.none()

        query = Q()

        for token in tokens:
            query |= Q(name__icontains=token)
            query |= Q(slug__icontains=token)

        return (
            Artist.objects.filter(query)
            .order_by("id")[: self.MAX_TITLE_CANDIDATES]
        )

    def _album_candidates(
        self,
        *,
        title: str,
    ) -> QuerySet[Album]:
        tokens = self._candidate_tokens(title)

        if not tokens:
            return Album.objects.none()

        query = Q()

        for token in tokens:
            query |= Q(title__icontains=token)

        return (
            Album.objects.filter(query)
            .prefetch_related("artists")
            .order_by("id")[: self.MAX_TITLE_CANDIDATES]
        )

    def _song_candidates(
        self,
        *,
        title: str,
    ) -> QuerySet[Song]:
        tokens = self._candidate_tokens(title)

        if not tokens:
            return Song.objects.none()

        query = Q()

        for token in tokens:
            query |= Q(title__icontains=token)

        return (
            Song.objects.filter(query)
            .prefetch_related(
                "artists",
                "featured_artists",
            )
            .order_by("id")[: self.MAX_TITLE_CANDIDATES]
        )

    @classmethod
    def _artist_credits(
        cls,
        value: str | None,
    ) -> set[str]:
        if not value or not value.strip():
            return set()

        cleaned_value = value.strip()
        parts = cls._CREDIT_SEPARATOR.split(cleaned_value)

        credits = {
            cls._normalize(part)
            for part in parts
            if cls._normalize(part)
        }

        return credits

    @classmethod
    def _candidate_tokens(
        cls,
        value: str,
    ) -> list[str]:
        tokens = cls._normalize(value).split()

        # Search using every distinct token. Final matching still
        # requires exact normalized titles or artist names.
        return sorted(
            set(tokens),
            key=lambda token: (-len(token), token),
        )

    @staticmethod
    def _normalize(
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
