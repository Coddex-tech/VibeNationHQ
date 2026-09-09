from rest_framework import generics

from music.api.pagination import MusicPagination
from music.models import Album, Song, Artist, Genre
from music.serializers.catalog import (
    AlbumCardSerializer,
    AlbumSerializer,
    SongCardSerializer,
    SongSerializer,
    ArtistSerializer,
    ArtistCardSerializer,
    GenreSerializer,
)


class SongListAPIView(generics.ListAPIView):
    """
    List published songs in the VibeNation music catalog.
    """

    queryset = (
        Song.objects
        .filter(status=Song.Status.PUBLISHED)
        .select_related("album")
        .prefetch_related(
            "artists",
            "featured_artists",
            "genres",
        )
        .order_by("-published_at")
    )

    serializer_class = SongCardSerializer
    pagination_class = MusicPagination


class SongDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve a single published song by slug.
    """

    queryset = (
        Song.objects
        .filter(status=Song.Status.PUBLISHED)
        .select_related("album")
        .prefetch_related(
            "artists",
            "featured_artists",
            "genres",
        )
    )

    serializer_class = SongSerializer
    lookup_field = "slug"


class AlbumListAPIView(generics.ListAPIView):
    """
    List published albums in the VibeNation music catalog.
    """

    queryset = (
        Album.objects
        .filter(status=Album.Status.PUBLISHED)
        .prefetch_related("artists")
        .order_by("-published_at")
    )

    serializer_class = AlbumCardSerializer
    pagination_class = MusicPagination


class AlbumDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve a single published album by slug.
    """

    queryset = (
        Album.objects
        .filter(status=Album.Status.PUBLISHED)
        .prefetch_related(
            "artists",
            "tracklist__song__artists",
            "tracklist__song__featured_artists",
        )
    )

    serializer_class = AlbumSerializer
    lookup_field = "slug"


class ArtistListAPIView(generics.ListAPIView):
    """
    List active artists in the VibeNation music catalog.
    """

    queryset = (
        Artist.objects
        .filter(is_active=True)
        .order_by("name")
    )

    serializer_class = ArtistCardSerializer
    pagination_class = MusicPagination


class ArtistDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve a single active artist by slug.
    """

    queryset = (
        Artist.objects
        .filter(is_active=True)
    )

    serializer_class = ArtistSerializer
    lookup_field = "slug"


class GenreListAPIView(generics.ListAPIView):
    """
    List active genres in the VibeNation music catalog.
    """

    queryset = (
        Genre.objects
        .filter(is_active=True)
        .order_by("name")
    )

    serializer_class = GenreSerializer
    pagination_class = MusicPagination