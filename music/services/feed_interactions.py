from __future__ import annotations

from uuid import UUID

from django.db import IntegrityError, transaction

from music.models import (
    Album,
    Artist,
    CommunityPost,
    EditorialArticle,
    MusicFeedInteraction,
    Song,
)


class MusicFeedInteractionService:
    """
    Records behavioral interactions used by the VibeNationHQ
    music feed and recommendation system.

    Persistent relationships such as favorites, ratings, likes,
    and follows remain the source of truth in their respective
    models.

    This service records behavioral history after those actions
    succeed.

    Examples:

        MusicFeedInteractionService.record_song_view(...)
        MusicFeedInteractionService.record_preview_play(...)
        MusicFeedInteractionService.record_artist_view(...)
    """

    # ========================================================
    # Internal helpers
    # ========================================================

    @staticmethod
    def _record(
        *,
        user,
        interaction_type: str,
        idempotency_key: UUID | None = None,
        song: Song | None = None,
        album: Album | None = None,
        artist: Artist | None = None,
        community_post: CommunityPost | None = None,
        editorial_article: EditorialArticle | None = None,
    ) -> MusicFeedInteraction:
        """
        Create one behavioral interaction.

        The database constraint on MusicFeedInteraction remains
        the final authority for validating the target/type
        combination.
        """

        try:
            with transaction.atomic():
                return MusicFeedInteraction.objects.create(
                    user=user,
                    interaction_type=interaction_type,
                    idempotency_key=idempotency_key,
                    song=song,
                    album=album,
                    artist=artist,
                    community_post=community_post,
                    editorial_article=editorial_article,
                )

        except IntegrityError:
            # An idempotency key may have already been processed
            # because the client retried the same request.
            if idempotency_key is None:
                raise

            existing = (
                MusicFeedInteraction.objects
                .filter(
                    idempotency_key=idempotency_key,
                )
                .first()
            )

            if existing is None:
                raise

            return existing

    # ========================================================
    # Song interactions
    # ========================================================

    @classmethod
    def record_song_view(
        cls,
        *,
        user,
        song: Song,
        idempotency_key: UUID | None = None,
    ) -> MusicFeedInteraction:
        return cls._record(
            user=user,
            interaction_type=(
                MusicFeedInteraction.InteractionType
                .VIEW_SONG
            ),
            idempotency_key=idempotency_key,
            song=song,
        )

    @classmethod
    def record_preview_play(
        cls,
        *,
        user,
        song: Song,
        idempotency_key: UUID | None = None,
    ) -> MusicFeedInteraction:
        return cls._record(
            user=user,
            interaction_type=(
                MusicFeedInteraction.InteractionType
                .PLAY_PREVIEW
            ),
            idempotency_key=idempotency_key,
            song=song,
        )

    @classmethod
    def record_song_favorite(
        cls,
        *,
        user,
        song: Song,
        idempotency_key: UUID | None = None,
    ) -> MusicFeedInteraction:
        return cls._record(
            user=user,
            interaction_type=(
                MusicFeedInteraction.InteractionType
                .FAVORITE_SONG
            ),
            idempotency_key=idempotency_key,
            song=song,
        )

    @classmethod
    def record_song_rating(
        cls,
        *,
        user,
        song: Song,
        idempotency_key: UUID | None = None,
    ) -> MusicFeedInteraction:
        return cls._record(
            user=user,
            interaction_type=(
                MusicFeedInteraction.InteractionType
                .RATE_SONG
            ),
            idempotency_key=idempotency_key,
            song=song,
        )

    # ========================================================
    # Album interactions
    # ========================================================

    @classmethod
    def record_album_view(
        cls,
        *,
        user,
        album: Album,
        idempotency_key: UUID | None = None,
    ) -> MusicFeedInteraction:
        return cls._record(
            user=user,
            interaction_type=(
                MusicFeedInteraction.InteractionType
                .VIEW_ALBUM
            ),
            idempotency_key=idempotency_key,
            album=album,
        )

    @classmethod
    def record_album_favorite(
        cls,
        *,
        user,
        album: Album,
        idempotency_key: UUID | None = None,
    ) -> MusicFeedInteraction:
        return cls._record(
            user=user,
            interaction_type=(
                MusicFeedInteraction.InteractionType
                .FAVORITE_ALBUM
            ),
            idempotency_key=idempotency_key,
            album=album,
        )

    @classmethod
    def record_album_rating(
        cls,
        *,
        user,
        album: Album,
        idempotency_key: UUID | None = None,
    ) -> MusicFeedInteraction:
        return cls._record(
            user=user,
            interaction_type=(
                MusicFeedInteraction.InteractionType
                .RATE_ALBUM
            ),
            idempotency_key=idempotency_key,
            album=album,
        )

    # ========================================================
    # Artist interactions
    # ========================================================

    @classmethod
    def record_artist_view(
        cls,
        *,
        user,
        artist: Artist,
        idempotency_key: UUID | None = None,
    ) -> MusicFeedInteraction:
        return cls._record(
            user=user,
            interaction_type=(
                MusicFeedInteraction.InteractionType
                .VIEW_ARTIST
            ),
            idempotency_key=idempotency_key,
            artist=artist,
        )

    @classmethod
    def record_artist_follow(
        cls,
        *,
        user,
        artist: Artist,
        idempotency_key: UUID | None = None,
    ) -> MusicFeedInteraction:
        return cls._record(
            user=user,
            interaction_type=(
                MusicFeedInteraction.InteractionType
                .FOLLOW_ARTIST
            ),
            idempotency_key=idempotency_key,
            artist=artist,
        )

    # ========================================================
    # Community interactions
    # ========================================================

    @classmethod
    def record_community_post_view(
        cls,
        *,
        user,
        post: CommunityPost,
        idempotency_key: UUID | None = None,
    ) -> MusicFeedInteraction:
        return cls._record(
            user=user,
            interaction_type=(
                MusicFeedInteraction.InteractionType
                .VIEW_COMMUNITY_POST
            ),
            idempotency_key=idempotency_key,
            community_post=post,
        )

    @classmethod
    def record_community_post_like(
        cls,
        *,
        user,
        post: CommunityPost,
        idempotency_key: UUID | None = None,
    ) -> MusicFeedInteraction:
        return cls._record(
            user=user,
            interaction_type=(
                MusicFeedInteraction.InteractionType
                .LIKE_COMMUNITY_POST
            ),
            idempotency_key=idempotency_key,
            community_post=post,
        )

    @classmethod
    def record_community_post_comment(
        cls,
        *,
        user,
        post: CommunityPost,
        idempotency_key: UUID | None = None,
    ) -> MusicFeedInteraction:
        return cls._record(
            user=user,
            interaction_type=(
                MusicFeedInteraction.InteractionType
                .COMMENT_COMMUNITY_POST
            ),
            idempotency_key=idempotency_key,
            community_post=post,
        )

    # ========================================================
    # Editorial interactions
    # ========================================================

    @classmethod
    def record_editorial_view(
        cls,
        *,
        user,
        article: EditorialArticle,
        idempotency_key: UUID | None = None,
    ) -> MusicFeedInteraction:
        return cls._record(
            user=user,
            interaction_type=(
                MusicFeedInteraction.InteractionType
                .VIEW_EDITORIAL
            ),
            idempotency_key=idempotency_key,
            editorial_article=article,
        )

    @classmethod
    def record_editorial_like(
        cls,
        *,
        user,
        article: EditorialArticle,
        idempotency_key: UUID | None = None,
    ) -> MusicFeedInteraction:
        return cls._record(
            user=user,
            interaction_type=(
                MusicFeedInteraction.InteractionType
                .LIKE_EDITORIAL
            ),
            idempotency_key=idempotency_key,
            editorial_article=article,
        )