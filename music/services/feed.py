from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from django.db.models import (
    BooleanField,
    Count,
    Exists,
    OuterRef,
    Value,
)
from django.utils import timezone

from music.models import (
    ArtistFollow,
    CommunityPost,
    CommunityPostComment,
    CommunityPostCommentLike,
    CommunityPostFavorite,
    CommunityPostLike,
    EditorialArticle,
    EditorialArticleFavorite,
    EditorialArticleLike,
    MusicFeedInteraction,
    UserFollow,
)

from music.services.feed_cursor import (
    FeedCursorError,
    FeedSnapshotItem,
    FeedSnapshotStore,
)


@dataclass(frozen=True, slots=True)
class FeedCandidate:
    content_type: str
    source: str
    object: Any
    score: float = 0.0

    @property
    def object_id(self) -> int:
        return self.object.id


@dataclass(frozen=True, slots=True)
class FeedUserContext:
    following_user_ids: frozenset[int]
    follower_user_ids: frozenset[int]
    mutual_user_ids: frozenset[int]
    followed_artist_ids: frozenset[int]
    preferred_genre_ids: frozenset[int]

    interacted_song_ids: frozenset[int]
    interacted_album_ids: frozenset[int]
    interacted_artist_ids: frozenset[int]

    liked_community_post_ids: frozenset[int]
    favorited_community_post_ids: frozenset[int]
    commented_community_post_ids: frozenset[int]
    comment_liked_post_ids: frozenset[int]

    interacted_community_post_ids: frozenset[int]
    engaged_creator_ids: frozenset[int]


