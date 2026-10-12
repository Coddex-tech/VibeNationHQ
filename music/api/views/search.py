from rest_framework import generics
from rest_framework.response import Response
from rest_framework import serializers

from music.serializers.search import MusicSearchSerializer
from music.services.search import MusicSearchService


class MusicSearchAPIView(generics.GenericAPIView):
    """
    Search the VibeNation music catalog.
    """

    serializer_class = MusicSearchSerializer

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("q", "").strip()

        if not query:
            raise serializers.ValidationError(
                {
                    "q": "This query parameter is required."
                }
            )

        if len(query) < 2:
            raise serializers.ValidationError(
                {
                    "q": "Search query must contain at least 2 characters."
                }
            )

        results = MusicSearchService.search(query)

        data = {
            "query": query,
            **results,
        }

        serializer = self.get_serializer(data)

        return Response(
            serializer.data,
            status=200,
        )