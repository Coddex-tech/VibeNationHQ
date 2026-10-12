from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ...serializers.provider_search import (
    MusicProviderSearchResultSerializer,
)
from music.providers.base import MusicEntityType
from music.services.provider_search import (
    MusicProviderSearchService,
)


class MusicProviderSearchView(APIView):
    """
    Search external music providers.

    Query parameters:

    q:
        Search query.

    type:
        Optional entity type:
        song, album, or artist.

    country:
        Optional two-letter country code.
        Defaults to NG.

    limit:
        Optional result limit.
        Defaults to 10 and is capped by the service.
    """

    search_service = MusicProviderSearchService()

    def get(self, request):
        query = request.query_params.get(
            "q",
            "",
        ).strip()

        if not query:
            return Response(
                {
                    "detail": (
                        "A search query is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        entity_type = self._parse_entity_type(
            request.query_params.get("type")
        )

        if (
            request.query_params.get("type")
            and entity_type is None
        ):
            return Response(
                {
                    "detail": (
                        "Invalid type. "
                        "Use song, album, or artist."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        country = self._parse_country(
            request.query_params.get(
                "country",
                "NG",
            )
        )

        if country is None:
            return Response(
                {
                    "detail": (
                        "Country must be a valid "
                        "2-letter country code."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        limit = self._parse_limit(
            request.query_params.get("limit")
        )

        if limit is None:
            return Response(
                {
                    "detail": (
                        "Limit must be a valid integer."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            results = self.search_service.search(
                query=query,
                entity_type=entity_type,
                country=country,
                limit=limit,
            )
        except ValueError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = MusicProviderSearchResultSerializer(
            results,
            many=True,
        )

        return Response(
            {
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _parse_entity_type(
        value: str | None,
    ) -> MusicEntityType | None:
        if not value:
            return None

        try:
            return MusicEntityType(
                value.strip().lower()
            )
        except ValueError:
            return None

    @staticmethod
    def _parse_country(
        value: str | None,
    ) -> str | None:
        if value is None:
            return "NG"

        normalized = value.strip().upper()

        if (
            len(normalized) != 2
            or not normalized.isalpha()
        ):
            return None

        return normalized

    @staticmethod
    def _parse_limit(
        value: str | None,
    ) -> int | None:
        if value is None or not value.strip():
            return 10

        try:
            return int(value)
        except (TypeError, ValueError):
            return None