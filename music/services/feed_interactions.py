
from __future__ import annotations

from uuid import UUID

from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

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
    Records behavioral interaction history for VibeNationHQ.

    Persistent relationships such as favorites, ratings, likes,
    and follows remain the source of truth in their respective
    models.

    This service records behavioral history after successful
    actions.

    Passive interactions can be recorded through the public
    interaction API. Engagement interactions must be recorded
    server-side after their corresponding persistent action
    succeeds.
    """

    TARGET_FIELDS = (
        "song",
        "album",
        "artist",
        "community_post",
        "editorial_article",
    )

    # ========================================================
    # Internal helpers
    # ========================================================

    @classmethod
    def _get_target_ids(
        cls,
        *,
        song: Song | None = None,
        album: Album | None = None,
        artist: Artist | None = None,
        community_post: CommunityPost | None = None,
        editorial_article: EditorialArticle | None = None,
    ) -> dict:
        targets = {
            "song": song,
            "album": album,
            "artist": artist,
            "community_post": community_post,
            "editorial_article": editorial_article,
        }

        return {
            field: (
                target.pk
                if target is not None
                else None
            )
            for field, target in targets.items()
        }

    @classmethod
    def _matches_existing_event(
        cls,
        *,
        existing: MusicFeedInteraction,
        user,
        interaction_type: str,
        target_ids: dict,
    ) -> bool:
        """
        Check whether an existing event represents exactly
        the same request.

        An idempotency key cannot be reused for another user,
        interaction type, or target.
        """
        if existing.user_id != user.pk:
            return False

        if existing.interaction_type != interaction_type:
            return False

        for field in cls.TARGET_FIELDS:
            existing_target_id = getattr(
                existing,
                f"{field}_id",
            )

            if existing_target_id != target_ids[field]:
                return False

        return True

    @classmethod
    def _record(
        cls,
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

        Identical retries using the same idempotency key return
        the original event.

        Reusing a key for a different event raises a validation
        error.

        The nested atomic block ensures an IntegrityError does
        not leave an enclosing transaction in a broken state.
        """
        target_ids = cls._get_target_ids(
            song=song,
            album=album,
            artist=artist,
            community_post=community_post,
            editorial_article=editorial_article,
        )

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

            if not cls._matches_existing_event(
                existing=existing,
                user=user,
                interaction_type=interaction_type,
                target_ids=target_ids,
            ):
                raise ValidationError(
                    {
                        "idempotency_key": (
                            "This idempotency key has already "
                            "been used for a different "
                            "interaction."
                        )
                    }
                )

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

    @classmethod
    def record_community_post_favorite(
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
                .FAVORITE_COMMUNITY_POST
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

    @classmethod
    def record_editorial_favorite(
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
                .FAVORITE_EDITORIAL
            ),
            idempotency_key=idempotency_key,
            editorial_article=article,
        )
