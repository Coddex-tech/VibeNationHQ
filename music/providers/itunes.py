from __future__ import annotations

import json
import re
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
    Music metadata/search provider backed by Apple's public iTunes API.

    This provider fetches and normalizes external music metadata.
    It never creates or modifies VibeNationHQ database records.
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
        """Search Apple's catalog and return normalized results."""

        cleaned_query = query.query.strip()

        if not cleaned_query:
            return []

        limit = max(1, min(query.limit, 50))
        country = self._normalize_country(query.country)

        params: dict[str, object] = {
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
        """Retrieve a single Apple catalog item by ID."""

        cleaned_provider_id = provider_id.strip()

        if not cleaned_provider_id:
            return None

        apple_id = self._parse_positive_id(
            cleaned_provider_id,
            description="Apple provider IDs",
        )

        normalized_country = self._normalize_country(country)

        data = self._request(
            url=self.LOOKUP_URL,
            params={
                "id": apple_id,
                "country": normalized_country,
            },
        )

        results = data.get("results")

        if not isinstance(results, list):
            raise MusicProviderResponseError(
                "Apple returned an invalid lookup response."
            )

        for item in results:
            if not isinstance(item, dict):
                continue

            result = self._normalize_result(
                item,
                country=normalized_country,
            )

            if (
                result is not None
                and result.entity_type == entity_type
            ):
                return result

        return None

    def get_album_tracks(
        self,
        *,
        album_provider_id: str,
        country: str = "NG",
    ) -> list[MusicSearchResult]:
        """
        Retrieve and validate tracks belonging to an Apple album.

        Tracks are ordered by disc number and track number. Invalid
        or incomplete tracklists raise MusicProviderResponseError
        so callers can preserve an existing tracklist.
        """

        cleaned_provider_id = album_provider_id.strip()

        if not cleaned_provider_id:
            raise MusicProviderResponseError(
                "Apple album provider ID cannot be empty."
            )

        apple_album_id = self._parse_positive_id(
            cleaned_provider_id,
            description="Apple album provider IDs",
        )

        normalized_country = self._normalize_country(country)

        data = self._request(
            url=self.LOOKUP_URL,
            params={
                "id": apple_album_id,
                "entity": "song",
                "country": normalized_country,
            },
        )

        results = data.get("results")

        if not isinstance(results, list):
            raise MusicProviderResponseError(
                "Apple returned an invalid album tracklist response."
            )

        album_found = False
        expected_track_count: int | None = None
        tracks: list[MusicSearchResult] = []

        for item in results:
            if not isinstance(item, dict):
                continue

            result = self._normalize_result(
                item,
                country=normalized_country,
            )

            if result is None:
                continue

            if result.entity_type == MusicEntityType.ALBUM:
                collection_id = result.metadata.get("collection_id")

                if str(collection_id) != str(apple_album_id):
                    continue

                album_found = True

                raw_track_count = result.metadata.get("track_count")

                if raw_track_count is not None:
                    if (
                        not isinstance(raw_track_count, int)
                        or isinstance(raw_track_count, bool)
                        or raw_track_count < 1
                    ):
                        raise MusicProviderResponseError(
                            "Apple returned an invalid album track count."
                        )

                    expected_track_count = raw_track_count

                continue

            if result.entity_type != MusicEntityType.SONG:
                continue

            # Accept only songs explicitly associated with this album.
            collection_id = result.metadata.get("collection_id")

            if str(collection_id) != str(apple_album_id):
                continue

            track_number = result.metadata.get("track_number")
            disc_number = result.metadata.get("disc_number", 1)

            if (
                not isinstance(track_number, int)
                or isinstance(track_number, bool)
                or track_number < 1
            ):
                raise MusicProviderResponseError(
                    "Apple returned a track without a valid track number."
                )

            if (
                not isinstance(disc_number, int)
                or isinstance(disc_number, bool)
                or disc_number < 1
            ):
                raise MusicProviderResponseError(
                    "Apple returned a track with an invalid disc number."
                )

            tracks.append(result)

        if not album_found:
            raise MusicProviderResponseError(
                "Apple did not return the requested album "
                "in its tracklist response."
            )

        if not tracks:
            raise MusicProviderResponseError(
                "Apple returned no tracks for the requested album."
            )

        provider_track_ids = [
            track.provider_id
            for track in tracks
        ]

        if len(provider_track_ids) != len(set(provider_track_ids)):
            raise MusicProviderResponseError(
                "Apple returned duplicate track IDs for the album."
            )

        disc_track_pairs = [
            (
                track.metadata.get("disc_number", 1),
                track.metadata["track_number"],
            )
            for track in tracks
        ]

        if len(disc_track_pairs) != len(set(disc_track_pairs)):
            raise MusicProviderResponseError(
                "Apple returned duplicate track positions for the album."
            )

        if (
            expected_track_count is not None
            and len(tracks) != expected_track_count
        ):
            raise MusicProviderResponseError(
                "Apple returned an incomplete album tracklist: "
                f"expected {expected_track_count} tracks but received "
                f"{len(tracks)}."
            )

        tracks.sort(
            key=lambda track: (
                track.metadata.get("disc_number", 1),
                track.metadata["track_number"],
                track.provider_id,
            )
        )

        return tracks

    @staticmethod
    def _parse_positive_id(
        value: str,
        *,
        description: str,
    ) -> int:
        try:
            parsed_id = int(value)
        except ValueError as exc:
            raise MusicProviderResponseError(
                f"{description} must be numeric."
            ) from exc

        if parsed_id <= 0:
            raise MusicProviderResponseError(
                f"{description} must be positive integers."
            )

        return parsed_id

    def _get_entity(
        self,
        entity_type: MusicEntityType,
    ) -> str:
        try:
            return self.ENTITY_MAP[entity_type]
        except KeyError as exc:
            raise MusicProviderError(
                f"Unsupported iTunes entity type: {entity_type}"
            ) from exc

    def _request(
        self,
        *,
        url: str,
        params: dict[str, object],
    ) -> dict:
        """Perform a GET request against Apple's public API."""

        request_url = f"{url}?{urlencode(params)}"

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

        except (URLError, TimeoutError, OSError) as exc:
            raise MusicProviderUnavailableError(
                "Apple iTunes Search API is currently unavailable."
            ) from exc

        try:
            data = json.loads(raw_body.decode("utf-8"))
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
        Normalize one Apple result into VibeNationHQ's provider format.

        Only supported music songs, albums, and artists are accepted.
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
            country or item.get("country")
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

        isrc = self._clean_string(item.get("isrc"))

        metadata = {
            "provider": self.name.value,
            "kind": item.get("kind"),
            "wrapper_type": item.get("wrapperType"),
            "artist_id": item.get("artistId"),
            "collection_id": item.get("collectionId"),
            "track_id": item.get("trackId"),
            "artist_view_url": item.get("artistViewUrl"),
            "collection_view_url": item.get("collectionViewUrl"),
            "track_view_url": item.get("trackViewUrl"),
            "primary_genre_name": self._clean_string(
                item.get("primaryGenreName")
            ),
            "track_number": item.get("trackNumber"),
            "track_count": item.get("trackCount"),
            "disc_number": item.get("discNumber"),
            "disc_count": item.get("discCount"),
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
        """
        Identify supported entities using Apple's wrapper and kind.

        Artist and collection entities are handled separately from
        track entities so non-song tracks such as music videos,
        podcasts, and films cannot be misclassified as songs.
        """

        wrapper_type = item.get("wrapperType")
        kind = item.get("kind")

        if wrapper_type == "artist":
            return MusicEntityType.ARTIST

        if wrapper_type == "collection":
            collection_type = item.get("collectionType")

            if collection_type in (None, "Album"):
                return MusicEntityType.ALBUM

            return None

        if wrapper_type == "track" and kind == "song":
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

        if value is None or isinstance(value, bool):
            return None

        cleaned = str(value).strip()

        return cleaned or None

    def _get_title(
        self,
        *,
        item: dict,
        entity_type: MusicEntityType,
    ) -> str | None:
        if entity_type == MusicEntityType.SONG:
            return self._clean_string(item.get("trackName"))

        if entity_type == MusicEntityType.ALBUM:
            return self._clean_string(item.get("collectionName"))

        if entity_type == MusicEntityType.ARTIST:
            return self._clean_string(item.get("artistName"))

        return None

    def _normalize_artwork_url(
        self,
        artwork_url: object,
    ) -> str | None:
        """
        Prefer a larger Apple artwork variant for standard artwork paths.

        Other URL formats remain unchanged.
        """

        value = self._clean_string(artwork_url)

        if not value:
            return None

        return re.sub(
            r"/(?:100|60)x(?:100|60)(?=/|$)",
            "/600x600",
            value,
            count=1,
        )

    @staticmethod
    def _get_duration_seconds(
        milliseconds: object,
    ) -> int | None:
        if (
            not isinstance(milliseconds, (int, float))
            or isinstance(milliseconds, bool)
            or milliseconds <= 0
        ):
            return None

        return round(milliseconds / 1000)

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
        Normalize a country name or code to a two-letter code.

        Unknown values fall back to Nigeria (NG).
        """

        cleaned = self._clean_string(value)

        if not cleaned:
            return "NG"

        normalized = cleaned.casefold()
        mapped = self.COUNTRY_MAP.get(normalized)

        if mapped:
            return mapped

        if len(cleaned) == 2 and cleaned.isalpha():
            return cleaned.upper()

        return "NG"

    @staticmethod
    def _clean_string(
        value: object,
    ) -> str | None:
        if not isinstance(value, str):
            return None

        cleaned = value.strip()

        return cleaned or None