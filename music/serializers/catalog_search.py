from __future__ import annotations

from rest_framework import serializers

from music.models import Album, Artist, Song
from music.services.catalog_search import (
    CatalogSearchResult,
)


class MusicCatalogSearchResultSerializer(
    serializers.Serializer,
):
    """
    Serializes a canonical VibeNationHQ music catalog
    search result into a consistent response shape.
    """

    entity_type = serializers.CharField()
    id = serializers.IntegerField()
    title = serializers.CharField()
    slug = serializers.CharField()

    artist = serializers.SerializerMethodField()
    artists = serializers.SerializerMethodField()
    album = serializers.SerializerMethodField()

    artwork = serializers.SerializerMethodField()

    def to_representation(
        self,
        result: CatalogSearchResult,
    ):
        obj = result.object

        if isinstance(obj, Artist):
            title = obj.name
        else:
            title = obj.title

        return {
            "entity_type": result.entity_type,
            "id": obj.id,
            "title": title,
            "slug": obj.slug,
            "artist": self.get_artist(result),
            "artists": self.get_artists(result),
            "album": self.get_album(result),
            "artwork": self.get_artwork(result),
        }

    def get_artist(
        self,
        result: CatalogSearchResult,
    ):
        obj = result.object

        if isinstance(obj, Song):
            artist = obj.artists.first()

            if artist is None:
                return None

            return {
                "id": artist.id,
                "name": artist.name,
                "slug": artist.slug,
            }

        if isinstance(obj, Album):
            artist = obj.artists.first()

            if artist is None:
                return None

            return {
                "id": artist.id,
                "name": artist.name,
                "slug": artist.slug,
            }

        return None

    def get_artists(
        self,
        result: CatalogSearchResult,
    ):
        obj = result.object

        if isinstance(obj, Artist):
            return [
                {
                    "id": obj.id,
                    "name": obj.name,
                    "slug": obj.slug,
                }
            ]

        if isinstance(obj, Song):
            artists = list(
                obj.artists.all()
            )

            return [
                {
                    "id": artist.id,
                    "name": artist.name,
                    "slug": artist.slug,
                }
                for artist in artists
            ]

        if isinstance(obj, Album):
            artists = list(
                obj.artists.all()
            )

            return [
                {
                    "id": artist.id,
                    "name": artist.name,
                    "slug": artist.slug,
                }
                for artist in artists
            ]

        return []

    def get_album(
        self,
        result: CatalogSearchResult,
    ):
        obj = result.object

        if not isinstance(obj, Song):
            return None

        album = obj.album

        if album is None:
            return None

        return {
            "id": album.id,
            "title": album.title,
            "slug": album.slug,
        }

    def get_artwork(
        self,
        result: CatalogSearchResult,
    ):
        obj = result.object

        if isinstance(obj, Song):
            return (
                obj.artwork.url
                if obj.artwork
                else None
            )

        if isinstance(obj, Album):
            return (
                obj.artwork.url
                if obj.artwork
                else None
            )

        if isinstance(obj, Artist):
            return (
                obj.profile_image.url
                if obj.profile_image
                else None
            )

        return None


class MusicCatalogSearchResponseSerializer(
    serializers.Serializer,
):
    """
    Wraps catalog search results in the API response shape.
    """

    results = MusicCatalogSearchResultSerializer(
        many=True,
        read_only=True,
    )