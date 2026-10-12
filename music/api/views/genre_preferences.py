from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from music.models import Genre
from music.serializers.genre_preferences import (
    UserGenrePreferenceSerializer,
    UserGenrePreferenceSetSerializer,
)
from music.services.genre_preferences import (
    UserGenrePreferenceService,
)


class UserGenrePreferenceListCreateAPIView(
    APIView,
):
    """
    List and manage the authenticated user's explicit
    music genre preferences.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        preferences = (
            UserGenrePreferenceService.get_preferences(
                user=request.user,
            )
        )

        serializer = UserGenrePreferenceSerializer(
            preferences,
            many=True,
        )

        return Response(
            {
                "results": serializer.data,
            }
        )

    def post(self, request):
        serializer = UserGenrePreferenceSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        preference = (
            UserGenrePreferenceService.add_preference(
                user=request.user,
                genre=serializer.validated_data[
                    "genre"
                ],
            )
        )

        response_serializer = (
            UserGenrePreferenceSerializer(
                preference,
            )
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class UserGenrePreferenceDeleteAPIView(
    APIView,
):
    """
    Remove one explicit genre preference belonging to
    the authenticated user.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def delete(
        self,
        request,
        genre_id: int,
    ):
        try:
            genre = Genre.objects.get(
                id=genre_id,
                is_active=True,
            )
        except Genre.DoesNotExist:
            return Response(
                {
                    "detail": "Genre not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        removed = (
            UserGenrePreferenceService.remove_preference(
                user=request.user,
                genre=genre,
            )
        )

        if not removed:
            return Response(
                {
                    "detail": (
                        "You do not have this genre "
                        "in your preferences."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class UserGenrePreferenceSetAPIView(
    APIView,
):
    """
    Replace the authenticated user's complete explicit
    genre preference selection.

    Expected request:

        {
            "genre_ids": [1, 4, 7]
        }
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = (
            UserGenrePreferenceSetSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        genres = serializer.validated_data[
            "genre_ids"
        ]

        preferences = (
            UserGenrePreferenceService.set_preferences(
                user=request.user,
                genres=genres,
            )
        )

        response_serializer = (
            UserGenrePreferenceSerializer(
                preferences,
                many=True,
            )
        )

        return Response(
            {
                "results": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )