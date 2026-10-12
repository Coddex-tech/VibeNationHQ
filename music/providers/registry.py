from __future__ import annotations

from .base import MusicProvider, MusicProviderName
from .itunes import ITunesProvider


class MusicProviderRegistry:
    """
    Central registry for all music metadata providers
    available to VibeNationHQ.

    Only providers explicitly registered here are active.

    Additional providers can be added later without changing
    the rest of the provider architecture.
    """

    def __init__(
        self,
        providers: list[MusicProvider] | None = None,
    ):
        self._providers = {
            provider.name: provider
            for provider in (
                providers
                if providers is not None
                else [
                    ITunesProvider(),
                ]
            )
        }

    def get(
        self,
        name: MusicProviderName,
    ) -> MusicProvider:
        try:
            return self._providers[name]
        except KeyError as exc:
            raise ValueError(
                f"Music provider '{name}' is not registered."
            ) from exc

    def all(self) -> list[MusicProvider]:
        return list(self._providers.values())

    def names(self) -> list[MusicProviderName]:
        return list(self._providers.keys())