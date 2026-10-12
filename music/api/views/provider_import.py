from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from music.serializers.provider_import import (
    MusicProviderImportResponseSerializer,
    MusicProviderImportSerializer,
)
from music.services.provider_import import (
    MusicImportError,
    MusicProviderImportService,
)


class MusicProviderImportView(APIView):
    """
    Import an explicitly selected external music provider
    result into the canonical VibeNationHQ music catalog.

    Searching providers never creates database records.

    Import only happens after the client explicitly selects
    a provider result and sends it to this endpoint.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = MusicProviderImportSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        try:
            result = (
                MusicProviderImportService()
                .import_result(
                    serializer.to_music_search_result(),
                )
            )
        except MusicImportError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = (
            MusicProviderImportResponseSerializer(
                result,
            )
        )

        return Response(
            response_serializer.data,
            status=(
                status.HTTP_201_CREATED
                if result.created
                else status.HTTP_200_OK
            ),
        )