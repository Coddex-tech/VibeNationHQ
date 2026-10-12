from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol


class MusicEntityType(StrEnum):
    SONG = "song"
    ALBUM = "album"
    ARTIST = "artist"


class MusicProviderName(StrEnum):
    """
    Identifies external music metadata providers.

    Only providers that are actually implemented and registered
    should be used by the active provider registry.

    Additional providers can be added here later without
    changing the provider abstraction itself.
    """

    ITUNES = "itunes"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class MusicSearchQuery:
    """
    Normalized search request sent to music providers.

    The provider layer decides how this query is translated
    into the provider's own search syntax.
    """

    query: str
    entity_type: MusicEntityType | None = None
    country: str = "NG"
    limit: int = 10


@dataclass(frozen=True, slots=True)
class MusicSearchResult:
    """
    Normalized music result returned by any provider.

    VibeNationHQ works with this structure instead of depending
    directly on the implementation details of a specific provider.
    """

    provider: MusicProviderName
    provider_id: str

    entity_type: MusicEntityType

    title: str
    artist_name: str | None = None
    album_name: str | None = None

    artwork_url: str | None = None

    release_date: str | None = None
    duration_seconds: int | None = None

    preview_url: str | None = None

    spotify_url: str | None = None
    apple_music_url: str | None = None
    youtube_url: str | None = None
    audiomack_url: str | None = None
    boomplay_url: str | None = None

    country: str | None = None

    isrc: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    @property
    def external_id(self) -> str:
        """
        Alias used when mapping a normalized result to
        CommunityPostTarget.external_id.
        """
        return self.provider_id


class MusicProvider(Protocol):
    """
    Contract implemented by every external music provider.

    Providers are responsible only for communicating with
    their external service and converting its response into
    MusicSearchResult objects.

    They do not create or modify VibeNationHQ database records.
    """

    name: MusicProviderName

    def search(
        self,
        query: MusicSearchQuery,
    ) -> list[MusicSearchResult]:
        """
        Search the provider and return normalized results.
        """
        ...

    def get(
        self,
        *,
        entity_type: MusicEntityType,
        provider_id: str,
        country: str = "NG",
    ) -> MusicSearchResult | None:
        """
        Retrieve one known provider entity by its external ID.
        """
        ...


class MusicProviderError(Exception):
    """
    Base exception for provider-related failures.
    """


class MusicProviderUnavailableError(MusicProviderError):
    """
    Provider could not be reached or is temporarily unavailable.
    """


class MusicProviderRateLimitError(MusicProviderError):
    """
    Provider rejected the request because its rate limit was reached.
    """


class MusicProviderResponseError(MusicProviderError):
    """
    Provider returned an unexpected or unusable response.
    """