from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from music.serializers.feed import MusicFeedSerializer
from music.services.feed import MusicFeedService
from music.services.feed_cursor import FeedCursorError


class MusicFeedAPIView(APIView):
    """
    Return the personalized VibeNationHQ music feed.

    The feed service owns candidate generation, personalization,
    ranking, diversity, and cursor-based snapshots.

    This API view is intentionally thin and only handles:
    - request parameters
    - authentication context
    - service invocation
    - serialization
    - cursor errors
    """

    def get(self, request):
        limit = request.query_params.get("limit")

        if limit is None:
            limit = MusicFeedService.DEFAULT_LIMIT
        else:
            try:
                limit = int(limit)
            except (TypeError, ValueError):
                return Response(
                    {
                        "detail": (
                            "The 'limit' parameter must be "
                            "a valid integer."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        cursor = request.query_params.get("cursor")

        user = (
            request.user
            if request.user.is_authenticated
            else None
        )

        try:
            data = MusicFeedService().get_feed(
                user=user,
                limit=limit,
                cursor=cursor,
            )
        except FeedCursorError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = MusicFeedSerializer(
            data,
            context={
                "request": request,
            },
        )

        return Response(serializer.data)