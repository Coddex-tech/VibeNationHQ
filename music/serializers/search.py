from rest_framework import serializers

from music.serializers.catalog import (
    AlbumCardSerializer,
    ArtistCardSerializer,
    GenreSerializer,
    SongCardSerializer,
)


class MusicSearchSerializer(serializers.Serializer):
    """
    Combined VibeNation music search response.
    """

    query = serializers.CharField(
        read_only=True,
    )

    songs = SongCardSerializer(
        many=True,
        read_only=True,
    )

    artists = ArtistCardSerializer(
        many=True,
        read_only=True,
    )

    albums = AlbumCardSerializer(
        many=True,
        read_only=True,
    )

    genres = GenreSerializer(
        many=True,
        read_only=True,
    )