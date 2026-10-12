from rest_framework import serializers

from music.serializers.catalog import (
    AlbumCardSerializer,
    ArtistCardSerializer,
    SongCardSerializer,
)


class DiscoverySongSerializer(SongCardSerializer):
    """
    Song serializer used by discovery endpoints.

    Extends SongCardSerializer and adds the annotated
    average rating used by top-rated discovery results.
    """

    average_rating = serializers.FloatField(
        read_only=True,
        allow_null=True,
    )

    class Meta(SongCardSerializer.Meta):
        fields = SongCardSerializer.Meta.fields + [
            "average_rating",
        ]


class DiscoveryAlbumSerializer(AlbumCardSerializer):
    """
    Album serializer used by discovery endpoints.

    Extends AlbumCardSerializer and adds the annotated
    average rating used by top-rated discovery results.
    """

    average_rating = serializers.FloatField(
        read_only=True,
        allow_null=True,
    )

    class Meta(AlbumCardSerializer.Meta):
        fields = AlbumCardSerializer.Meta.fields + [
            "average_rating",
        ]


class DiscoveryArtistSerializer(ArtistCardSerializer):
    """
    Artist serializer used by discovery endpoints.
    """

    pass


class DiscoveryResponseSerializer(serializers.Serializer):
    """
    Serializer for the combined music discovery response.
    """

    trending_songs = DiscoverySongSerializer(
        many=True,
        read_only=True,
    )

    trending_albums = DiscoveryAlbumSerializer(
        many=True,
        read_only=True,
    )

    trending_artists = DiscoveryArtistSerializer(
        many=True,
        read_only=True,
    )

    most_discussed_songs = DiscoverySongSerializer(
        many=True,
        read_only=True,
    )

    most_discussed_albums = DiscoveryAlbumSerializer(
        many=True,
        read_only=True,
    )

    most_favorited_songs = DiscoverySongSerializer(
        many=True,
        read_only=True,
    )

    most_favorited_albums = DiscoveryAlbumSerializer(
        many=True,
        read_only=True,
    )

    top_rated_songs = DiscoverySongSerializer(
        many=True,
        read_only=True,
    )

    top_rated_albums = DiscoveryAlbumSerializer(
        many=True,
        read_only=True,
    )

    featured_songs = DiscoverySongSerializer(
        many=True,
        read_only=True,
    )

    featured_albums = DiscoveryAlbumSerializer(
        many=True,
        read_only=True,
    )

    featured_artists = DiscoveryArtistSerializer(
        many=True,
        read_only=True,
    )

    recently_released_songs = DiscoverySongSerializer(
        many=True,
        read_only=True,
    )

    recently_released_albums = DiscoveryAlbumSerializer(
        many=True,
        read_only=True,
    )