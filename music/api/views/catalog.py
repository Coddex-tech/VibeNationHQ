
from rest_framework import generics
from rest_framework.response import Response

from music.api.pagination import MusicPagination
from music.models import Album, Artist, Genre, Song
from music.serializers.catalog import (
    AlbumCardSerializer,
    AlbumSerializer,
    ArtistCardSerializer,
    ArtistSerializer,
    GenreSerializer,
    SongCardSerializer,
    SongSerializer,
)
from music.services.feed_interactions import (
    MusicFeedInteractionService,
)


# ============================================================
# SONGS
# ============================================================

class SongListAPIView(generics.ListAPIView):
    """
    List published songs using the lightweight song-card serializer.
    """

    queryset = (
        Song.objects
        .filter(
            status=Song.Status.PUBLISHED,
        )
        .select_related(
            "album",
        )
        .prefetch_related(
            "artists",
            "featured_artists",
            "genres",
        )
        .order_by("-published_at", "-pk")
    )

    serializer_class = SongCardSerializer
    pagination_class = MusicPagination


class SongDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve a published song with its artists, album, genres,
    provider preview identities, community ratings, and related posts.

    Authenticated song-detail visits are recorded as feed interactions.
    Anonymous visitors can still access published song details.
    """

    queryset = (
        Song.objects
        .filter(
            status=Song.Status.PUBLISHED,
        )
        .select_related(
            "album",
        )
        .prefetch_related(
            "artists",
            "featured_artists",
            "genres",
            "provider_identities",
            "album__artists",
        )
    )

    serializer_class = SongSerializer
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve the song and record a view for authenticated users.

        The interaction is recorded after the song has been
        successfully resolved, so unpublished or nonexistent
        songs cannot generate view interactions.
        """
        instance = self.get_object()

        if request.user.is_authenticated:
            MusicFeedInteractionService.record_song_view(
                user=request.user,
                song=instance,
            )

        serializer = self.get_serializer(instance)

        return Response(serializer.data)


# ============================================================
# ALBUMS
# ============================================================

class AlbumListAPIView(generics.ListAPIView):
    """
    List published albums using the lightweight album-card serializer.
    """

    queryset = (
        Album.objects
        .filter(
            status=Album.Status.PUBLISHED,
        )
        .prefetch_related(
            "artists",
        )
        .order_by("-published_at", "-pk")
    )

    serializer_class = AlbumCardSerializer
    pagination_class = MusicPagination



class AlbumDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve a published album with its artists, ordered tracklist,
    and provider-supplied song preview URLs.

    Authenticated album-detail visits are recorded as feed interactions.
    Anonymous visitors can still access published album details.
    """

    queryset = (
        Album.objects
        .filter(
            status=Album.Status.PUBLISHED,
        )
        .prefetch_related(
            "artists",
            "tracklist__song__artists",
            "tracklist__song__featured_artists",
            "tracklist__song__genres",
            "tracklist__song__album",
            "tracklist__song__provider_identities",
        )
    )

    serializer_class = AlbumSerializer
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve the album and record a view for authenticated users.
        """
        instance = self.get_object()

        if request.user.is_authenticated:
            MusicFeedInteractionService.record_album_view(
                user=request.user,
                album=instance,
            )

        serializer = self.get_serializer(instance)

        return Response(serializer.data)



# ============================================================
# ARTISTS
# ============================================================

class ArtistListAPIView(generics.ListAPIView):
    """
    List active artists using the lightweight artist-card serializer.
    """

    queryset = (
        Artist.objects
        .filter(
            is_active=True,
        )
        .order_by("name", "pk")
    )

    serializer_class = ArtistCardSerializer
    pagination_class = MusicPagination



class ArtistDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve an active artist with their published discography
    and related community posts.

    Authenticated artist-detail visits are recorded as feed interactions.
    Anonymous visitors can still access active artist details.
    """

    queryset = (
        Artist.objects
        .filter(
            is_active=True,
        )
    )

    serializer_class = ArtistSerializer
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve the artist and record a view for authenticated users.
        """
        instance = self.get_object()

        if request.user.is_authenticated:
            MusicFeedInteractionService.record_artist_view(
                user=request.user,
                artist=instance,
            )

        serializer = self.get_serializer(instance)

        return Response(serializer.data)



# ============================================================
# GENRES
# ============================================================

class GenreListAPIView(generics.ListAPIView):
    """
    List active genres.
    """

    queryset = (
        Genre.objects
        .filter(
            is_active=True,
        )
        .order_by("name", "pk")
    )

    serializer_class = GenreSerializer
    pagination_class = MusicPagination
