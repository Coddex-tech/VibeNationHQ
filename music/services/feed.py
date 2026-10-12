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
    Album,
    Artist,
    CommunityPost,
    CommunityPostFavorite,
    CommunityPostLike,
    EditorialArticle,
    EditorialArticleLike,
    MusicFeedInteraction,
    Song,
    UserFollow,
)

from music.models import ArtistFollow

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
    liked_editorial_ids: frozenset[int]


class MusicFeedService:
    """
    Deterministic music feed engine for VibeNationHQ.

    The service is deliberately independent from the API layer so that
    ranking logic can evolve later without changing the public API.

    The current implementation uses bounded candidate generation,
    deterministic scoring, diversity rules, and cursor-based feed
    snapshots. It does not require ML.
    """

    DEFAULT_LIMIT = 20
    MAX_LIMIT = 50

    CANDIDATE_MULTIPLIER = 4
    MAX_CANDIDATES = 100

    INTERACTION_LOOKBACK_DAYS = 90
    INTERACTION_LIMIT = 500

    SOURCE_PRIORITY = {
        "mutual": 100,
        "following": 90,
        "followed_artist": 80,
        "history": 70,
        "featured": 60,
        "editorial": 50,
        "discovery": 40,
        "recent": 30,
    }

    def get_feed(
        self,
        *,
        user=None,
        limit: int = DEFAULT_LIMIT,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Return one page of the feed.

        A request without a cursor creates a new feed snapshot.

        Requests with a cursor continue through the existing snapshot
        without recalculating ranking or personalization.
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

        candidates = self._generate_candidates(
            user=user,
            candidate_limit=candidate_limit,
        )

        context = self._build_user_context(
            user=user,
            candidates=candidates,
        )

        ranked_candidates = self._rank_candidates(
            candidates=candidates,
            context=context,
        )

        ordered_candidates = self._select_diverse(
            candidates=ranked_candidates,
            limit=len(ranked_candidates),
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

    
    def _resolve_snapshot_items(
        self,
        items: list[FeedSnapshotItem],
        *,
        user=None,
    ) -> list[FeedCandidate]:
        """
        Resolve lightweight snapshot references back into model objects.

        Community posts are annotated with the current user's like,
        favorite, and author-following states.

        Community posts also receive their current total favorite count.

        Provider identities are prefetched for canonical song targets
        so CommunityPostTargetSerializer can resolve provider preview
        URLs without causing an additional query per post.
        """
        if not items:
            return []

        ids_by_type: dict[str, set[int]] = {}

        for item in items:
            ids_by_type.setdefault(
                item.content_type,
                set(),
            ).add(item.object_id)

        objects_by_key: dict[
            tuple[str, int],
            Any,
        ] = {}

        if ids_by_type.get("community_post"):
            posts = (
                CommunityPost.objects
                .filter(
                    id__in=ids_by_type["community_post"],
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

                favorited_posts = (
                    CommunityPostFavorite.objects.filter(
                        user_id=user.id,
                        post_id=OuterRef("pk"),
                    )
                )

                followed_author = UserFollow.objects.filter(
                    follower_id=user.id,
                    following_id=OuterRef("user_id"),
                )

                posts = posts.annotate(
                    is_liked=Exists(
                        liked_posts,
                    ),
                    is_favorited=Exists(
                        favorited_posts,
                    ),
                    author_is_following=Exists(
                        followed_author,
                    ),
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
                # CommunityUserSerializer reads this attribute
                # to serialize the current viewer's follow state.
                post.user.is_following = bool(
                    post.author_is_following
                )

                objects_by_key[
                    ("community_post", post.id)
                ] = post

        if ids_by_type.get("editorial"):
            articles = (
                EditorialArticle.objects
                .filter(
                    id__in=ids_by_type["editorial"],
                    status=EditorialArticle.Status.PUBLISHED,
                )
                .select_related(
                    "author",
                    "song",
                    "artist",
                    "album",
                )
                .prefetch_related(
                    "genres",
                    "song__artists",
                    "song__featured_artists",
                    "song__genres",
                    "album__artists",
                )
            )

            for article in articles:
                objects_by_key[
                    ("editorial", article.id)
                ] = article

        if ids_by_type.get("song"):
            songs = (
                Song.objects
                .filter(
                    id__in=ids_by_type["song"],
                    status=Song.Status.PUBLISHED,
                )
                .prefetch_related(
                    "artists",
                    "featured_artists",
                    "genres",
                )
            )

            for song in songs:
                objects_by_key[
                    ("song", song.id)
                ] = song

        if ids_by_type.get("album"):
            albums = (
                Album.objects
                .filter(
                    id__in=ids_by_type["album"],
                    status=Album.Status.PUBLISHED,
                )
                .prefetch_related(
                    "artists",
                )
            )

            for album in albums:
                objects_by_key[
                    ("album", album.id)
                ] = album

        if ids_by_type.get("artist"):
            artists = Artist.objects.filter(
                id__in=ids_by_type["artist"],
                is_active=True,
            )

            if (
                user is not None
                and user.is_authenticated
            ):
                followed_artist = ArtistFollow.objects.filter(
                    user_id=user.id,
                    artist_id=OuterRef("pk"),
                )

                artists = artists.annotate(
                    is_following=Exists(
                        followed_artist,
                    ),
                )
            else:
                artists = artists.annotate(
                    is_following=Value(
                        False,
                        output_field=BooleanField(),
                    ),
                )

            for artist in artists:
                objects_by_key[
                    ("artist", artist.id)
                ] = artist


        candidates: list[FeedCandidate] = []

        for item in items:
            obj = objects_by_key.get(
                (
                    item.content_type,
                    item.object_id,
                )
            )

            if obj is None:
                continue

            candidates.append(
                FeedCandidate(
                    content_type=item.content_type,
                    source=item.source,
                    object=obj,
                    score=item.score,
                )
            )

        return candidates


    # ------------------------------------------------------------------
    # Candidate generation
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

        candidates.extend(
            self._editorial_candidates(
                limit=candidate_limit,
            )
        )

        candidates.extend(
            self._song_candidates(
                limit=candidate_limit,
            )
        )

        candidates.extend(
            self._album_candidates(
                limit=candidate_limit,
            )
        )

        candidates.extend(
            self._artist_candidates(
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
        queryset = (
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
            .order_by("-created_at")
        )

        return [
            FeedCandidate(
                content_type="community_post",
                source="recent",
                object=post,
            )
            for post in queryset[:limit]
        ]

    def _editorial_candidates(
        self,
        *,
        limit: int,
    ) -> list[FeedCandidate]:
        queryset = (
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
                "genres",
                "song__artists",
                "song__featured_artists",
                "song__genres",
                "album__artists",
            )
            .order_by(
                "-is_featured",
                "-published_at",
            )
        )

        return [
            FeedCandidate(
                content_type="editorial",
                source=(
                    "featured"
                    if article.is_featured
                    else "editorial"
                ),
                object=article,
            )
            for article in queryset[:limit]
        ]

    def _song_candidates(
        self,
        *,
        limit: int,
    ) -> list[FeedCandidate]:
        queryset = (
            Song.objects
            .filter(
                status=Song.Status.PUBLISHED,
            )
            .prefetch_related(
                "artists",
                "featured_artists",
                "genres",
            )
            .order_by(
                "-is_featured",
                "-published_at",
                "-favorites_count",
            )
        )

        return [
            FeedCandidate(
                content_type="song",
                source=(
                    "featured"
                    if song.is_featured
                    else "discovery"
                ),
                object=song,
            )
            for song in queryset[:limit]
        ]

    def _album_candidates(
        self,
        *,
        limit: int,
    ) -> list[FeedCandidate]:
        queryset = (
            Album.objects
            .filter(
                status=Album.Status.PUBLISHED,
            )
            .prefetch_related(
                "artists",
            )
            .order_by(
                "-is_featured",
                "-published_at",
                "-favorites_count",
            )
        )

        return [
            FeedCandidate(
                content_type="album",
                source=(
                    "featured"
                    if album.is_featured
                    else "discovery"
                ),
                object=album,
            )
            for album in queryset[:limit]
        ]

    def _artist_candidates(
        self,
        *,
        limit: int,
    ) -> list[FeedCandidate]:
        queryset = Artist.objects.filter(
            is_active=True,
        ).order_by(
            "-is_verified",
            "-followers_count",
            "name",
        )

        return [
            FeedCandidate(
                content_type="artist",
                source="discovery",
                object=artist,
            )
            for artist in queryset[:limit]
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

        relationship_user_ids = (
            following_ids | mutual_ids
        )

        if relationship_user_ids:
            posts = (
                CommunityPost.objects
                .filter(
                    status=CommunityPost.Status.PUBLISHED,
                    user_id__in=relationship_user_ids,
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
            user.artist_follows.values_list(
                "artist_id",
                flat=True,
            )
        )

        if followed_artist_ids:
            songs = (
                Song.objects
                .filter(
                    status=Song.Status.PUBLISHED,
                    artists__id__in=followed_artist_ids,
                )
                .prefetch_related(
                    "artists",
                    "featured_artists",
                    "genres",
                )
                .distinct()
                .order_by(
                    "-published_at",
                    "-favorites_count",
                )[:limit]
            )

            candidates.extend(
                FeedCandidate(
                    content_type="song",
                    source="followed_artist",
                    object=song,
                )
                for song in songs
            )

            albums = (
                Album.objects
                .filter(
                    status=Album.Status.PUBLISHED,
                    artists__id__in=followed_artist_ids,
                )
                .prefetch_related(
                    "artists",
                )
                .distinct()
                .order_by(
                    "-published_at",
                    "-favorites_count",
                )[:limit]
            )

            candidates.extend(
                FeedCandidate(
                    content_type="album",
                    source="followed_artist",
                    object=album,
                )
                for album in albums
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
            )[: self.INTERACTION_LIMIT]
        )

        interacted_song_ids = {
            item["song_id"]
            for item in interactions
            if item["song_id"] is not None
        }

        interacted_album_ids = {
            item["album_id"]
            for item in interactions
            if item["album_id"] is not None
        }

        if interacted_song_ids:
            songs = (
                Song.objects
                .filter(
                    id__in=interacted_song_ids,
                    status=Song.Status.PUBLISHED,
                )
                .prefetch_related(
                    "artists",
                    "featured_artists",
                    "genres",
                )
            )

            candidates.extend(
                FeedCandidate(
                    content_type="song",
                    source="history",
                    object=song,
                )
                for song in songs
            )

        if interacted_album_ids:
            albums = (
                Album.objects
                .filter(
                    id__in=interacted_album_ids,
                    status=Album.Status.PUBLISHED,
                )
                .prefetch_related(
                    "artists",
                )
            )

            candidates.extend(
                FeedCandidate(
                    content_type="album",
                    source="history",
                    object=album,
                )
                for album in albums
            )

        return candidates

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
            return FeedUserContext(
                following_user_ids=frozenset(),
                follower_user_ids=frozenset(),
                mutual_user_ids=frozenset(),
                followed_artist_ids=frozenset(),
                preferred_genre_ids=frozenset(),
                interacted_song_ids=frozenset(),
                interacted_album_ids=frozenset(),
                interacted_artist_ids=frozenset(),
                liked_community_post_ids=frozenset(),
                liked_editorial_ids=frozenset(),
            )

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
            user.artist_follows.values_list(
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

        interactions = (
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

        community_post_ids = {
            candidate.object_id
            for candidate in candidates
            if candidate.content_type
            == "community_post"
        }

        editorial_ids = {
            candidate.object_id
            for candidate in candidates
            if candidate.content_type
            == "editorial"
        }

        liked_community_post_ids = frozenset(
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

        liked_editorial_ids = frozenset(
            EditorialArticleLike.objects
            .filter(
                user_id=user.id,
                article_id__in=editorial_ids,
            )
            .values_list(
                "article_id",
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
            liked_community_post_ids=liked_community_post_ids,
            liked_editorial_ids=liked_editorial_ids,
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
    # Ranking
    # ------------------------------------------------------------------

    def _rank_candidates(
        self,
        *,
        candidates: list[FeedCandidate],
        context: FeedUserContext,
    ) -> list[FeedCandidate]:
        ranked: list[FeedCandidate] = []

        for candidate in candidates:
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
                self._candidate_timestamp(candidate)
                is not None,
                (
                    self._candidate_timestamp(candidate).timestamp()
                    if self._candidate_timestamp(candidate)
                    is not None
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
        score = 0.0

        timestamp = self._candidate_timestamp(
            candidate,
        )

        if timestamp is not None:
            now = timezone.now()

            if timezone.is_naive(timestamp):
                timestamp = timezone.make_aware(
                    timestamp,
                    timezone.get_current_timezone(),
                )

            age_hours = max(
                0.0,
                (
                    now - timestamp
                ).total_seconds() / 3600,
            )

            score += max(
                0.0,
                40.0 - age_hours * 0.35,
            )

        obj = candidate.object

        if candidate.content_type == "community_post":
            score += min(
                float(
                    getattr(
                        obj,
                        "likes_count",
                        0,
                    )
                ) * 1.5,
                20.0,
            )

            score += min(
                float(
                    getattr(
                        obj,
                        "comments_count",
                        0,
                    )
                ) * 2.0,
                20.0,
            )

            score += min(
                float(
                    getattr(
                        obj,
                        "views_count",
                        0,
                    )
                ) * 0.05,
                10.0,
            )

        elif candidate.content_type == "editorial":
            score += min(
                float(
                    getattr(
                        obj,
                        "likes_count",
                        0,
                    )
                ) * 1.2,
                15.0,
            )

            score += min(
                float(
                    getattr(
                        obj,
                        "comments_count",
                        0,
                    )
                ) * 1.5,
                15.0,
            )

            score += min(
                float(
                    getattr(
                        obj,
                        "views_count",
                        0,
                    )
                ) * 0.03,
                10.0,
            )

            if getattr(
                obj,
                "is_featured",
                False,
            ):
                score += 12.0

        elif candidate.content_type == "song":
            score += min(
                float(
                    getattr(
                        obj,
                        "favorites_count",
                        0,
                    )
                ) * 1.5,
                20.0,
            )

            score += min(
                float(
                    getattr(
                        obj,
                        "ratings_count",
                        0,
                    )
                ) * 0.5,
                10.0,
            )

            if getattr(
                obj,
                "is_featured",
                False,
            ):
                score += 12.0

        elif candidate.content_type == "album":
            score += min(
                float(
                    getattr(
                        obj,
                        "favorites_count",
                        0,
                    )
                ) * 1.5,
                20.0,
            )

            score += min(
                float(
                    getattr(
                        obj,
                        "ratings_count",
                        0,
                    )
                ) * 0.5,
                10.0,
            )

            if getattr(
                obj,
                "is_featured",
                False,
            ):
                score += 12.0

        elif candidate.content_type == "artist":
            score += min(
                float(
                    getattr(
                        obj,
                        "followers_count",
                        0,
                    )
                ) * 0.5,
                20.0,
            )

            if getattr(
                obj,
                "is_verified",
                False,
            ):
                score += 8.0

        return score

    def _personalization_score(
        self,
        *,
        candidate: FeedCandidate,
        context: FeedUserContext,
    ) -> float:
        score = 0.0

        if candidate.content_type == "community_post":
            post = candidate.object

            if post.user_id in context.following_user_ids:
                score += 35.0

            if post.user_id in context.mutual_user_ids:
                score += 20.0

            if post.id in context.liked_community_post_ids:
                score -= 20.0

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

        elif candidate.content_type == "editorial":
            article = candidate.object

            if article.id in context.liked_editorial_ids:
                score -= 20.0

            if (
                article.artist_id
                and article.artist_id
                in context.followed_artist_ids
            ):
                score += 28.0

            if (
                article.song_id
                and article.song_id
                in context.interacted_song_ids
            ):
                score += 18.0

            if (
                article.album_id
                and article.album_id
                in context.interacted_album_ids
            ):
                score += 20.0

            if (
                article.artist_id
                and article.artist_id
                in context.interacted_artist_ids
            ):
                score += 20.0

            score += self._genre_personalization_score(
                genres=article.genres.all(),
                context=context,
            )

        elif candidate.content_type == "song":
            song = candidate.object

            if song.id in context.interacted_song_ids:
                score += 18.0

            score += self._artist_personalization_score(
                artists=song.artists.all(),
                context=context,
            )

            score += self._genre_personalization_score(
                genres=song.genres.all(),
                context=context,
            )

        elif candidate.content_type == "album":
            album = candidate.object

            if album.id in context.interacted_album_ids:
                score += 20.0

            score += self._artist_personalization_score(
                artists=album.artists.all(),
                context=context,
            )

        elif candidate.content_type == "artist":
            artist = candidate.object

            if artist.id in context.followed_artist_ids:
                score -= 8.0

            if artist.id in context.interacted_artist_ids:
                score += 20.0

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
                score += (
                    MusicFeedService
                    ._artist_personalization_score(
                        artists=song.artists.all(),
                        context=context,
                    )
                )

                score += (
                    MusicFeedService
                    ._genre_personalization_score(
                        genres=song.genres.all(),
                        context=context,
                    )
                )

        if target.album_id:
            if target.album_id in context.interacted_album_ids:
                score += 20.0

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
    # Diversity
    # ------------------------------------------------------------------

    def _select_diverse(
        self,
        *,
        candidates: list[FeedCandidate],
        limit: int,
    ) -> list[FeedCandidate]:
        selected: list[FeedCandidate] = []

        seen_keys: set[tuple[str, int]] = set()
        recent_author_ids: list[int] = []
        recent_artist_ids: list[int] = []
        recent_content_types: list[str] = []

        def violates_diversity(
            candidate: FeedCandidate,
            *,
            check_people: bool = True,
        ) -> bool:
            author_id = self._candidate_author_id(
                candidate,
            )

            artist_ids = self._candidate_artist_ids(
                candidate,
            )

            if (
                check_people
                and author_id is not None
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

            if (
                len(recent_content_types) >= 2
                and recent_content_types[-1]
                == candidate.content_type
                and recent_content_types[-2]
                == candidate.content_type
            ):
                return True

            return False

        def add_candidate(
            candidate: FeedCandidate,
        ) -> None:
            selected.append(candidate)

            seen_keys.add(
                (
                    candidate.content_type,
                    candidate.object_id,
                )
            )

            author_id = self._candidate_author_id(
                candidate,
            )

            if author_id is not None:
                recent_author_ids.append(
                    author_id,
                )

            recent_artist_ids.extend(
                self._candidate_artist_ids(
                    candidate,
                )
            )

            recent_content_types.append(
                candidate.content_type,
            )

        for candidate in candidates:
            if len(selected) >= limit:
                break

            key = (
                candidate.content_type,
                candidate.object_id,
            )

            if key in seen_keys:
                continue

            if violates_diversity(candidate):
                continue

            add_candidate(candidate)

        if len(selected) < limit:
            for candidate in candidates:
                if len(selected) >= limit:
                    break

                key = (
                    candidate.content_type,
                    candidate.object_id,
                )

                if key in seen_keys:
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
        Deduplicate candidates while preserving the strongest source.

        A single object can be discovered through several paths:

        - recent
        - discovery
        - history
        - followed_artist
        - following
        - mutual

        The strongest relationship source should win because the source
        is part of the feed's semantic metadata.
        """
        deduplicated: list[FeedCandidate] = []
        index_by_key: dict[
            tuple[str, int],
            int,
        ] = {}

        for candidate in candidates:
            key = (
                candidate.content_type,
                candidate.object_id,
            )

            existing_index = index_by_key.get(key)

            if existing_index is None:
                index_by_key[key] = len(
                    deduplicated,
                )
                deduplicated.append(candidate)
                continue

            existing = deduplicated[
                existing_index
            ]

            current_priority = cls.SOURCE_PRIORITY.get(
                candidate.source,
                0,
            )

            existing_priority = cls.SOURCE_PRIORITY.get(
                existing.source,
                0,
            )

            if current_priority > existing_priority:
                deduplicated[
                    existing_index
                ] = candidate

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
    def _candidate_author_id(
        candidate: FeedCandidate,
    ) -> int | None:
        if candidate.content_type == "community_post":
            return candidate.object.user_id

        if candidate.content_type == "editorial":
            return candidate.object.author_id

        return None

    @staticmethod
    def _candidate_artist_ids(
        candidate: FeedCandidate,
    ) -> set[int]:
        if candidate.content_type == "song":
            return {
                artist.id
                for artist in candidate.object.artists.all()
            }

        if candidate.content_type == "album":
            return {
                artist.id
                for artist in candidate.object.artists.all()
            }

        if candidate.content_type == "artist":
            return {
                candidate.object.id,
            }

        if candidate.content_type == "editorial":
            artist_ids: set[int] = set()

            if candidate.object.artist_id:
                artist_ids.add(
                    candidate.object.artist_id,
                )

            song = getattr(
                candidate.object,
                "song",
                None,
            )

            if song is not None:
                artist_ids.update(
                    artist.id
                    for artist in song.artists.all()
                )

            album = getattr(
                candidate.object,
                "album",
                None,
            )

            if album is not None:
                artist_ids.update(
                    artist.id
                    for artist in album.artists.all()
                )

            return artist_ids

        if candidate.content_type == "community_post":
            target = getattr(
                candidate.object,
                "target",
                None,
            )

            if target is None:
                return set()

            artist_ids: set[int] = set()

            if target.artist_id:
                artist_ids.add(
                    target.artist_id,
                )

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

        return set()

    @staticmethod
    def _candidate_timestamp(
        candidate: FeedCandidate,
    ) -> datetime | None:
        obj = candidate.object

        if candidate.content_type == "community_post":
            return obj.created_at

        if candidate.content_type == "editorial":
            return (
                obj.published_at
                or obj.created_at
            )

        if candidate.content_type == "song":
            return obj.published_at

        if candidate.content_type == "album":
            return obj.published_at

        return None