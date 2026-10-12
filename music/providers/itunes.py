from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .base import (
    MusicEntityType,
    MusicProviderError,
    MusicProviderName,
    MusicProviderResponseError,
    MusicProviderUnavailableError,
    MusicSearchQuery,
    MusicSearchResult,
)


class ITunesProvider:
    """
    Music metadata/search provider backed by Apple's
    public iTunes Search API.

    This provider handles communication with Apple and
    normalization into VibeNationHQ's provider format.

    It does not create or modify VibeNationHQ database records.
    """

    name = MusicProviderName.ITUNES

    SEARCH_URL = "https://itunes.apple.com/search"
    LOOKUP_URL = "https://itunes.apple.com/lookup"

    DEFAULT_TIMEOUT = 8

    ENTITY_MAP = {
        MusicEntityType.SONG: "song",
        MusicEntityType.ALBUM: "album",
        MusicEntityType.ARTIST: "musicArtist",
    }

    COUNTRY_MAP = {
        "nigeria": "NG",
        "ng": "NG",
        "united states": "US",
        "united states of america": "US",
        "us": "US",
        "united kingdom": "GB",
        "uk": "GB",
        "great britain": "GB",
        "ghana": "GH",
        "gh": "GH",
        "south africa": "ZA",
        "za": "ZA",
        "kenya": "KE",
        "ke": "KE",
        "canada": "CA",
        "ca": "CA",
        "australia": "AU",
        "au": "AU",
        "germany": "DE",
        "de": "DE",
        "france": "FR",
        "fr": "FR",
        "italy": "IT",
        "it": "IT",
        "spain": "ES",
        "es": "ES",
        "india": "IN",
        "in": "IN",
        "brazil": "BR",
        "br": "BR",
        "japan": "JP",
        "jp": "JP",
    }

    def search(
        self,
        query: MusicSearchQuery,
    ) -> list[MusicSearchResult]:
        """
        Search Apple's iTunes catalog and return normalized results.
        """

        cleaned_query = query.query.strip()

        if not cleaned_query:
            return []

        limit = max(
            1,
            min(query.limit, 50),
        )

        country = self._normalize_country(
            query.country,
        )

        params = {
            "term": cleaned_query,
            "media": "music",
            "country": country,
            "limit": limit,
        }

        if query.entity_type is not None:
            params["entity"] = self._get_entity(
                query.entity_type,
            )

        data = self._request(
            url=self.SEARCH_URL,
            params=params,
        )

        results = data.get("results")

        if not isinstance(results, list):
            raise MusicProviderResponseError(
                "Apple returned an invalid search response."
            )

        normalized_results: list[MusicSearchResult] = []

        for item in results:
            if not isinstance(item, dict):
                continue

            result = self._normalize_result(
                item,
                country=country,
            )

            if result is not None:
                normalized_results.append(result)

        return normalized_results

    def get(
        self,
        *,
        entity_type: MusicEntityType,
        provider_id: str,
        country: str = "NG",
    ) -> MusicSearchResult | None:
        """
        Retrieve a single Apple/iTunes catalog item by ID.
        """

        if not provider_id.strip():
            return None

        try:
            apple_id = int(provider_id)
        except ValueError as exc:
            raise MusicProviderResponseError(
                "Apple provider IDs must be numeric."
            ) from exc

        normalized_country = self._normalize_country(
            country,
        )

        params = {
            "id": apple_id,
            "country": normalized_country,
        }

        data = self._request(
            url=self.LOOKUP_URL,
            params=params,
        )

        results = data.get("results")

        if not isinstance(results, list):
            raise MusicProviderResponseError(
                "Apple returned an invalid lookup response."
            )

        expected_entity = entity_type

        for item in results:
            if not isinstance(item, dict):
                continue

            result = self._normalize_result(
                item,
                country=normalized_country,
            )

            if result is None:
                continue

            if result.entity_type == expected_entity:
                return result

        return None

    def _get_entity(
        self,
        entity_type: MusicEntityType,
    ) -> str:
        try:
            return self.ENTITY_MAP[entity_type]
        except KeyError as exc:
            raise MusicProviderError(
                f"Unsupported iTunes entity type: "
                f"{entity_type}"
            ) from exc

    def _request(
        self,
        *,
        url: str,
        params: dict[str, object],
    ) -> dict:
        """
        Perform a GET request against Apple's public API.
        """

        query_string = urlencode(params)
        request_url = f"{url}?{query_string}"

        request = Request(
            request_url,
            headers={
                "Accept": "application/json",
                "User-Agent": "VibeNationHQ/1.0",
            },
            method="GET",
        )

        try:
            with urlopen(
                request,
                timeout=self.DEFAULT_TIMEOUT,
            ) as response:
                raw_body = response.read()

        except HTTPError as exc:
            if exc.code == 429:
                raise MusicProviderUnavailableError(
                    "Apple iTunes Search API rate limit reached."
                ) from exc

            raise MusicProviderUnavailableError(
                "Apple iTunes Search API returned "
                f"HTTP {exc.code}."
            ) from exc

        except (
            URLError,
            TimeoutError,
        ) as exc:
            raise MusicProviderUnavailableError(
                "Apple iTunes Search API is currently unavailable."
            ) from exc

        try:
            data = json.loads(
                raw_body.decode("utf-8")
            )
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:
            raise MusicProviderResponseError(
                "Apple returned an invalid JSON response."
            ) from exc

        if not isinstance(data, dict):
            raise MusicProviderResponseError(
                "Apple returned an unexpected response format."
            )

        return data

    def _normalize_result(
        self,
        item: dict,
        *,
        country: str | None = None,
    ) -> MusicSearchResult | None:
        """
        Convert one Apple result into VibeNationHQ's
        normalized MusicSearchResult structure.

        Artist artwork is used only when Apple directly
        provides an artwork URL. No additional API request
        is made to retrieve representative artwork.

        If Apple does not provide artist artwork, the result
        returns without artwork and the frontend can display
        its fallback avatar.
        """

        entity_type = self._detect_entity_type(item)

        if entity_type is None:
            return None

        provider_id = self._get_provider_id(
            item=item,
            entity_type=entity_type,
        )

        if not provider_id:
            return None

        title = self._get_title(
            item=item,
            entity_type=entity_type,
        )

        if not title:
            return None

        normalized_country = self._normalize_country(
            country
            or item.get("country")
        )

        artwork_url = self._normalize_artwork_url(
            item.get("artworkUrl100")
            or item.get("artworkUrl60")
        )

        duration_seconds = self._get_duration_seconds(
            item.get("trackTimeMillis")
        )

        release_date = self._normalize_release_date(
            item.get("releaseDate")
        )

        apple_music_url = self._clean_string(
            item.get("trackViewUrl")
            or item.get("collectionViewUrl")
            or item.get("artistLinkUrl")
        )

        artist_name = self._clean_string(
            item.get("artistName")
        )

        album_name = self._clean_string(
            item.get("collectionName")
        )

        isrc = self._clean_string(
            item.get("isrc")
        )

        metadata = {
            "provider": self.name.value,
            "kind": item.get("kind"),
            "wrapper_type": item.get("wrapperType"),
            "artist_id": item.get("artistId"),
            "collection_id": item.get("collectionId"),
            "track_id": item.get("trackId"),
            "artist_view_url": item.get(
                "artistViewUrl"
            ),
            "collection_view_url": item.get(
                "collectionViewUrl"
            ),
            "track_view_url": item.get(
                "trackViewUrl"
            ),
            "primary_genre_name": self._clean_string(
                item.get("primaryGenreName")
            ),
            "track_number": item.get(
                "trackNumber"
            ),
            "track_count": item.get(
                "trackCount"
            ),
        }

        metadata = {
            key: value
            for key, value in metadata.items()
            if value is not None
        }

        return MusicSearchResult(
            provider=self.name,
            provider_id=str(provider_id),
            entity_type=entity_type,
            title=title,
            artist_name=artist_name,
            album_name=album_name,
            artwork_url=artwork_url,
            release_date=release_date,
            duration_seconds=duration_seconds,
            preview_url=self._clean_string(
                item.get("previewUrl")
            ),
            spotify_url=None,
            apple_music_url=apple_music_url,
            youtube_url=None,
            audiomack_url=None,
            boomplay_url=None,
            country=normalized_country,
            isrc=isrc,
            metadata=metadata,
        )

    def _detect_entity_type(
        self,
        item: dict,
    ) -> MusicEntityType | None:
        wrapper_type = item.get("wrapperType")
        kind = item.get("kind")

        if wrapper_type == "track":
            return MusicEntityType.SONG

        if wrapper_type == "collection":
            return MusicEntityType.ALBUM

        if wrapper_type == "artist":
            return MusicEntityType.ARTIST

        if kind in {
            "song",
            "feature-movie",
            "podcast",
            "music-video",
        }:
            return MusicEntityType.SONG

        return None

    def _get_provider_id(
        self,
        *,
        item: dict,
        entity_type: MusicEntityType,
    ) -> str | None:
        if entity_type == MusicEntityType.SONG:
            value = item.get("trackId")

        elif entity_type == MusicEntityType.ALBUM:
            value = item.get("collectionId")

        elif entity_type == MusicEntityType.ARTIST:
            value = item.get("artistId")

        else:
            value = None

        if value is None:
            return None

        return str(value)

    def _get_title(
        self,
        *,
        item: dict,
        entity_type: MusicEntityType,
    ) -> str | None:
        if entity_type == MusicEntityType.SONG:
            return self._clean_string(
                item.get("trackName")
            )

        if entity_type == MusicEntityType.ALBUM:
            return self._clean_string(
                item.get("collectionName")
            )

        if entity_type == MusicEntityType.ARTIST:
            return self._clean_string(
                item.get("artistName")
            )

        return None

    def _normalize_artwork_url(
        self,
        artwork_url: object,
    ) -> str | None:
        value = self._clean_string(artwork_url)

        if not value:
            return None

        if "100x100" in value:
            value = value.replace(
                "100x100",
                "600x600",
            )

        elif "60x60" in value:
            value = value.replace(
                "60x60",
                "600x600",
            )

        return value

    def _get_duration_seconds(
        self,
        milliseconds: object,
    ) -> int | None:
        if not isinstance(
            milliseconds,
            (int, float),
        ):
            return None

        if milliseconds <= 0:
            return None

        return round(
            milliseconds / 1000
        )

    def _normalize_release_date(
        self,
        value: object,
    ) -> str | None:
        cleaned = self._clean_string(value)

        if not cleaned:
            return None

        return cleaned[:10]

    def _normalize_country(
        self,
        value: object,
    ) -> str:
        """
        Normalize Apple's country value to an ISO-style
        two-letter country code.

        Apple may return either a country name or a code.
        The provider contract always receives a two-letter code.
        """

        cleaned = self._clean_string(value)

        if not cleaned:
            return "NG"

        normalized = cleaned.casefold()

        mapped = self.COUNTRY_MAP.get(
            normalized
        )

        if mapped:
            return mapped

        # Already looks like a two-letter country code.
        if len(cleaned) == 2 and cleaned.isalpha():
            return cleaned.upper()

        # Unknown country names should not leak into the
        # normalized provider contract.
        return "NG"

    def _clean_string(
        self,
        value: object,
    ) -> str | None:
        if not isinstance(value, str):
            return None

        value = value.strip()

        return value or None