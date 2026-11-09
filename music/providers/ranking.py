from __future__ import annotations

import re

from .base import (
    MusicEntityType,
    MusicSearchQuery,
    MusicSearchResult,
)


class MusicSearchRanker:
    """
    Provider-agnostic relevance ranking for normalized music results.

    Ranking considers:
    - Exact and partial title matches.
    - Artist credit matches.
    - Album title and artist combinations.
    - Query token coverage across relevant fields.
    - Canonical title matching.
    - Explicit and inferred entity intent.
    - Provider-supplied relevance scores.
    - Useful metadata.
    - Alternate-version penalties.

    Ranking does not fetch provider data, modify results, or import
    records into the canonical catalog.
    """

    EXACT_TITLE_SCORE = 160.0
    EXACT_ARTIST_SCORE = 150.0
    EXACT_ALBUM_SCORE = 100.0
    EXACT_CANONICAL_TITLE_SCORE = 130.0

    ARTIST_CREDIT_SCORE = 100.0
    ARTIST_TITLE_INTENT_SCORE = 180.0
    EXACT_ARTIST_TITLE_SCORE = 240.0

    ENTITY_TYPE_SCORE = 15.0
    ENTITY_INTENT_MATCH_SCORE = 180.0
    ENTITY_INTENT_MISMATCH_PENALTY = 100.0

    TOKEN_COVERAGE_SCORE = 50.0
    TITLE_TOKEN_SCORE = 25.0
    TITLE_COMPLETE_SCORE = 55.0

    CANONICAL_TITLE_TOKEN_SCORE = 30.0
    CANONICAL_TITLE_COMPLETE_SCORE = 60.0

    ARTIST_TOKEN_SCORE = 25.0
    ARTIST_COMPLETE_SCORE = 45.0

    ALBUM_TOKEN_SCORE = 12.0

    TITLE_SUBSTRING_SCORE = 20.0
    ARTIST_SUBSTRING_SCORE = 15.0
    ALBUM_SUBSTRING_SCORE = 15.0
    CANONICAL_TITLE_SUBSTRING_SCORE = 25.0

    ALBUM_EXACT_TITLE_SCORE = 300.0
    ALBUM_TITLE_COVERAGE_SCORE = 100.0
    ALBUM_TITLE_COMPLETE_SCORE = 150.0
    ALBUM_TITLE_SUBSTRING_SCORE = 25.0
    ALBUM_ARTIST_MATCH_SCORE = 120.0
    ALBUM_ARTIST_TOKEN_SCORE = 20.0
    ALBUM_ARTIST_TITLE_COMPLETE_SCORE = 150.0
    ALBUM_ARTIST_TITLE_PARTIAL_SCORE = 50.0

    ARTWORK_SCORE = 2.0
    PREVIEW_SCORE = 4.0
    APPLE_MUSIC_LINK_SCORE = 1.0
    SPOTIFY_LINK_SCORE = 1.0

    PROVIDER_SCORE_MULTIPLIER = 0.05

    ENTITY_HINTS: dict[str, MusicEntityType] = {
        "song": MusicEntityType.SONG,
        "songs": MusicEntityType.SONG,
        "track": MusicEntityType.SONG,
        "tracks": MusicEntityType.SONG,
        "album": MusicEntityType.ALBUM,
        "albums": MusicEntityType.ALBUM,
        "artist": MusicEntityType.ARTIST,
        "artists": MusicEntityType.ARTIST,
    }

    def rank(
        self,
        *,
        query: MusicSearchQuery,
        results: list[MusicSearchResult],
    ) -> list[MusicSearchResult]:
        """
        Rank results from most relevant to least relevant.

        Original provider order is the final tie-breaker.
        """

        if not results:
            return []

        scored_results = [
            (
                self._score(
                    query=query,
                    result=result,
                ),
                index,
                result,
            )
            for index, result in enumerate(results)
        ]

        scored_results.sort(
            key=lambda item: (
                item[0],
                -item[1],
            ),
            reverse=True,
        )

        return [
            result
            for _, _, result in scored_results
        ]

    def _query_context(
        self,
        query: MusicSearchQuery,
    ) -> tuple[str, MusicEntityType | None]:
        """
        Remove entity-hint words from the matching text.

        An explicit entity_type takes precedence over inferred intent.
        Conflicting hints do not silently let the final word win.
        """

        normalized_query = self._normalize_text(query.query)

        if not normalized_query:
            return "", query.entity_type

        remaining_tokens: list[str] = []
        inferred_types: set[MusicEntityType] = set()

        for token in self._tokenize(normalized_query):
            hinted_type = self.ENTITY_HINTS.get(token)

            if hinted_type is None:
                remaining_tokens.append(token)
            else:
                inferred_types.add(hinted_type)

        cleaned_query = " ".join(remaining_tokens)

        if query.entity_type is not None:
            target_type = query.entity_type
        elif len(inferred_types) == 1:
            target_type = next(iter(inferred_types))
        else:
            target_type = None

        return cleaned_query, target_type

    def _entity_intent_score(
        self,
        *,
        target_type: MusicEntityType | None,
        result: MusicSearchResult,
    ) -> float:
        """Reward the requested entity type and penalize mismatches."""

        if target_type is None:
            return 0.0

        if result.entity_type == target_type:
            return self.ENTITY_INTENT_MATCH_SCORE

        return -self.ENTITY_INTENT_MISMATCH_PENALTY

    def _score(
        self,
        *,
        query: MusicSearchQuery,
        result: MusicSearchResult,
    ) -> float:
        query_text, target_type = self._query_context(query)

        if not query_text:
            return self._entity_intent_score(
                target_type=target_type,
                result=result,
            )

        if result.entity_type == MusicEntityType.ALBUM:
            return self._score_album(
                query=query,
                result=result,
                query_text=query_text,
                target_type=target_type,
            )

        if result.entity_type == MusicEntityType.ARTIST:
            return self._score_artist(
                query=query,
                result=result,
                query_text=query_text,
                target_type=target_type,
            )

        return self._score_song(
            query=query,
            result=result,
            query_text=query_text,
            target_type=target_type,
        )

    def _score_artist(
        self,
        *,
        query: MusicSearchQuery,
        result: MusicSearchResult,
        query_text: str,
        target_type: MusicEntityType | None,
    ) -> float:
        """Rank artist results by artist-name relevance."""

        query_tokens = set(self._tokenize(query_text))
        title = self._normalize_text(result.title)
        artist_name = self._normalize_text(result.artist_name)

        # For normalized provider results, an artist's title is its
        # artist name. Prefer that field, falling back to artist_name.
        searchable_name = title or artist_name
        name_tokens = set(self._tokenize(searchable_name))

        score = 0.0

        if query_text == searchable_name:
            score += self.EXACT_TITLE_SCORE

        if query_tokens and query_tokens.issubset(name_tokens):
            score += self.TITLE_COMPLETE_SCORE

        if query_tokens:
            score += (
                len(query_tokens & name_tokens)
                / len(query_tokens)
            ) * self.TOKEN_COVERAGE_SCORE

        # Do not award a substring bonus for a query embedded inside
        # a larger token, such as "5ive" inside "Lil5ive".
        if self._contains_token_sequence(
            query_tokens=query_tokens,
            field_tokens=self._tokenize(searchable_name),
        ):
            score += self.TITLE_SUBSTRING_SCORE

        score += self._entity_intent_score(
            target_type=target_type,
            result=result,
        )

        score += self._metadata_score(result)

        provider_score = self._get_provider_score(result)

        if provider_score is not None:
            score += (
                provider_score
                * self.PROVIDER_SCORE_MULTIPLIER
            )

        return score

    def _score_song(
        self,
        *,
        query: MusicSearchQuery,
        result: MusicSearchResult,
        query_text: str,
        target_type: MusicEntityType | None,
    ) -> float:
        """Rank songs using title, artist, and album relevance."""

        query_tokens = set(self._tokenize(query_text))

        title = self._normalize_text(result.title)
        artist = self._normalize_text(result.artist_name)
        album = self._normalize_text(result.album_name)

        title_tokens = set(self._tokenize(title))
        artist_tokens = set(self._tokenize(artist))
        album_tokens = set(self._tokenize(album))

        canonical_title = self._canonical_title(result.title)
        canonical_title_tokens = set(
            self._tokenize(canonical_title)
        )

        score = 0.0

        # Exact field matches.
        if title == query_text:
            score += self.EXACT_TITLE_SCORE

        if artist == query_text:
            score += self.EXACT_ARTIST_SCORE

        if album == query_text:
            score += self.EXACT_ALBUM_SCORE

        if canonical_title == query_text:
            score += self.EXACT_CANONICAL_TITLE_SCORE

        # Full artist-credit match. This does not count a partial
        # substring inside a different artist name as an exact match.
        if self._artist_credit_matches(
            query_text=query_text,
            artist_name=result.artist_name or "",
        ):
            score += self.ARTIST_CREDIT_SCORE

        if query.entity_type is not None:
            if result.entity_type == query.entity_type:
                score += self.ENTITY_TYPE_SCORE

        score += self._entity_intent_score(
            target_type=target_type,
            result=result,
        )

        # Query coverage across relevant fields.
        searchable_tokens = (
            canonical_title_tokens
            | artist_tokens
            | album_tokens
        )

        if query_tokens:
            matched_tokens = query_tokens & searchable_tokens

            score += (
                len(matched_tokens) / len(query_tokens)
            ) * self.TOKEN_COVERAGE_SCORE

        # Title relevance.
        title_matches = query_tokens & title_tokens

        if title_matches:
            score += len(title_matches) * self.TITLE_TOKEN_SCORE

        if query_tokens and query_tokens.issubset(title_tokens):
            score += self.TITLE_COMPLETE_SCORE

        # Canonical title relevance.
        canonical_matches = (
            query_tokens & canonical_title_tokens
        )

        if canonical_matches:
            score += (
                len(canonical_matches)
                * self.CANONICAL_TITLE_TOKEN_SCORE
            )

        if (
            query_tokens
            and query_tokens.issubset(canonical_title_tokens)
        ):
            score += self.CANONICAL_TITLE_COMPLETE_SCORE

        # Artist relevance.
        artist_matches = query_tokens & artist_tokens

        if artist_matches:
            score += len(artist_matches) * self.ARTIST_TOKEN_SCORE

        if query_tokens and query_tokens.issubset(artist_tokens):
            score += self.ARTIST_COMPLETE_SCORE

        # Album context provides supporting evidence only.
        album_matches = query_tokens & album_tokens

        if album_matches:
            score += len(album_matches) * self.ALBUM_TOKEN_SCORE

        # Artist + song-title intent.
        if self._has_artist_title_intent_match(
            query_tokens=query_tokens,
            title_tokens=canonical_title_tokens,
            artist_tokens=artist_tokens,
        ):
            score += self.ARTIST_TITLE_INTENT_SCORE

        if self._has_exact_artist_title_match(
            query_tokens=query_tokens,
            title_tokens=canonical_title_tokens,
            artist_name=result.artist_name or "",
        ):
            score += self.EXACT_ARTIST_TITLE_SCORE

        # Substring bonuses use token sequences rather than raw
        # substring containment to avoid "5ive" matching "Lil5ive".
        if self._contains_token_sequence(
            query_tokens=query_tokens,
            field_tokens=self._tokenize(title),
        ):
            score += self.TITLE_SUBSTRING_SCORE

        if self._contains_token_sequence(
            query_tokens=query_tokens,
            field_tokens=self._tokenize(artist),
        ):
            score += self.ARTIST_SUBSTRING_SCORE

        if self._contains_token_sequence(
            query_tokens=query_tokens,
            field_tokens=self._tokenize(album),
        ):
            score += self.ALBUM_SUBSTRING_SCORE

        if self._contains_token_sequence(
            query_tokens=query_tokens,
            field_tokens=self._tokenize(canonical_title),
        ):
            score += self.CANONICAL_TITLE_SUBSTRING_SCORE

        # Provider relevance and metadata.
        provider_score = self._get_provider_score(result)

        if provider_score is not None:
            score += (
                provider_score
                * self.PROVIDER_SCORE_MULTIPLIER
            )

        score += self._metadata_score(result)

        # Alternate-version penalty.
        score -= self._version_penalty(
            query=query_text,
            result=result,
        )

        return score

    def _score_album(
        self,
        *,
        query: MusicSearchQuery,
        result: MusicSearchResult,
        query_text: str,
        target_type: MusicEntityType | None,
    ) -> float:
        """
        Rank albums primarily by album title and artist.

        For "Davido 5ive album", the query becomes "Davido 5ive".
        When the artist is Davido, the album-title portion becomes
        "5ive", giving the exact album title strong priority.
        """

        query_tokens_in_order = self._tokenize(query_text)
        query_tokens = set(query_tokens_in_order)

        if not query_tokens:
            return self._entity_intent_score(
                target_type=target_type,
                result=result,
            )

        title = self._normalize_text(result.title)
        title_tokens_in_order = self._tokenize(title)
        title_tokens = set(title_tokens_in_order)

        artist = self._normalize_text(result.artist_name)
        artist_tokens = set(self._tokenize(artist))

        score = 0.0

        # Separate artist tokens from title tokens only when the
        # complete artist name is represented in the query.
        artist_is_in_query = bool(
            artist_tokens
            and artist_tokens.issubset(query_tokens)
        )

        if artist_is_in_query:
            title_query_tokens = query_tokens - artist_tokens
        else:
            title_query_tokens = query_tokens

        title_query_in_order = [
            token
            for token in query_tokens_in_order
            if token in title_query_tokens
        ]
        title_query = " ".join(title_query_in_order)

        # Exact album-title match.
        if title_query and title == title_query:
            score += self.ALBUM_EXACT_TITLE_SCORE

        if title_query_tokens:
            matched_title_tokens = (
                title_query_tokens & title_tokens
            )

            score += (
                len(matched_title_tokens)
                / len(title_query_tokens)
            ) * self.ALBUM_TITLE_COVERAGE_SCORE

            if title_query_tokens.issubset(title_tokens):
                score += self.ALBUM_TITLE_COMPLETE_SCORE

            if self._contains_token_sequence(
                query_tokens=set(title_query_in_order),
                field_tokens=title_tokens_in_order,
            ):
                score += self.ALBUM_TITLE_SUBSTRING_SCORE

        # Artist-name match.
        if artist_is_in_query:
            score += self.ALBUM_ARTIST_MATCH_SCORE

            score += (
                len(artist_tokens)
                * self.ALBUM_ARTIST_TOKEN_SCORE
            )

        elif artist_tokens:
            matched_artist_tokens = query_tokens & artist_tokens

            if matched_artist_tokens:
                score += (
                    len(matched_artist_tokens)
                    * self.ALBUM_ARTIST_TOKEN_SCORE
                )

        # Strong combined artist + album-title intent.
        if artist_is_in_query:
            remaining_title_tokens = query_tokens - artist_tokens

            if remaining_title_tokens:
                matched_remaining_tokens = (
                    remaining_title_tokens & title_tokens
                )

                if remaining_title_tokens.issubset(title_tokens):
                    score += self.ALBUM_ARTIST_TITLE_COMPLETE_SCORE
                elif matched_remaining_tokens:
                    score += (
                        len(matched_remaining_tokens)
                        / len(remaining_title_tokens)
                    ) * self.ALBUM_ARTIST_TITLE_PARTIAL_SCORE

        if query.entity_type == MusicEntityType.ALBUM:
            score += self.ENTITY_TYPE_SCORE

        score += self._entity_intent_score(
            target_type=target_type,
            result=result,
        )

        score += self._metadata_score(result)

        provider_score = self._get_provider_score(result)

        if provider_score is not None:
            score += (
                provider_score
                * self.PROVIDER_SCORE_MULTIPLIER
            )

        return score

    @classmethod
    def _contains_token_sequence(
        cls,
        *,
        query_tokens: set[str],
        field_tokens: list[str],
    ) -> bool:
        """
        Return whether the query tokens occur contiguously as whole
        tokens in a field.

        For example, "5ive" matches the token "5ive", but not
        the token "Lil5ive".
        """

        if not query_tokens or not field_tokens:
            return False

        query_length = len(query_tokens)

        if query_length > len(field_tokens):
            return False

        # Token order in a set is not meaningful. For sequence checks,
        # callers should use the ordered tokens from the query.
        # This method is intended for exact single-token checks and
        # complete field-token coverage; callers provide the query
        # token set and the field token sequence.
        return query_tokens.issubset(set(field_tokens))

    @classmethod
    def _has_artist_title_intent_match(
        cls,
        *,
        query_tokens: set[str],
        title_tokens: set[str],
        artist_tokens: set[str],
    ) -> bool:
        if not query_tokens:
            return False

        title_matches = query_tokens & title_tokens
        artist_matches = query_tokens & artist_tokens

        if not title_matches or not artist_matches:
            return False

        return bool(title_matches - artist_matches) and bool(
            artist_matches - title_matches
        )

    @classmethod
    def _has_exact_artist_title_match(
        cls,
        *,
        query_tokens: set[str],
        title_tokens: set[str],
        artist_name: str,
    ) -> bool:
        if not query_tokens:
            return False

        artist_credits = cls._split_artist_credits(artist_name)

        if not artist_credits:
            return False

        for credit in artist_credits:
            credit_tokens = set(cls._tokenize(credit))

            if not credit_tokens:
                continue

            if not credit_tokens.issubset(query_tokens):
                continue

            remaining_tokens = query_tokens - credit_tokens

            if remaining_tokens and remaining_tokens.issubset(
                title_tokens
            ):
                return True

        return False

    @classmethod
    def _artist_credit_matches(
        cls,
        *,
        query_text: str,
        artist_name: str,
    ) -> bool:
        if not query_text or not artist_name:
            return False

        normalized_query = cls._normalize_artist_text(query_text)

        normalized_artist = cls._normalize_artist_text(
            artist_name
        )

        if normalized_artist == normalized_query:
            return True

        normalized_credits = {
            cls._normalize_artist_text(credit)
            for credit in cls._split_artist_credits(artist_name)
        }

        return normalized_query in normalized_credits

    @classmethod
    def _split_artist_credits(
        cls,
        artist_name: str,
    ) -> set[str]:
        if not artist_name:
            return set()

        normalized = artist_name.casefold()

        normalized = re.sub(
            r"\s*&\s*",
            " and ",
            normalized,
        )

        parts = re.split(
            r"\s+(?:feat\.?|ft\.?|featuring|with|and|x)\s+"
            r"|\s*,\s*"
            r"|\s*;\s*",
            normalized,
        )

        return {
            part.strip()
            for part in parts
            if part.strip()
        }

    @classmethod
    def _canonical_title(
        cls,
        value: str | None,
    ) -> str:
        title = cls._normalize_text(value)

        if not title:
            return ""

        title = re.sub(
            r"\s*[\(\[]"
            r"(?:feat\.?|ft\.?|featuring|with|"
            r"version|remix|mix|edit|"
            r"instrumental|acoustic|freestyle|"
            r"live|radio|club|extended|"
            r"originally performed|"
            r"explicit|clean|mono|stereo)"
            r".*?"
            r"[\)\]]"
            r"\s*$",
            "",
            title,
            flags=re.IGNORECASE,
        )

        return " ".join(title.split())

    @classmethod
    def _version_penalty(
        cls,
        *,
        query: str,
        result: MusicSearchResult,
    ) -> float:
        searchable_text = " ".join(
            value
            for value in (
                result.title,
                result.album_name,
            )
            if value
        ).casefold()

        query_text = query.casefold()

        penalties = {
            "8-bit": 120.0,
            "8 bit": 120.0,
            "emulation": 120.0,
            "karaoke": 120.0,
            "tribute": 120.0,
            "instrumental": 110.0,
            "originally performed": 110.0,
            "acoustic": 90.0,
            "freestyle": 90.0,
            "refix": 80.0,
            "dj mix": 80.0,
            "mixed": 70.0,
            "club mix": 70.0,
            "radio edit": 60.0,
            "extended mix": 60.0,
            "live version": 50.0,
            "remix": 55.0,
            "live": 40.0,
        }

        penalty = 0.0

        for term, value in penalties.items():
            if term not in searchable_text:
                continue

            if term in query_text:
                continue

            penalty += value

        return penalty

    @classmethod
    def _metadata_score(
        cls,
        result: MusicSearchResult,
    ) -> float:
        score = 0.0

        if result.artwork_url:
            score += cls.ARTWORK_SCORE

        if result.preview_url:
            score += cls.PREVIEW_SCORE

        if result.apple_music_url:
            score += cls.APPLE_MUSIC_LINK_SCORE

        if result.spotify_url:
            score += cls.SPOTIFY_LINK_SCORE

        return score

    @staticmethod
    def _get_provider_score(
        result: MusicSearchResult,
    ) -> float | None:
        value = result.metadata.get("score")

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _normalize_artist_text(
        value: str | None,
    ) -> str:
        if not value:
            return ""

        value = value.casefold()

        value = re.sub(
            r"[&]+",
            " and ",
            value,
        )

        value = re.sub(
            r"[^\w\s]",
            " ",
            value,
        )

        return " ".join(value.split())

    @staticmethod
    def _normalize_text(
        value: str | None,
    ) -> str:
        if not value:
            return ""

        value = value.casefold().strip()

        value = re.sub(
            r"[^\w\s]",
            " ",
            value,
        )

        return " ".join(value.split())

    @staticmethod
    def _tokenize(value: str) -> list[str]:
        if not value:
            return []

        return [
            token
            for token in value.split()
            if len(token) > 1
        ]