from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from music.models import (
    Album,
    AlbumFavorite,
    Song,
    SongFavorite,
)

from music.serializers.favorites import (
    AlbumFavoriteCreateSerializer,
    AlbumFavoriteSerializer,
    SongFavoriteCreateSerializer,
    SongFavoriteSerializer,
)

from music.services.favorites import (
    AlbumFavoriteService,
    SongFavoriteService,
)

from music.services.feed_interactions import (
    MusicFeedInteractionService,
)


class SongFavoriteAPIView(generics.GenericAPIView):
    queryset = Song.objects.filter(
        status=Song.Status.PUBLISHED
    )
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        song = self.get_object()

        serializer = SongFavoriteCreateSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        favorite = SongFavoriteService.create(
            user=request.user,
            song=song,
        )

        MusicFeedInteractionService.record_song_favorite(
            user=request.user,
            song=song,
        )

        output_serializer = SongFavoriteSerializer(
            favorite,
            context=self.get_serializer_context(),
        )

        song.refresh_from_db()

        return Response(
            {
                "favorited": True,
                "favorites_count": song.favorites_count,
                "favorite": output_serializer.data,
            },
            status=201,
        )

    def delete(self, request, *args, **kwargs):
        song = self.get_object()

        favorite = SongFavorite.objects.filter(
            user=request.user,
            song=song,
        ).first()

        if favorite is None:
            return Response(
                {
                    "favorited": False,
                    "favorites_count": song.favorites_count,
                },
                status=200,
            )

        SongFavoriteService.delete(
            favorite_instance=favorite,
        )

        song.refresh_from_db()

        return Response(
            {
                "favorited": False,
                "favorites_count": song.favorites_count,
            },
            status=200,
        )


class AlbumFavoriteAPIView(generics.GenericAPIView):
    queryset = Album.objects.filter(
        status=Album.Status.PUBLISHED
    )
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        album = self.get_object()

        serializer = AlbumFavoriteCreateSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        favorite = AlbumFavoriteService.create(
            user=request.user,
            album=album,
        )

        MusicFeedInteractionService.record_album_favorite(
            user=request.user,
            album=album,
        )

        output_serializer = AlbumFavoriteSerializer(
            favorite,
            context=self.get_serializer_context(),
        )

        album.refresh_from_db()

        return Response(
            {
                "favorited": True,
                "favorites_count": album.favorites_count,
                "favorite": output_serializer.data,
            },
            status=201,
        )

    def delete(self, request, *args, **kwargs):
        album = self.get_object()

        favorite = AlbumFavorite.objects.filter(
            user=request.user,
            album=album,
        ).first()

        if favorite is None:
            return Response(
                {
                    "favorited": False,
                    "favorites_count": album.favorites_count,
                },
                status=200,
            )

        AlbumFavoriteService.delete(
            favorite_instance=favorite,
        )

        album.refresh_from_db()

        return Response(
            {
                "favorited": False,
                "favorites_count": album.favorites_count,
            },
            status=200,
        )