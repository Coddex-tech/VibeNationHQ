from rest_framework import serializers

from music.providers.base import MusicSearchResult


class MusicProviderSearchResultSerializer(
    serializers.Serializer
):
    provider = serializers.CharField()
    provider_id = serializers.CharField()
    entity_type = serializers.CharField()
    title = serializers.CharField()

    artist_name = serializers.CharField(
        allow_null=True,
        required=False,
    )

    album_name = serializers.CharField(
        allow_null=True,
        required=False,
    )

    artwork_url = serializers.URLField(
        allow_null=True,
        required=False,
    )

    release_date = serializers.CharField(
        allow_null=True,
        required=False,
    )

    duration_seconds = serializers.IntegerField(
        allow_null=True,
        required=False,
    )

    preview_url = serializers.URLField(
        allow_null=True,
        required=False,
    )

    spotify_url = serializers.URLField(
        allow_null=True,
        required=False,
    )

    apple_music_url = serializers.URLField(
        allow_null=True,
        required=False,
    )

    youtube_url = serializers.URLField(
        allow_null=True,
        required=False,
    )

    audiomack_url = serializers.URLField(
        allow_null=True,
        required=False,
    )

    boomplay_url = serializers.URLField(
        allow_null=True,
        required=False,
    )

    country = serializers.CharField(
        allow_null=True,
        required=False,
    )

    isrc = serializers.CharField(
        allow_null=True,
        required=False,
    )

    metadata = serializers.JSONField(
        required=False,
    )

    def to_representation(
        self,
        instance: MusicSearchResult,
    ):
        return {
            "provider": instance.provider.value,
            "provider_id": instance.provider_id,
            "entity_type": instance.entity_type.value,
            "title": instance.title,
            "artist_name": instance.artist_name,
            "album_name": instance.album_name,
            "artwork_url": instance.artwork_url,
            "release_date": instance.release_date,
            "duration_seconds": instance.duration_seconds,
            "preview_url": instance.preview_url,
            "spotify_url": instance.spotify_url,
            "apple_music_url": instance.apple_music_url,
            "youtube_url": instance.youtube_url,
            "audiomack_url": instance.audiomack_url,
            "boomplay_url": instance.boomplay_url,
            "country": instance.country,
            "isrc": instance.isrc,
            "metadata": instance.metadata,
        }