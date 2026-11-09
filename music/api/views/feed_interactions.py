
from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.api.permissions import (
    IsOrdinaryVibeNationUser,
)

from music.models import (
    Album,
    Artist,
    CommunityPost,
    EditorialArticle,
    MusicFeedInteraction,
    Song,
)

from music.serializers.feed_interactions import (
    MusicFeedInteractionSerializer,
)

from music.services.feed_interactions import (
    MusicFeedInteractionService,
)


class MusicFeedInteractionAPIView(APIView):
    """
    Records passive behavioral interactions submitted by
    authenticated ordinary VibeNation users.

    Engagement interactions such as likes, favorites,
    comments, ratings, and follows must be recorded by
    their respective backend action endpoints.
    """

    permission_classes = [
        IsAuthenticated,
        IsOrdinaryVibeNationUser,
    ]

    INTERACTION_METHODS = {
        "view_song": (
            "record_song_view",
            "song",
        ),
        "play_preview": (
            "record_preview_play",
            "song",
        ),
        "view_album": (
            "record_album_view",
            "album",
        ),
        "view_artist": (
            "record_artist_view",
            "artist",
        ),
        "view_community_post": (
            "record_community_post_view",
            "post",
        ),
        "view_editorial": (
            "record_editorial_view",
            "article",
        ),
    }

    def post(self, request, *args, **kwargs):
        serializer = MusicFeedInteractionSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        interaction_type = (
            serializer.validated_data["interaction_type"]
        )

        target_type = (
            serializer.validated_data["target_type"]
        )

        target_id = serializer.get_target_id()

        idempotency_key = (
            serializer.get_idempotency_key()
        )

        target = self._get_eligible_target(
            target_type=target_type,
            target_id=target_id,
        )

        interaction = self._record_interaction(
            user=request.user,
            interaction_type=interaction_type,
            target_type=target_type,
            target=target,
            idempotency_key=idempotency_key,
        )

        return Response(
            {
                "id": interaction.id,
                "interaction_type": (
                    interaction.interaction_type
                ),
                "target_type": target_type,
                "target_id": target.pk,
            },
            status=status.HTTP_201_CREATED,
        )

    def _get_eligible_target(
        self,
        *,
        target_type: str,
        target_id: int,
    ):
        """
        Resolve a target only when it is currently eligible
        for passive interaction tracking.

        Unpublished, archived, hidden, removed, and inactive
        content is not eligible.
        """

        if target_type == "song":
            return get_object_or_404(
                Song,
                pk=target_id,
                status=Song.Status.PUBLISHED,
            )

        if target_type == "album":
            return get_object_or_404(
                Album,
                pk=target_id,
                status=Album.Status.PUBLISHED,
            )

        if target_type == "artist":
            return get_object_or_404(
                Artist,
                pk=target_id,
                is_active=True,
            )

        if target_type == "community_post":
            return get_object_or_404(
                CommunityPost,
                pk=target_id,
                status=CommunityPost.Status.PUBLISHED,
            )

        if target_type == "editorial":
            return get_object_or_404(
                EditorialArticle,
                pk=target_id,
                status=EditorialArticle.Status.PUBLISHED,
            )

        return None

    def _record_interaction(
        self,
        *,
        user,
        interaction_type: str,
        target_type: str,
        target,
        idempotency_key,
    ) -> MusicFeedInteraction:
        """
        Dispatch only passive interactions accepted by
        MusicFeedInteractionSerializer.
        """

        method_config = self.INTERACTION_METHODS.get(
            interaction_type,
        )

        if method_config is None:
            raise ValueError(
                f"Unsupported passive interaction: "
                f"{interaction_type}"
            )

        service_method_name, target_argument = (
            method_config
        )

        service_method = getattr(
            MusicFeedInteractionService,
            service_method_name,
        )

        return service_method(
            user=user,
            **{
                target_argument: target,
            },
            idempotency_key=idempotency_key,
        )
