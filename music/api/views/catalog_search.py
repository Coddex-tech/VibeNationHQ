from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from music.serializers.catalog_search import (
    MusicCatalogSearchResponseSerializer,
)
from music.services.catalog_search import (
    MusicCatalogSearchService,
)


class MusicCatalogSearchView(APIView):
    """
    Search the canonical VibeNationHQ music catalog.

    This endpoint is read-only. It never creates or modifies
    artists, albums, songs, or provider identities.
    """

    DEFAULT_LIMIT = 10

    ALLOWED_ENTITY_TYPES = {
        "song",
        "album",
        "artist",
    }

    def get(self, request):
        query = request.query_params.get(
            "q",
            "",
        ).strip()

        entity_type = request.query_params.get(
            "type",
        )

        if entity_type:
            entity_type = entity_type.strip().lower()

            if entity_type not in self.ALLOWED_ENTITY_TYPES:
                return Response(
                    {
                        "detail": (
                            "Invalid entity type. "
                            "Expected song, album, or artist."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        limit_value = request.query_params.get(
            "limit",
            str(self.DEFAULT_LIMIT),
        )

        try:
            limit = int(limit_value)
        except (TypeError, ValueError):
            return Response(
                {
                    "detail": (
                        "Limit must be a valid integer."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            results = (
                MusicCatalogSearchService()
                .search(
                    query=query,
                    entity_type=entity_type,
                    limit=limit,
                )
            )
        except ValueError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            MusicCatalogSearchResponseSerializer(
                {
                    "results": results,
                }
            )
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )