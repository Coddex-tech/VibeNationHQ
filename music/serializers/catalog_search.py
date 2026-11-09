
from __future__ import annotations

from rest_framework import serializers

from music.models import Album, Artist, MusicProviderIdentity, Song
from music.services.catalog_search import CatalogSearchResult


class MusicCatalogSearchResultSerializer(serializers.Serializer):
    """
    Serializes canonical catalog results, including available
    provider artwork, previews, and official listening links.
    """

    entity_type = serializers.CharField()
    id = serializers.IntegerField()
    title = serializers.CharField()
    slug = serializers.CharField()

    artist = serializers.SerializerMethodField()
    artists = serializers.SerializerMethodField()
    album = serializers.SerializerMethodField()
    artwork = serializers.SerializerMethodField()

    preview_url = serializers.SerializerMethodField()
    apple_music_url = serializers.SerializerMethodField()
    spotify_url = serializers.SerializerMethodField()
    youtube_url = serializers.SerializerMethodField()
    audiomack_url = serializers.SerializerMethodField()
    boomplay_url = serializers.SerializerMethodField()

    def to_representation(self, result: CatalogSearchResult):
        obj = result.object

        title = obj.name if isinstance(obj, Artist) else obj.title

        return {
            "entity_type": result.entity_type,
            "id": obj.id,
            "title": title,
            "slug": obj.slug,
            "artist": self.get_artist(result),
            "artists": self.get_artists(result),
            "album": self.get_album(result),
            "artwork": self.get_artwork(result),
            "preview_url": self.get_preview_url(result),
            "apple_music_url": self.get_apple_music_url(result),
            "spotify_url": self.get_spotify_url(result),
            "youtube_url": self.get_youtube_url(result),
            "audiomack_url": self.get_audiomack_url(result),
            "boomplay_url": self.get_boomplay_url(result),
        }

    @staticmethod
    def _get_provider_identities(obj):
        """
        Return linked provider identities, preferring iTunes when
        multiple providers have metadata for the same entity.
        """
        identities = list(obj.provider_identities.all())

        provider_priority = {
            MusicProviderIdentity.Provider.ITUNES: 0,
            MusicProviderIdentity.Provider.SPOTIFY: 1,
            MusicProviderIdentity.Provider.MUSICBRAINZ: 2,
        }

        identities.sort(
            key=lambda identity: (
                provider_priority.get(identity.provider, 3),
                identity.pk,
            )
        )

        return identities

    @classmethod
    def _provider_value(cls, obj, field_name):
        for identity in cls._get_provider_identities(obj):
            value = getattr(identity, field_name, "")
            if value:
                return value

        return None

    @staticmethod
    def _model_value(obj, field_name):
        value = getattr(obj, field_name, "")
        return value or None

    def get_artist(self, result: CatalogSearchResult):
        obj = result.object

        if isinstance(obj, (Song, Album)):
            artist = obj.artists.first()

            if artist is None:
                return None

            return {
                "id": artist.id,
                "name": artist.name,
                "slug": artist.slug,
            }

        return None

    def get_artists(self, result: CatalogSearchResult):
        obj = result.object

        if isinstance(obj, Artist):
            artists = [obj]
        elif isinstance(obj, (Song, Album)):
            artists = list(obj.artists.all())
        else:
            artists = []

        return [
            {
                "id": artist.id,
                "name": artist.name,
                "slug": artist.slug,
            }
            for artist in artists
        ]

    def get_album(self, result: CatalogSearchResult):
        obj = result.object

        if not isinstance(obj, Song) or obj.album is None:
            return None

        return {
            "id": obj.album.id,
            "title": obj.album.title,
            "slug": obj.album.slug,
        }

    def get_artwork(self, result: CatalogSearchResult):
        obj = result.object

        if isinstance(obj, Artist):
            if obj.profile_image:
                return obj.profile_image.url

        elif isinstance(obj, (Song, Album)):
            if obj.artwork:
                return obj.artwork.url

        return self._provider_value(obj, "artwork_url")

    def get_preview_url(self, result: CatalogSearchResult):
        obj = result.object

        # Short previews are currently relevant to songs only.
        if not isinstance(obj, Song):
            return None

        return self._provider_value(obj, "preview_url")

    def get_apple_music_url(self, result: CatalogSearchResult):
        obj = result.object

        return (
            self._model_value(obj, "apple_music_url")
            or self._provider_value(obj, "apple_music_url")
        )

    def get_spotify_url(self, result: CatalogSearchResult):
        obj = result.object

        return (
            self._model_value(obj, "spotify_url")
            or self._provider_value(obj, "spotify_url")
        )

    def get_youtube_url(self, result: CatalogSearchResult):
        obj = result.object

        return (
            self._model_value(obj, "youtube_url")
            or self._provider_value(obj, "youtube_url")
        )

    def get_audiomack_url(self, result: CatalogSearchResult):
        obj = result.object

        return (
            self._model_value(obj, "audiomack_url")
            or self._provider_value(obj, "audiomack_url")
        )

    def get_boomplay_url(self, result: CatalogSearchResult):
        obj = result.object

        return (
            self._model_value(obj, "boomplay_url")
            or self._provider_value(obj, "boomplay_url")
        )


class MusicCatalogSearchResponseSerializer(serializers.Serializer):
    """Wraps catalog search results in the API response shape."""

    results = MusicCatalogSearchResultSerializer(
        many=True,
        read_only=True,
    )