class MusicFeedService:
    """
    Personalized VibeNationHQ feed containing:

    - Community posts
    - Published editorial articles

    Community posts retain their existing recommendation,
    personalization, ranking, and diversity behavior.

    Editorial articles use separate editorial ordering signals.
    Editorial engagement never affects community-post ranking.

    Music attached to a community post enriches personalization.
    Songs, albums, and artists are never independent feed items.

    Feed snapshots preserve the original mixed ordering across
    cursor pages.
    """

    DEFAULT_LIMIT = 20
    MAX_LIMIT = 50

    CANDIDATE_MULTIPLIER = 4
    MAX_CANDIDATES = 100

    INTERACTION_LOOKBACK_DAYS = 90
    INTERACTION_LIMIT = 500

    COMMUNITY_POSTS_PER_EDITORIAL = 10

    SOURCE_PRIORITY = {
        "just_published": 110,
        "mutual": 100,
        "following": 90,
        "followed_artist": 80,
        "history": 70,
        "recent": 30,
        "editorial": 10,
    }

    def get_feed(
        self,
        *,
        user=None,
        limit: int = DEFAULT_LIMIT,
        cursor: str | None = None,
        new_post_id: int | str | None = None,
    ) -> dict[str, Any]:
        """
        Return one page of the mixed community and editorial feed.

        A request without a cursor creates a new snapshot.

        If new_post_id belongs to the authenticated requesting user
        and is published, that post is placed first in the new
        snapshot. It receives no permanent ranking boost.

        Cursor requests always continue their existing snapshot.
        """
        limit = self._normalize_limit(limit)

        if cursor:
            return self._get_snapshot_page(
                cursor=cursor,
                limit=limit,
                user=user,
            )

        candidate_limit = min(
            limit * self.CANDIDATE_MULTIPLIER,
            self.MAX_CANDIDATES,
        )

        # Community candidates are generated and ranked independently.
        community_candidates = self._generate_candidates(
            user=user,
            candidate_limit=candidate_limit,
        )

        pinned_candidate = self._get_newly_published_candidate(
            user=user,
            new_post_id=new_post_id,
        )

        if pinned_candidate is not None:
            community_candidates.insert(
                0,
                pinned_candidate,
            )

        community_candidates = self._deduplicate_candidates(
            candidates=community_candidates,
            limit=candidate_limit,
        )

        # Only community candidates enter the recommendation context.
        context = self._build_user_context(
            user=user,
            candidates=community_candidates,
        )

        ranked_community_candidates = self._rank_candidates(
            candidates=community_candidates,
            context=context,
        )

        # Preserve the newly published post at absolute position one.
        if pinned_candidate is not None:
            pinned_key = (
                "community_post",
                pinned_candidate.object_id,
            )

            pinned_ranked_candidate = next(
                (
                    candidate
                    for candidate in ranked_community_candidates
                    if (
                        candidate.content_type,
                        candidate.object_id,
                    ) == pinned_key
                ),
                None,
            )

            ranked_community_candidates = [
                candidate
                for candidate in ranked_community_candidates
                if (
                    candidate.content_type,
                    candidate.object_id,
                ) != pinned_key
            ]

            if pinned_ranked_candidate is not None:
                ranked_community_candidates.insert(
                    0,
                    pinned_ranked_candidate,
                )

        # Diversity is applied to community posts only.
        diverse_community_candidates = self._select_diverse(
            candidates=ranked_community_candidates,
            limit=len(ranked_community_candidates),
        )

        # Editorial articles have their own ordering system.
        editorial_candidates = self._generate_editorial_candidates(
            limit=candidate_limit,
        )

        # Combine the two independently prepared pools.
        ordered_candidates = self._mix_feed_candidates(
            community_candidates=diverse_community_candidates,
            editorial_candidates=editorial_candidates,
        )

        snapshot_items = [
            FeedSnapshotItem(
                content_type=candidate.content_type,
                object_id=candidate.object_id,
                source=candidate.source,
                score=candidate.score,
            )
            for candidate in ordered_candidates
        ]

        snapshot_id = FeedSnapshotStore.create_snapshot(
            snapshot_items,
        )

        return self._build_snapshot_page(
            snapshot_id=snapshot_id,
            snapshot_items=snapshot_items,
            position=0,
            limit=limit,
            user=user,
        )

    # ------------------------------------------------------------------
    # Newly published community post
    # ------------------------------------------------------------------

    def _get_newly_published_candidate(
        self,
        *,
        user,
        new_post_id: int | str | None,
    ) -> FeedCandidate | None:
        """
        Resolve a post to temporarily prioritize after creation.

        The post must belong to the requesting user and must already
        be published. Invalid IDs are ignored.
        """
        if (
            user is None
            or not user.is_authenticated
            or new_post_id is None
        ):
            return None

        try:
            post_id = int(new_post_id)
        except (TypeError, ValueError):
            return None

        if post_id <= 0:
            return None

        post = (
            self._community_post_queryset()
            .filter(
                id=post_id,
                user_id=user.id,
                status=CommunityPost.Status.PUBLISHED,
            )
            .first()
        )

        if post is None:
            return None

        return FeedCandidate(
            content_type="community_post",
            source="just_published",
            object=post,
        )

    # ------------------------------------------------------------------
    # Snapshot pagination
    # ------------------------------------------------------------------

    def _get_snapshot_page(
        self,
        *,
        cursor: str,
        limit: int,
        user=None,
    ) -> dict[str, Any]:
        decoded_cursor = FeedSnapshotStore.decode_cursor(
            cursor,
        )

        snapshot_items = FeedSnapshotStore.get_snapshot(
            decoded_cursor.snapshot_id,
        )

        return self._build_snapshot_page(
            snapshot_id=decoded_cursor.snapshot_id,
            snapshot_items=snapshot_items,
            position=decoded_cursor.position,
            limit=limit,
            user=user,
        )

    def _build_snapshot_page(
        self,
        *,
        snapshot_id: str,
        snapshot_items: list[FeedSnapshotItem],
        position: int,
        limit: int,
        user=None,
    ) -> dict[str, Any]:
        total_items = len(snapshot_items)

        if position > total_items:
            raise FeedCursorError(
                "This feed cursor points beyond the "
                "available feed."
            )

        page_items = snapshot_items[
            position : position + limit
        ]

        next_position = position + len(page_items)
        has_more = next_position < total_items

        if has_more:
            next_cursor = FeedSnapshotStore.create_cursor(
                snapshot_id=snapshot_id,
                position=next_position,
            )
        else:
            next_cursor = None

            FeedSnapshotStore.delete_snapshot(
                snapshot_id,
            )

        results = self._resolve_snapshot_items(
            page_items,
            user=user,
        )

        return {
            "results": results,
            "has_more": has_more,
            "next_cursor": next_cursor,
        }

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _community_post_queryset():
        """
        Shared queryset for published community posts.
        """
        return (
            CommunityPost.objects
            .filter(
                status=CommunityPost.Status.PUBLISHED,
            )
            .select_related(
                "user",
                "target",
                "target__song",
                "target__album",
                "target__artist",
            )
            .prefetch_related(
                "target__song__artists",
                "target__song__featured_artists",
                "target__song__genres",
                "target__song__provider_identities",
                "target__album__artists",
            )
        )

    @staticmethod
    def _editorial_article_queryset():
        """
        Shared queryset for published editorial articles.

        Articles do not need a song, artist, album, or genre
        relationship to qualify for the feed.
        """
        return (
            EditorialArticle.objects
            .filter(
                status=EditorialArticle.Status.PUBLISHED,
            )
            .select_related(
                "author",
                "song",
                "artist",
                "album",
            )
            .prefetch_related(
                "song__artists",
                "song__featured_artists",
                "song__genres",
                "song__provider_identities",
                "album__artists",
            )
        )

    # ------------------------------------------------------------------
    # Snapshot item resolution
    # ------------------------------------------------------------------

    def _resolve_snapshot_items(
        self,
        items: list[FeedSnapshotItem],
        *,
        user=None,
    ) -> list[FeedCandidate]:
        """
        Resolve both community and editorial snapshot references.

        Viewer-specific like and favorite states are recalculated
        for each page. Snapshot ordering remains unchanged.

        Deleted or unpublished objects are skipped.
        """
        if not items:
            return []

        post_ids = {
            item.object_id
            for item in items
            if item.content_type == "community_post"
        }

        article_ids = {
            item.object_id
            for item in items
            if item.content_type == "editorial"
        }

        posts_by_id = {}
        articles_by_id = {}

        # Resolve community posts.
        if post_ids:
            posts = (
                self._community_post_queryset()
                .filter(id__in=post_ids)
                .annotate(
                    favorites_count=Count(
                        "favorites",
                        distinct=True,
                    ),
                )
            )

            if (
                user is not None
                and user.is_authenticated
            ):
                liked_posts = CommunityPostLike.objects.filter(
                    user_id=user.id,
                    post_id=OuterRef("pk"),
                )

                favorited_posts = CommunityPostFavorite.objects.filter(
                    user_id=user.id,
                    post_id=OuterRef("pk"),
                )

                followed_author = UserFollow.objects.filter(
                    follower_id=user.id,
                    following_id=OuterRef("user_id"),
                )

                posts = posts.annotate(
                    is_liked=Exists(liked_posts),
                    is_favorited=Exists(favorited_posts),
                    author_is_following=Exists(followed_author),
                )
            else:
                posts = posts.annotate(
                    is_liked=Value(
                        False,
                        output_field=BooleanField(),
                    ),
                    is_favorited=Value(
                        False,
                        output_field=BooleanField(),
                    ),
                    author_is_following=Value(
                        False,
                        output_field=BooleanField(),
                    ),
                )

            for post in posts:
                post.user.is_following = bool(
                    post.author_is_following
                )

                posts_by_id[post.id] = post

        # Resolve editorial articles independently.
        if article_ids:
            articles = self._editorial_article_queryset().filter(
                id__in=article_ids,
            )

            if (
                user is not None
                and user.is_authenticated
            ):
                liked_articles = EditorialArticleLike.objects.filter(
                    user_id=user.id,
                    article_id=OuterRef("pk"),
                )

                favorited_articles = EditorialArticleFavorite.objects.filter(
                    user_id=user.id,
                    article_id=OuterRef("pk"),
                )

                articles = articles.annotate(
                    user_has_liked=Exists(liked_articles),
                    user_has_favorited=Exists(favorited_articles),
                )
            else:
                articles = articles.annotate(
                    user_has_liked=Value(
                        False,
                        output_field=BooleanField(),
                    ),
                    user_has_favorited=Value(
                        False,
                        output_field=BooleanField(),
                    ),
                )

            for article in articles:
                articles_by_id[article.id] = article

        # Reconstruct the original snapshot order.
        candidates = []

        for item in items:
            if item.content_type == "community_post":
                post = posts_by_id.get(item.object_id)

                if post is None:
                    continue

                candidates.append(
                    FeedCandidate(
                        content_type="community_post",
                        source=item.source,
                        object=post,
                        score=item.score,
                    )
                )

            elif item.content_type == "editorial":
                article = articles_by_id.get(item.object_id)

                if article is None:
                    continue

                candidates.append(
                    FeedCandidate(
                        content_type="editorial",
                        source=item.source,
                        object=article,
                        score=item.score,
                    )
                )

        return candidates

    # ------------------------------------------------------------------
    # Community candidate generation
    # ------------------------------------------------------------------

    def _generate_candidates(
        self,
        *,
        user,
        candidate_limit: int,
    ) -> list[FeedCandidate]:
        candidates: list[FeedCandidate] = []

        if user is not None and user.is_authenticated:
            candidates.extend(
                self._relationship_candidates(
                    user=user,
                    limit=candidate_limit,
                )
            )

        candidates.extend(
            self._community_candidates(
                limit=candidate_limit,
            )
        )

        return self._deduplicate_candidates(
            candidates=candidates,
            limit=candidate_limit,
        )

    def _community_candidates(
        self,
        *,
        limit: int,
    ) -> list[FeedCandidate]:
        posts = (
            self._community_post_queryset()
            .order_by("-created_at")[:limit]
        )

        return [
            FeedCandidate(
                content_type="community_post",
                source="recent",
                object=post,
            )
            for post in posts
        ]

    def _relationship_candidates(
        self,
        *,
        user,
        limit: int,
    ) -> list[FeedCandidate]:
        candidates: list[FeedCandidate] = []

        following_ids = set(
            UserFollow.objects
            .filter(
                follower_id=user.id,
            )
            .values_list(
                "following_id",
                flat=True,
            )
        )

        mutual_ids = self._get_mutual_user_ids(
            user_id=user.id,
            following_ids=following_ids,
        )

        relationship_user_ids = following_ids | mutual_ids

        if relationship_user_ids:
            posts = (
                self._community_post_queryset()
                .filter(
                    user_id__in=relationship_user_ids,
                )
                .order_by("-created_at")[:limit]
            )

            for post in posts:
                source = (
                    "mutual"
                    if post.user_id in mutual_ids
                    else "following"
                )

                candidates.append(
                    FeedCandidate(
                        content_type="community_post",
                        source=source,
                        object=post,
                    )
                )

        followed_artist_ids = set(
            ArtistFollow.objects
            .filter(
                user_id=user.id,
            )
            .values_list(
                "artist_id",
                flat=True,
            )
        )

        if followed_artist_ids:
            artist_posts = (
                self._community_post_queryset()
                .filter(
                    target__artist_id__in=followed_artist_ids,
                )
                .order_by("-created_at")[:limit]
            )

            song_posts = (
                self._community_post_queryset()
                .filter(
                    target__song__artists__id__in=followed_artist_ids,
                )
                .order_by("-created_at")[:limit]
            )

            album_posts = (
                self._community_post_queryset()
                .filter(
                    target__album__artists__id__in=followed_artist_ids,
                )
                .order_by("-created_at")[:limit]
            )

            for post in artist_posts:
                candidates.append(
                    FeedCandidate(
                        content_type="community_post",
                        source="followed_artist",
                        object=post,
                    )
                )

            for post in song_posts:
                candidates.append(
                    FeedCandidate(
                        content_type="community_post",
                        source="followed_artist",
                        object=post,
                    )
                )

            for post in album_posts:
                candidates.append(
                    FeedCandidate(
                        content_type="community_post",
                        source="followed_artist",
                        object=post,
                    )
                )

        interaction_since = timezone.now() - timedelta(
            days=self.INTERACTION_LOOKBACK_DAYS,
        )

        interacted_post_ids = set(
            MusicFeedInteraction.objects
            .filter(
                user=user,
                created_at__gte=interaction_since,
                community_post__isnull=False,
                interaction_type__in=[
                    MusicFeedInteraction.InteractionType.VIEW_COMMUNITY_POST,
                    MusicFeedInteraction.InteractionType.LIKE_COMMUNITY_POST,
                    MusicFeedInteraction.InteractionType.COMMENT_COMMUNITY_POST,
                    MusicFeedInteraction.InteractionType.FAVORITE_COMMUNITY_POST,
                ],
            )
            .order_by("-created_at")
            .values_list(
                "community_post_id",
                flat=True,
            )[: self.INTERACTION_LIMIT]
        )

        if interacted_post_ids:
            history_posts = (
                self._community_post_queryset()
                .filter(
                    id__in=interacted_post_ids,
                )
            )

            candidates.extend(
                FeedCandidate(
                    content_type="community_post",
                    source="history",
                    object=post,
                )
                for post in history_posts
            )

        return candidates

    # ------------------------------------------------------------------
    # Editorial candidate generation and ordering
    # ------------------------------------------------------------------

    def _generate_editorial_candidates(
        self,
        *,
        limit: int,
    ) -> list[FeedCandidate]:
        """
        Generate published editorial articles.

        Editorial ordering is independent of community engagement
        and personalization.

        Featured articles are placed before non-featured articles.
        Within each group, newer publication dates come first.

        No music relationship is required.
        """
        articles = (
            self._editorial_article_queryset()
            .order_by(
                "-is_featured",
                "-published_at",
                "-created_at",
                "-id",
            )[:limit]
        )

        candidates = []

        for article in articles:
            candidates.append(
                FeedCandidate(
                    content_type="editorial",
                    source="editorial",
                    object=article,
                )
            )

        return candidates

    # ------------------------------------------------------------------
    # Feed mixing
    # ------------------------------------------------------------------

    def _mix_feed_candidates(
        self,
        *,
        community_candidates: list[FeedCandidate],
        editorial_candidates: list[FeedCandidate],
    ) -> list[FeedCandidate]:
        """
        Mix community posts and editorial articles.

        The normal pattern is:

            10 community posts
            1 editorial article

        Consecutive editorial articles are prevented while
        community posts remain available.

        If the community pool is exhausted, remaining editorial
        articles fill the feed.

        If the editorial pool is exhausted, remaining community
        posts fill the feed.
        """
        mixed: list[FeedCandidate] = []

        community_index = 0
        editorial_index = 0

        while (
            community_index < len(community_candidates)
            or editorial_index < len(editorial_candidates)
        ):
            # Add up to ten community posts.
            community_batch_end = min(
                community_index + self.COMMUNITY_POSTS_PER_EDITORIAL,
                len(community_candidates),
            )

            while community_index < community_batch_end:
                mixed.append(
                    community_candidates[community_index]
                )
                community_index += 1

            # Add one editorial article after the community batch.
            if editorial_index < len(editorial_candidates):
                mixed.append(
                    editorial_candidates[editorial_index]
                )
                editorial_index += 1

            # If there are no more community posts, the next loop
            # will continue adding editorial articles in batches
            # of one. This is intentional: the remaining editorial
            # pool fills the available feed positions.
            if (
                community_index >= len(community_candidates)
                and editorial_index < len(editorial_candidates)
            ):
                mixed.extend(
                    editorial_candidates[editorial_index:]
                )
                break

        return mixed

    # ------------------------------------------------------------------
    # User context
    # ------------------------------------------------------------------

    def _build_user_context(
        self,
        *,
        user,
        candidates: list[FeedCandidate],
    ) -> FeedUserContext:
        if user is None or not user.is_authenticated:
            return self._empty_user_context()

        # Only community posts are considered here.
        community_candidates = [
            candidate
            for candidate in candidates
            if candidate.content_type == "community_post"
        ]

        following_user_ids = frozenset(
            UserFollow.objects
            .filter(
                follower_id=user.id,
            )
            .values_list(
                "following_id",
                flat=True,
            )
        )

        follower_user_ids = frozenset(
            UserFollow.objects
            .filter(
                following_id=user.id,
            )
            .values_list(
                "follower_id",
                flat=True,
            )
        )

        mutual_user_ids = frozenset(
            following_user_ids & follower_user_ids
        )

        followed_artist_ids = frozenset(
            ArtistFollow.objects
            .filter(
                user_id=user.id,
            )
            .values_list(
                "artist_id",
                flat=True,
            )
        )

        preferred_genre_ids = frozenset(
            user.music_genre_preferences.values_list(
                "genre_id",
                flat=True,
            )
        )

        interaction_since = timezone.now() - timedelta(
            days=self.INTERACTION_LOOKBACK_DAYS,
        )

        interactions = list(
            MusicFeedInteraction.objects
            .filter(
                user=user,
                created_at__gte=interaction_since,
            )
            .order_by("-created_at")
            .values(
                "interaction_type",
                "song_id",
                "album_id",
                "artist_id",
                "community_post_id",
            )[: self.INTERACTION_LIMIT]
        )

        interacted_song_ids = frozenset(
            item["song_id"]
            for item in interactions
            if item["song_id"] is not None
        )

        interacted_album_ids = frozenset(
            item["album_id"]
            for item in interactions
            if item["album_id"] is not None
        )

        interacted_artist_ids = frozenset(
            item["artist_id"]
            for item in interactions
            if item["artist_id"] is not None
        )

        interacted_community_post_ids = frozenset(
            item["community_post_id"]
            for item in interactions
            if (
                item["community_post_id"] is not None
                and item["interaction_type"] in {
                    MusicFeedInteraction.InteractionType.VIEW_COMMUNITY_POST,
                    MusicFeedInteraction.InteractionType.LIKE_COMMUNITY_POST,
                    MusicFeedInteraction.InteractionType.COMMENT_COMMUNITY_POST,
                    MusicFeedInteraction.InteractionType.FAVORITE_COMMUNITY_POST,
                }
            )
        )

        community_post_ids = {
            candidate.object_id
            for candidate in community_candidates
        }

        liked_post_ids = frozenset(
            CommunityPostLike.objects
            .filter(
                user_id=user.id,
                post_id__in=community_post_ids,
            )
            .values_list(
                "post_id",
                flat=True,
            )
        )

        favorited_post_ids = frozenset(
            CommunityPostFavorite.objects
            .filter(
                user_id=user.id,
                post_id__in=community_post_ids,
            )
            .values_list(
                "post_id",
                flat=True,
            )
        )

        commented_post_ids = frozenset(
            CommunityPostComment.objects
            .filter(
                user_id=user.id,
                post_id__in=community_post_ids,
                status=CommunityPostComment.Status.PUBLISHED,
            )
            .values_list(
                "post_id",
                flat=True,
            )
            .distinct()
        )

        comment_liked_post_ids = frozenset(
            CommunityPostCommentLike.objects
            .filter(
                user_id=user.id,
                comment__post_id__in=community_post_ids,
                comment__status=CommunityPostComment.Status.PUBLISHED,
            )
            .values_list(
                "comment__post_id",
                flat=True,
            )
            .distinct()
        )

        # Creator affinity is based exclusively on community-post
        # engagement.
        engaged_creator_ids = set(
            CommunityPostLike.objects
            .filter(user_id=user.id)
            .values_list(
                "post__user_id",
                flat=True,
            )
        )

        engaged_creator_ids.update(
            CommunityPostFavorite.objects
            .filter(user_id=user.id)
            .values_list(
                "post__user_id",
                flat=True,
            )
        )

        engaged_creator_ids.update(
            CommunityPostComment.objects
            .filter(
                user_id=user.id,
                status=CommunityPostComment.Status.PUBLISHED,
            )
            .values_list(
                "post__user_id",
                flat=True,
            )
        )

        engaged_creator_ids.update(
            CommunityPostCommentLike.objects
            .filter(
                user_id=user.id,
                comment__status=CommunityPostComment.Status.PUBLISHED,
            )
            .values_list(
                "comment__post__user_id",
                flat=True,
            )
        )

        return FeedUserContext(
            following_user_ids=following_user_ids,
            follower_user_ids=follower_user_ids,
            mutual_user_ids=mutual_user_ids,
            followed_artist_ids=followed_artist_ids,
            preferred_genre_ids=preferred_genre_ids,
            interacted_song_ids=interacted_song_ids,
            interacted_album_ids=interacted_album_ids,
            interacted_artist_ids=interacted_artist_ids,
            liked_community_post_ids=liked_post_ids,
            favorited_community_post_ids=favorited_post_ids,
            commented_community_post_ids=commented_post_ids,
            comment_liked_post_ids=comment_liked_post_ids,
            interacted_community_post_ids=interacted_community_post_ids,
            engaged_creator_ids=frozenset(engaged_creator_ids),
        )

    @staticmethod
    def _empty_user_context() -> FeedUserContext:
        empty = frozenset()

        return FeedUserContext(
            following_user_ids=empty,
            follower_user_ids=empty,
            mutual_user_ids=empty,
            followed_artist_ids=empty,
            preferred_genre_ids=empty,
            interacted_song_ids=empty,
            interacted_album_ids=empty,
            interacted_artist_ids=empty,
            liked_community_post_ids=empty,
            favorited_community_post_ids=empty,
            commented_community_post_ids=empty,
            comment_liked_post_ids=empty,
            interacted_community_post_ids=empty,
            engaged_creator_ids=empty,
        )

    @staticmethod
    def _get_mutual_user_ids(
        *,
        user_id: int,
        following_ids: set[int],
    ) -> set[int]:
        if not following_ids:
            return set()

        return set(
            UserFollow.objects
            .filter(
                following_id=user_id,
                follower_id__in=following_ids,
            )
            .values_list(
                "follower_id",
                flat=True,
            )
        )

    # ------------------------------------------------------------------
    # Community ranking
    # ------------------------------------------------------------------

    def _rank_candidates(
        self,
        *,
        candidates: list[FeedCandidate],
        context: FeedUserContext,
    ) -> list[FeedCandidate]:
        ranked = []

        for candidate in candidates:
            if candidate.content_type != "community_post":
                continue

            score = self._base_score(candidate)

            score += self._personalization_score(
                candidate=candidate,
                context=context,
            )

            ranked.append(
                FeedCandidate(
                    content_type=candidate.content_type,
                    source=candidate.source,
                    object=candidate.object,
                    score=score,
                )
            )

        ranked.sort(
            key=lambda candidate: (
                candidate.score,
                self._candidate_timestamp(candidate) is not None,
                (
                    self._candidate_timestamp(candidate).timestamp()
                    if self._candidate_timestamp(candidate) is not None
                    else float("-inf")
                ),
                candidate.object_id,
            ),
            reverse=True,
        )

        return ranked

    def _base_score(
        self,
        candidate: FeedCandidate,
    ) -> float:
        post = candidate.object
        score = 0.0

        timestamp = self._candidate_timestamp(candidate)

        if timestamp is not None:
            now = timezone.now()

            if timezone.is_naive(timestamp):
                timestamp = timezone.make_aware(
                    timestamp,
                    timezone.get_current_timezone(),
                )

            age_hours = max(
                0.0,
                (now - timestamp).total_seconds() / 3600,
            )

            score += max(
                0.0,
                40.0 - age_hours * 0.35,
            )

        score += min(
            float(post.likes_count) * 1.5,
            20.0,
        )

        score += min(
            float(post.comments_count) * 2.0,
            20.0,
        )

        score += min(
            float(post.views_count) * 0.05,
            10.0,
        )

        return score

    def _personalization_score(
        self,
        *,
        candidate: FeedCandidate,
        context: FeedUserContext,
    ) -> float:
        post = candidate.object
        score = 0.0

        if post.user_id in context.following_user_ids:
            score += 35.0

        if post.user_id in context.mutual_user_ids:
            score += 20.0

        if post.user_id in context.engaged_creator_ids:
            score += 12.0

        if post.id in context.liked_community_post_ids:
            score -= 25.0

        if post.id in context.favorited_community_post_ids:
            score -= 30.0

        if post.id in context.commented_community_post_ids:
            score -= 20.0

        if post.id in context.comment_liked_post_ids:
            score -= 8.0

        if post.id in context.interacted_community_post_ids:
            score -= 5.0

        target = getattr(
            post,
            "target",
            None,
        )

        if target is not None:
            score += self._target_personalization_score(
                target=target,
                context=context,
            )

        return score

    @staticmethod
    def _target_personalization_score(
        *,
        target,
        context: FeedUserContext,
    ) -> float:
        score = 0.0

        if target.song_id:
            if target.song_id in context.interacted_song_ids:
                score += 18.0

            song = getattr(
                target,
                "song",
                None,
            )

            if song is not None:
                score += MusicFeedService._artist_personalization_score(
                    artists=song.artists.all(),
                    context=context,
                )

                score += MusicFeedService._genre_personalization_score(
                    genres=song.genres.all(),
                    context=context,
                )

        if target.album_id:
            if target.album_id in context.interacted_album_ids:
                score += 20.0

            album = getattr(
                target,
                "album",
                None,
            )

            if album is not None:
                score += MusicFeedService._artist_personalization_score(
                    artists=album.artists.all(),
                    context=context,
                )

        if target.artist_id:
            if target.artist_id in context.followed_artist_ids:
                score += 28.0

            if target.artist_id in context.interacted_artist_ids:
                score += 20.0

        return score

    @staticmethod
    def _artist_personalization_score(
        *,
        artists,
        context: FeedUserContext,
    ) -> float:
        score = 0.0

        for artist in artists:
            if artist.id in context.followed_artist_ids:
                score += 28.0

            if artist.id in context.interacted_artist_ids:
                score += 20.0

        return score

    @staticmethod
    def _genre_personalization_score(
        *,
        genres,
        context: FeedUserContext,
    ) -> float:
        score = 0.0

        for genre in genres:
            if genre.id in context.preferred_genre_ids:
                score += 24.0

        return score

    # ------------------------------------------------------------------
    # Community diversity
    # ------------------------------------------------------------------

    def _select_diverse(
        self,
        *,
        candidates: list[FeedCandidate],
        limit: int,
    ) -> list[FeedCandidate]:
        """
        Prevent one creator or artist from dominating community posts.

        Editorial articles are not passed through this method.
        """
        selected: list[FeedCandidate] = []

        seen_post_ids: set[int] = set()
        recent_author_ids: list[int] = []
        recent_artist_ids: list[int] = []

        def violates_diversity(
            candidate: FeedCandidate,
            *,
            check_people: bool = True,
        ) -> bool:
            author_id = candidate.object.user_id
            artist_ids = self._candidate_artist_ids(candidate)

            if (
                check_people
                and recent_author_ids.count(author_id) >= 2
            ):
                return True

            if (
                check_people
                and any(
                    recent_artist_ids.count(artist_id) >= 2
                    for artist_id in artist_ids
                )
            ):
                return True

            return False

        def add_candidate(
            candidate: FeedCandidate,
        ) -> None:
            selected.append(candidate)
            seen_post_ids.add(candidate.object_id)

            recent_author_ids.append(
                candidate.object.user_id
            )

            recent_artist_ids.extend(
                self._candidate_artist_ids(candidate)
            )

        for candidate in candidates:
            if len(selected) >= limit:
                break

            if candidate.object_id in seen_post_ids:
                continue

            if violates_diversity(candidate):
                continue

            add_candidate(candidate)

        if len(selected) < limit:
            for candidate in candidates:
                if len(selected) >= limit:
                    break

                if candidate.object_id in seen_post_ids:
                    continue

                if violates_diversity(
                    candidate,
                    check_people=False,
                ):
                    continue

                add_candidate(candidate)

        return selected

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @classmethod
    def _deduplicate_candidates(
        cls,
        *,
        candidates: list[FeedCandidate],
        limit: int,
    ) -> list[FeedCandidate]:
        """
        Keep one candidate per content type and object ID.

        For community posts, the strongest relationship source wins.
        Editorial articles are also deduplicated independently.
        """
        deduplicated: list[FeedCandidate] = []
        index_by_key: dict[tuple[str, int], int] = {}

        for candidate in candidates:
            key = (
                candidate.content_type,
                candidate.object_id,
            )

            existing_index = index_by_key.get(key)

            if existing_index is None:
                index_by_key[key] = len(deduplicated)
                deduplicated.append(candidate)
                continue

            existing = deduplicated[existing_index]

            current_priority = cls.SOURCE_PRIORITY.get(
                candidate.source,
                0,
            )

            existing_priority = cls.SOURCE_PRIORITY.get(
                existing.source,
                0,
            )

            if current_priority > existing_priority:
                deduplicated[existing_index] = candidate

        return deduplicated[:limit]

    @staticmethod
    def _normalize_limit(
        limit: int,
    ) -> int:
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            return MusicFeedService.DEFAULT_LIMIT

        return max(
            1,
            min(
                limit,
                MusicFeedService.MAX_LIMIT,
            ),
        )

    @staticmethod
    def _candidate_artist_ids(
        candidate: FeedCandidate,
    ) -> set[int]:
        if candidate.content_type != "community_post":
            return set()

        target = getattr(
            candidate.object,
            "target",
            None,
        )

        if target is None:
            return set()

        artist_ids: set[int] = set()

        if target.artist_id:
            artist_ids.add(target.artist_id)

        song = getattr(
            target,
            "song",
            None,
        )

        if song is not None:
            artist_ids.update(
                artist.id
                for artist in song.artists.all()
            )

        album = getattr(
            target,
            "album",
            None,
        )

        if album is not None:
            artist_ids.update(
                artist.id
                for artist in album.artists.all()
            )

        return artist_ids

    @staticmethod
    def _candidate_timestamp(
        candidate: FeedCandidate,
    ) -> datetime | None:
        if candidate.content_type == "community_post":
            return candidate.object.created_at

        if candidate.content_type == "editorial":
            return candidate.object.published_at

        return None