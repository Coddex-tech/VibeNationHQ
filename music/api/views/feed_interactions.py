from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from music.models import (
    MusicFeedInteraction,
)
from music.serializers.feed_interactions import (
    MusicFeedInteractionSerializer,
)
from music.services.feed_interactions import (
    MusicFeedInteractionService,
)


class MusicFeedInteractionAPIView(APIView):
    """
    Records an authenticated user's behavioral interaction
    with music-related content.

    The request is validated by
    MusicFeedInteractionSerializer.

    The target object is resolved here, while persistence is
    delegated to MusicFeedInteractionService.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        serializer = (
            MusicFeedInteractionSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        target_model = (
            serializer.get_target_model()
        )

        target_id = serializer.get_target_id()

        target = get_object_or_404(
            target_model,
            pk=target_id,
        )

        interaction_type = (
            serializer.validated_data[
                "interaction_type"
            ]
        )

        idempotency_key = (
            serializer.get_idempotency_key()
        )

        interaction = (
            self._record_interaction(
                request=request,
                interaction_type=interaction_type,
                target=target,
                target_type=serializer.validated_data[
                    "target_type"
                ],
                idempotency_key=idempotency_key,
            )
        )

        return Response(
            {
                "id": interaction.id,
                "interaction_type": (
                    interaction.interaction_type
                ),
                "target_type": serializer.validated_data[
                    "target_type"
                ],
                "target_id": target.id,
            },
            status=status.HTTP_201_CREATED,
        )

    def _record_interaction(
        self,
        *,
        request,
        interaction_type: str,
        target,
        target_type: str,
        idempotency_key,
    ):
        if target_type == "song":
            return self._record_song_interaction(
                request=request,
                interaction_type=interaction_type,
                target=target,
                idempotency_key=idempotency_key,
            )

        if target_type == "album":
            return self._record_album_interaction(
                request=request,
                interaction_type=interaction_type,
                target=target,
                idempotency_key=idempotency_key,
            )

        if target_type == "artist":
            return self._record_artist_interaction(
                request=request,
                interaction_type=interaction_type,
                target=target,
                idempotency_key=idempotency_key,
            )

        if target_type == "community_post":
            return (
                self._record_community_post_interaction(
                    request=request,
                    interaction_type=interaction_type,
                    target=target,
                    idempotency_key=idempotency_key,
                )
            )

        if target_type == "editorial":
            return self._record_editorial_interaction(
                request=request,
                interaction_type=interaction_type,
                target=target,
                idempotency_key=idempotency_key,
            )

        raise ValueError(
            f"Unsupported interaction target type: "
            f"{target_type}"
        )

    def _record_song_interaction(
        self,
        *,
        request,
        interaction_type: str,
        target,
        idempotency_key,
    ):
        service = (
            MusicFeedInteractionService
        )

        if interaction_type == "view_song":
            return service.record_song_view(
                user=request.user,
                song=target,
                idempotency_key=idempotency_key,
            )

        if interaction_type == "play_preview":
            return service.record_preview_play(
                user=request.user,
                song=target,
                idempotency_key=idempotency_key,
            )

        if interaction_type == "favorite_song":
            return service.record_song_favorite(
                user=request.user,
                song=target,
                idempotency_key=idempotency_key,
            )

        if interaction_type == "rate_song":
            return service.record_song_rating(
                user=request.user,
                song=target,
                idempotency_key=idempotency_key,
            )

        raise ValueError(
            f"Unsupported song interaction: "
            f"{interaction_type}"
        )

    def _record_album_interaction(
        self,
        *,
        request,
        interaction_type: str,
        target,
        idempotency_key,
    ):
        service = (
            MusicFeedInteractionService
        )

        if interaction_type == "view_album":
            return service.record_album_view(
                user=request.user,
                album=target,
                idempotency_key=idempotency_key,
            )

        if interaction_type == "favorite_album":
            return service.record_album_favorite(
                user=request.user,
                album=target,
                idempotency_key=idempotency_key,
            )

        if interaction_type == "rate_album":
            return service.record_album_rating(
                user=request.user,
                album=target,
                idempotency_key=idempotency_key,
            )

        raise ValueError(
            f"Unsupported album interaction: "
            f"{interaction_type}"
        )

    def _record_artist_interaction(
        self,
        *,
        request,
        interaction_type: str,
        target,
        idempotency_key,
    ):
        service = (
            MusicFeedInteractionService
        )

        if interaction_type == "view_artist":
            return service.record_artist_view(
                user=request.user,
                artist=target,
                idempotency_key=idempotency_key,
            )

        if interaction_type == "follow_artist":
            return service.record_artist_follow(
                user=request.user,
                artist=target,
                idempotency_key=idempotency_key,
            )

        raise ValueError(
            f"Unsupported artist interaction: "
            f"{interaction_type}"
        )

    def _record_community_post_interaction(
        self,
        *,
        request,
        interaction_type: str,
        target,
        idempotency_key,
    ):
        service = (
            MusicFeedInteractionService
        )

        if interaction_type == "view_community_post":
            return (
                service.record_community_post_view(
                    user=request.user,
                    post=target,
                    idempotency_key=idempotency_key,
                )
            )

        if interaction_type == "like_community_post":
            return (
                service.record_community_post_like(
                    user=request.user,
                    post=target,
                    idempotency_key=idempotency_key,
                )
            )

        if (
            interaction_type
            == "comment_community_post"
        ):
            return (
                service.record_community_post_comment(
                    user=request.user,
                    post=target,
                    idempotency_key=idempotency_key,
                )
            )

        raise ValueError(
            "Unsupported community post "
            f"interaction: {interaction_type}"
        )

    def _record_editorial_interaction(
        self,
        *,
        request,
        interaction_type: str,
        target,
        idempotency_key,
    ):
        service = (
            MusicFeedInteractionService
        )

        if interaction_type == "view_editorial":
            return service.record_editorial_view(
                user=request.user,
                article=target,
                idempotency_key=idempotency_key,
            )

        if interaction_type == "like_editorial":
            return service.record_editorial_like(
                user=request.user,
                article=target,
                idempotency_key=idempotency_key,
            )

        raise ValueError(
            f"Unsupported editorial interaction: "
            f"{interaction_type}"
        )