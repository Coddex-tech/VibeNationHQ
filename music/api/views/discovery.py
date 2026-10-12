from rest_framework.response import Response
from rest_framework.views import APIView

from music.serializers.discovery import (
    DiscoveryResponseSerializer,
    DiscoverySongSerializer,
    DiscoveryAlbumSerializer,
    DiscoveryArtistSerializer,
)

from music.services.discovery import DiscoveryService


class TrendingSongsAPIView(APIView):
    """
    Return the currently trending published songs.
    """

    def get(self, request):
        songs = DiscoveryService.trending_songs()

        serializer = DiscoverySongSerializer(
            songs,
            many=True,
        )

        return Response(serializer.data)


class TrendingAlbumsAPIView(APIView):
    """
    Return the currently trending published albums.
    """

    def get(self, request):
        albums = DiscoveryService.trending_albums()

        serializer = DiscoveryAlbumSerializer(
            albums,
            many=True,
        )

        return Response(serializer.data)


class TrendingArtistsAPIView(APIView):
    """
    Return currently trending active artists.
    """

    def get(self, request):
        artists = DiscoveryService.trending_artists()

        serializer = DiscoveryArtistSerializer(
            artists,
            many=True,
        )

        return Response(serializer.data)


class MostDiscussedSongsAPIView(APIView):
    """
    Return songs with the most published community discussions.
    """

    def get(self, request):
        songs = DiscoveryService.most_discussed_songs()

        serializer = DiscoverySongSerializer(
            songs,
            many=True,
        )

        return Response(serializer.data)


class MostDiscussedAlbumsAPIView(APIView):
    """
    Return albums with the most published community discussions.
    """

    def get(self, request):
        albums = DiscoveryService.most_discussed_albums()

        serializer = DiscoveryAlbumSerializer(
            albums,
            many=True,
        )

        return Response(serializer.data)


class MostFavoritedSongsAPIView(APIView):
    """
    Return the most-favorited published songs.
    """

    def get(self, request):
        songs = DiscoveryService.most_favorited_songs()

        serializer = DiscoverySongSerializer(
            songs,
            many=True,
        )

        return Response(serializer.data)


class MostFavoritedAlbumsAPIView(APIView):
    """
    Return the most-favorited published albums.
    """

    def get(self, request):
        albums = DiscoveryService.most_favorited_albums()

        serializer = DiscoveryAlbumSerializer(
            albums,
            many=True,
        )

        return Response(serializer.data)


class TopRatedSongsAPIView(APIView):
    """
    Return the highest-rated published songs.
    """

    def get(self, request):
        songs = DiscoveryService.top_rated_songs()

        serializer = DiscoverySongSerializer(
            songs,
            many=True,
        )

        return Response(serializer.data)


class TopRatedAlbumsAPIView(APIView):
    """
    Return the highest-rated published albums.
    """

    def get(self, request):
        albums = DiscoveryService.top_rated_albums()

        serializer = DiscoveryAlbumSerializer(
            albums,
            many=True,
        )

        return Response(serializer.data)


class FeaturedSongsAPIView(APIView):
    """
    Return featured published songs.
    """

    def get(self, request):
        songs = DiscoveryService.featured_songs()

        serializer = DiscoverySongSerializer(
            songs,
            many=True,
        )

        return Response(serializer.data)


class FeaturedAlbumsAPIView(APIView):
    """
    Return featured published albums.
    """

    def get(self, request):
        albums = DiscoveryService.featured_albums()

        serializer = DiscoveryAlbumSerializer(
            albums,
            many=True,
        )

        return Response(serializer.data)


class FeaturedArtistsAPIView(APIView):
    """
    Return featured artists.
    """

    def get(self, request):
        artists = DiscoveryService.featured_artists()

        serializer = DiscoveryArtistSerializer(
            artists,
            many=True,
        )

        return Response(serializer.data)


class RecentlyReleasedSongsAPIView(APIView):
    """
    Return the most recently released published songs.
    """

    def get(self, request):
        songs = DiscoveryService.recently_released_songs()

        serializer = DiscoverySongSerializer(
            songs,
            many=True,
        )

        return Response(serializer.data)


class RecentlyReleasedAlbumsAPIView(APIView):
    """
    Return the most recently released published albums.
    """

    def get(self, request):
        albums = DiscoveryService.recently_released_albums()

        serializer = DiscoveryAlbumSerializer(
            albums,
            many=True,
        )

        return Response(serializer.data)


class MusicDiscoveryAPIView(APIView):
    """
    Return the complete music discovery payload.

    This endpoint is intended for discovery/homepage-style
    screens where multiple discovery sections are needed
    in a single API request.
    """

    def get(self, request):
        data = {
            "trending_songs": DiscoveryService.trending_songs(),
            "trending_albums": DiscoveryService.trending_albums(),
            "trending_artists": DiscoveryService.trending_artists(),

            "most_discussed_songs": (
                DiscoveryService.most_discussed_songs()
            ),
            "most_discussed_albums": (
                DiscoveryService.most_discussed_albums()
            ),

            "most_favorited_songs": (
                DiscoveryService.most_favorited_songs()
            ),
            "most_favorited_albums": (
                DiscoveryService.most_favorited_albums()
            ),

            "top_rated_songs": (
                DiscoveryService.top_rated_songs()
            ),
            "top_rated_albums": (
                DiscoveryService.top_rated_albums()
            ),

            "featured_songs": (
                DiscoveryService.featured_songs()
            ),
            "featured_albums": (
                DiscoveryService.featured_albums()
            ),
            "featured_artists": (
                DiscoveryService.featured_artists()
            ),

            "recently_released_songs": (
                DiscoveryService.recently_released_songs()
            ),
            "recently_released_albums": (
                DiscoveryService.recently_released_albums()
            ),
        }

        serializer = DiscoveryResponseSerializer(data)

        return Response(serializer.data)