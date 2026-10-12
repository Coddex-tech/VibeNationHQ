from __future__ import annotations

import re

from .base import MusicSearchQuery, MusicSearchResult


class MusicSearchRanker:
    """
    Scores and ranks normalized music search results.

    The ranker is provider-agnostic. It does not fetch external
    data or modify provider results.

    Ranking considers:

    - Exact title, artist, and album matches.
    - Artist credit matching.
    - Artist + song-title search intent.
    - Token coverage and field relevance.
    - Canonical title matching.
    - Partial and substring matches.
    - Provider-supplied relevance scores.
    - Availability of useful metadata.
    - Alternate-version penalties.

    The scoring system intentionally favors user intent over
    metadata completeness.
    """

    # Strong signals should dominate weaker metadata signals.
    EXACT_TITLE_SCORE = 120.0
    EXACT_ARTIST_SCORE = 150.0
    EXACT_ALBUM_SCORE = 100.0
    EXACT_CANONICAL_TITLE_SCORE = 110.0

    ARTIST_CREDIT_SCORE = 125.0
    ARTIST_TITLE_INTENT_SCORE = 250.0
    EXACT_ARTIST_TITLE_SCORE = 350.0

    ENTITY_TYPE_SCORE = 15.0

    TOKEN_COVERAGE_SCORE = 50.0
    TITLE_TOKEN_SCORE = 25.0
    TITLE_COMPLETE_SCORE = 45.0

    CANONICAL_TITLE_TOKEN_SCORE = 35.0
    CANONICAL_TITLE_COMPLETE_SCORE = 70.0

    ARTIST_TOKEN_SCORE = 35.0
    ARTIST_COMPLETE_SCORE = 55.0

    ALBUM_TOKEN_SCORE = 15.0

    TITLE_SUBSTRING_SCORE = 40.0
    ARTIST_SUBSTRING_SCORE = 35.0
    ALBUM_SUBSTRING_SCORE = 30.0
    CANONICAL_TITLE_SUBSTRING_SCORE = 55.0

    ARTWORK_SCORE = 2.0
    PREVIEW_SCORE = 4.0
    APPLE_MUSIC_LINK_SCORE = 1.0
    SPOTIFY_LINK_SCORE = 1.0

    PROVIDER_SCORE_MULTIPLIER = 0.05

    def rank(
        self,
        *,
        query: MusicSearchQuery,
        results: list[MusicSearchResult],
    ) -> list[MusicSearchResult]:
        """
        Rank search results from most relevant to least relevant.

        Original result order is used as the final tie-breaker so
        provider ordering is preserved when two results have the
        same relevance score.
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

    def _score(
        self,
        *,
        query: MusicSearchQuery,
        result: MusicSearchResult,
    ) -> float:
        query_text = self._normalize_text(
            query.query
        )

        if not query_text:
            return 0.0

        query_tokens = set(
            self._tokenize(query_text)
        )

        title = self._normalize_text(
            result.title
        )
        artist = self._normalize_text(
            result.artist_name
        )
        album = self._normalize_text(
            result.album_name
        )

        title_tokens = set(
            self._tokenize(title)
        )
        artist_tokens = set(
            self._tokenize(artist)
        )
        album_tokens = set(
            self._tokenize(album)
        )

        canonical_title = self._canonical_title(
            result.title
        )

        canonical_title_tokens = set(
            self._tokenize(canonical_title)
        )

        score = 0.0

        # ---------------------------------------------------------
        # Exact field matches
        # ---------------------------------------------------------

        if title == query_text:
            score += self.EXACT_TITLE_SCORE

        if artist == query_text:
            score += self.EXACT_ARTIST_SCORE

        if album == query_text:
            score += self.EXACT_ALBUM_SCORE

        if canonical_title == query_text:
            score += self.EXACT_CANONICAL_TITLE_SCORE

        # ---------------------------------------------------------
        # Artist credit matching
        # ---------------------------------------------------------

        if self._artist_credit_matches(
            query_text=query_text,
            artist_name=result.artist_name or "",
        ):
            score += self.ARTIST_CREDIT_SCORE

        # ---------------------------------------------------------
        # Requested entity type
        # ---------------------------------------------------------

        if (
            query.entity_type is not None
            and result.entity_type == query.entity_type
        ):
            score += self.ENTITY_TYPE_SCORE

        # ---------------------------------------------------------
        # Query token coverage
        # ---------------------------------------------------------

        if query_tokens:
            searchable_tokens = (
                canonical_title_tokens
                | artist_tokens
                | album_tokens
            )

            matched_tokens = (
                query_tokens
                & searchable_tokens
            )

            coverage = (
                len(matched_tokens)
                / len(query_tokens)
            )

            score += (
                coverage
                * self.TOKEN_COVERAGE_SCORE
            )

        # ---------------------------------------------------------
        # Title relevance
        # ---------------------------------------------------------

        title_matches = len(
            query_tokens
            & title_tokens
        )

        if title_matches:
            score += (
                title_matches
                * self.TITLE_TOKEN_SCORE
            )

        if (
            query_tokens
            and query_tokens.issubset(title_tokens)
        ):
            score += self.TITLE_COMPLETE_SCORE

        # ---------------------------------------------------------
        # Canonical title relevance
        # ---------------------------------------------------------

        canonical_title_matches = len(
            query_tokens
            & canonical_title_tokens
        )

        if canonical_title_matches:
            score += (
                canonical_title_matches
                * self.CANONICAL_TITLE_TOKEN_SCORE
            )

        if (
            query_tokens
            and query_tokens.issubset(
                canonical_title_tokens
            )
        ):
            score += (
                self.CANONICAL_TITLE_COMPLETE_SCORE
            )

        # ---------------------------------------------------------
        # Artist relevance
        # ---------------------------------------------------------

        artist_matches = len(
            query_tokens
            & artist_tokens
        )

        if artist_matches:
            score += (
                artist_matches
                * self.ARTIST_TOKEN_SCORE
            )

        if (
            query_tokens
            and query_tokens.issubset(
                artist_tokens
            )
        ):
            score += self.ARTIST_COMPLETE_SCORE

        # ---------------------------------------------------------
        # Album relevance
        # ---------------------------------------------------------

        album_matches = len(
            query_tokens
            & album_tokens
        )

        if album_matches:
            score += (
                album_matches
                * self.ALBUM_TOKEN_SCORE
            )

        # ---------------------------------------------------------
        # Artist + title search intent
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # Query substring matches
        # ---------------------------------------------------------

        if (
            query_text
            and query_text in title
        ):
            score += self.TITLE_SUBSTRING_SCORE

        if (
            query_text
            and query_text in artist
        ):
            score += self.ARTIST_SUBSTRING_SCORE

        if (
            query_text
            and query_text in album
        ):
            score += self.ALBUM_SUBSTRING_SCORE

        if (
            query_text
            and query_text in canonical_title
        ):
            score += (
                self.CANONICAL_TITLE_SUBSTRING_SCORE
            )

        # ---------------------------------------------------------
        # Provider-supplied relevance
        # ---------------------------------------------------------

        provider_score = self._get_provider_score(
            result
        )

        if provider_score is not None:
            score += (
                provider_score
                * self.PROVIDER_SCORE_MULTIPLIER
            )

        # ---------------------------------------------------------
        # Useful metadata
        # ---------------------------------------------------------

        if result.artwork_url:
            score += self.ARTWORK_SCORE

        if result.preview_url:
            score += self.PREVIEW_SCORE

        if result.apple_music_url:
            score += self.APPLE_MUSIC_LINK_SCORE

        if result.spotify_url:
            score += self.SPOTIFY_LINK_SCORE

        # ---------------------------------------------------------
        # Alternate-version penalty
        # ---------------------------------------------------------

        score -= self._version_penalty(
            query=query_text,
            result=result,
        )

        return score

    @classmethod
    def _has_artist_title_intent_match(
        cls,
        *,
        query_tokens: set[str],
        title_tokens: set[str],
        artist_tokens: set[str],
    ) -> bool:
        """
        Detect queries that contain meaningful tokens belonging
        to both an artist and a title.

        Examples:

            Burna Boy Last Last
            Wizkid Essence
            Davido Awuke
        """

        if not query_tokens:
            return False

        title_matches = (
            query_tokens
            & title_tokens
        )

        artist_matches = (
            query_tokens
            & artist_tokens
        )

        if not title_matches or not artist_matches:
            return False

        # Prevent a query such as "Burna Boy" from being treated
        # as an artist + title search simply because the same token
        # happens to occur in both fields.
        return bool(
            title_matches - artist_matches
        ) and bool(
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
        """
        Detect a query containing a complete artist credit and
        the remaining tokens matching the canonical title.

        Examples:

            "Burna Boy Last Last"
            "Wizkid Essence"
            "Davido Awuke"
        """

        if not query_tokens:
            return False

        artist_credits = cls._split_artist_credits(
            artist_name
        )

        if not artist_credits:
            return False

        for credit in artist_credits:
            credit_tokens = set(
                cls._tokenize(
                    cls._normalize_text(credit)
                )
            )

            if not credit_tokens:
                continue

            if not credit_tokens.issubset(
                query_tokens
            ):
                continue

            remaining_tokens = (
                query_tokens
                - credit_tokens
            )

            if not remaining_tokens:
                continue

            if remaining_tokens.issubset(
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
        """
        Check whether the complete query matches the artist
        name or one of its individual artist credits.
        """

        if not query_text or not artist_name:
            return False

        normalized_query = (
            cls._normalize_artist_text(
                query_text
            )
        )

        normalized_artist = (
            cls._normalize_artist_text(
                artist_name
            )
        )

        if normalized_artist == normalized_query:
            return True

        credits = cls._split_artist_credits(
            artist_name
        )

        normalized_credits = {
            cls._normalize_artist_text(
                credit
            )
            for credit in credits
        }

        return normalized_query in normalized_credits

    @classmethod
    def _split_artist_credits(
        cls,
        artist_name: str,
    ) -> set[str]:
        """
        Split common artist collaboration formats.

        Examples:

            Davido & YG Marley
            Davido feat. YG Marley
            Davido ft YG Marley
            Davido featuring YG Marley
            Davido with YG Marley
            Davido, YG Marley
            Davido; YG Marley
            Davido x YG Marley
        """

        if not artist_name:
            return set()

        normalized = artist_name.casefold()

        # Treat ampersands as collaboration separators.
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

    @staticmethod
    def _canonical_title(
        value: str | None,
    ) -> str:
        """
        Extract a simpler title for search matching.

        Examples:

            "Essence (feat. Tems)"
                -> "essence"

            "Awuke (ADP Club Mix)"
                -> "awuke"

            "Terminator [Instrumental Version]"
                -> "terminator"
        """

        title = MusicSearchRanker._normalize_text(
            value
        )

        if not title:
            return ""

        # Remove a trailing parenthetical/bracketed qualifier
        # when it describes a common alternate-version or
        # collaboration form.
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

        return " ".join(
            title.split()
        )

    @classmethod
    def _version_penalty(
        cls,
        *,
        query: str,
        result: MusicSearchResult,
    ) -> float:
        """
        Penalize alternate versions when the user did not ask
        for that version.

        If the user explicitly searches for the corresponding
        version keyword, no penalty is applied for that keyword.
        """

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

    @staticmethod
    def _get_provider_score(
        result: MusicSearchResult,
    ) -> float | None:
        """
        Read an optional provider-supplied relevance score.

        Providers do not have to supply a score. Invalid values
        are ignored rather than affecting search ranking.
        """

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
        """
        Normalize artist names while preserving word boundaries.
        """

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

        return " ".join(
            value.split()
        )

    @staticmethod
    def _normalize_text(
        value: str | None,
    ) -> str:
        """
        Normalize general searchable text.

        Punctuation is converted to spaces so searches such as:

            "Last-Last"
            "Last Last"

        can still match.
        """

        if not value:
            return ""

        value = value.casefold().strip()

        value = re.sub(
            r"[^\w\s]",
            " ",
            value,
        )

        return " ".join(
            value.split()
        )

    @staticmethod
    def _tokenize(
        value: str,
    ) -> list[str]:
        """
        Convert normalized text into meaningful search tokens.

        Single-character tokens are ignored because they generally
        provide very little search relevance.
        """

        if not value:
            return []

        return [
            token
            for token in value.split()
            if len(token) > 1
        ]