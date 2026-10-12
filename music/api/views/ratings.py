from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from music.models import (
    Song,
    SongRating,
    Album,
    AlbumRating,
)

from music.serializers.ratings import (
    SongRatingCreateSerializer,
    SongRatingSerializer,
    SongRatingUpdateSerializer,
    AlbumRatingCreateSerializer,
    AlbumRatingSerializer,
    AlbumRatingUpdateSerializer,
)

from music.services.ratings import (
    SongRatingService,
    AlbumRatingService,
)

from music.services.feed_interactions import (
    MusicFeedInteractionService,
)


class SongRatingAPIView(generics.GenericAPIView):
    """
    Create, update, or delete the authenticated user's rating
    for a published song.
    """

    queryset = Song.objects.filter(
        status=Song.Status.PUBLISHED
    )

    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

    def post(self, request, *args, **kwargs):
        song = self.get_object()

        serializer = SongRatingCreateSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        rating = SongRatingService.create(
            user=request.user,
            song=song,
            rating=serializer.validated_data["rating"],
        )

        MusicFeedInteractionService.record_song_rating(
            user=request.user,
            song=song,
        )

        output_serializer = SongRatingSerializer(
            rating,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=201,
        )

    def patch(self, request, *args, **kwargs):
        song = self.get_object()

        rating = SongRating.objects.filter(
            user=request.user,
            song=song,
        ).first()

        if rating is None:
            return Response(
                {
                    "detail": "You have not rated this song."
                },
                status=404,
            )

        serializer = SongRatingUpdateSerializer(
            rating,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        updated_rating = SongRatingService.update(
            rating_instance=rating,
            rating=serializer.validated_data["rating"],
        )

        MusicFeedInteractionService.record_song_rating(
            user=request.user,
            song=song,
        )

        output_serializer = SongRatingSerializer(
            updated_rating,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=200,
        )

    def delete(self, request, *args, **kwargs):
        song = self.get_object()

        rating = SongRating.objects.filter(
            user=request.user,
            song=song,
        ).first()

        if rating is None:
            return Response(
                status=204,
            )

        SongRatingService.delete(
            rating_instance=rating,
        )

        return Response(
            status=204,
        )


class AlbumRatingAPIView(generics.GenericAPIView):
    """
    Create, update, or delete the authenticated user's rating
    for a published album.
    """

    queryset = Album.objects.filter(
        status=Album.Status.PUBLISHED
    )

    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

    def post(self, request, *args, **kwargs):
        album = self.get_object()

        serializer = AlbumRatingCreateSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        rating = AlbumRatingService.create(
            user=request.user,
            album=album,
            rating=serializer.validated_data["rating"],
        )

        MusicFeedInteractionService.record_album_rating(
            user=request.user,
            album=album,
        )

        output_serializer = AlbumRatingSerializer(
            rating,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=201,
        )

    def patch(self, request, *args, **kwargs):
        album = self.get_object()

        rating = AlbumRating.objects.filter(
            user=request.user,
            album=album,
        ).first()

        if rating is None:
            return Response(
                {
                    "detail": "You have not rated this album."
                },
                status=404,
            )

        serializer = AlbumRatingUpdateSerializer(
            rating,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        updated_rating = AlbumRatingService.update(
            rating_instance=rating,
            rating=serializer.validated_data["rating"],
        )

        MusicFeedInteractionService.record_album_rating(
            user=request.user,
            album=album,
        )

        output_serializer = AlbumRatingSerializer(
            updated_rating,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=200,
        )

    def delete(self, request, *args, **kwargs):
        album = self.get_object()

        rating = AlbumRating.objects.filter(
            user=request.user,
            album=album,
        ).first()

        if rating is None:
            return Response(
                status=204,
            )

        AlbumRatingService.delete(
            rating_instance=rating,
        )

        return Response(
            status=204,
        )