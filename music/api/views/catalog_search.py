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
    MAX_LIMIT = 20
    MAX_QUERY_LENGTH = 200

    ALLOWED_ENTITY_TYPES = {
        "song",
        "album",
        "artist",
    }

    def get(self, request):
        query = request.query_params.get("q", "").strip()

        if len(query) > self.MAX_QUERY_LENGTH:
            return Response(
                {
                    "detail": (
                        f"Search query must not exceed "
                        f"{self.MAX_QUERY_LENGTH} characters."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_entity_type = request.query_params.get("type")
        entity_type = None

        if raw_entity_type is not None:
            entity_type = raw_entity_type.strip().lower()

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
                    "detail": "Limit must be a valid integer."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not 1 <= limit <= self.MAX_LIMIT:
            return Response(
                {
                    "detail": (
                        f"Limit must be between 1 and "
                        f"{self.MAX_LIMIT}."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Empty queries return a valid empty response without
        # performing catalog database searches.
        if not query:
            serializer = MusicCatalogSearchResponseSerializer(
                {"results": []}
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        try:
            results = MusicCatalogSearchService().search(
                query=query,
                entity_type=entity_type,
                limit=limit,
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = MusicCatalogSearchResponseSerializer(
            {"results": results}
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )