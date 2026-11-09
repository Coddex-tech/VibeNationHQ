
from datetime import timedelta
from decimal import Decimal

from django.db.models import (
    Avg,
    BigIntegerField,
    Count,
    DecimalField,
    F,
    OuterRef,
    Q,
    Subquery,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce
from django.utils import timezone

from music.models import (
    Album,
    Artist,
    ArtistFollow,
    CommunityPost,
    CommunityPostFavorite,
    CommunityPostLike,
    CommunityPostTarget,
    ContentDailyView,
    EditorialArticle,
    Song,
)


class DiscoveryService:
    """
    Business logic for VibeNationHQ music discovery.

    Song and album ratings come exclusively from rated community
    posts attached to their exact canonical targets.

    Trending may include draft catalog entries, but engagement
    must come from published community posts or published
    editorial articles.

    Most Favorited and Top Rated include draft and published
    catalog entries, but exclude archived entries.

    This service never changes publication status.
    """

    RESULT_LIMIT = 10
    TRENDING_DAYS = 7

    # Top Rated eligibility thresholds.
    MIN_RATINGS_FOR_TOP_RATED = 1
    MIN_AVERAGE_RATING_FOR_TOP_RATED = Decimal("4.0")

    # ========================================================
    # SHARED HELPERS
    # ========================================================

    @classmethod
    def _trending_window(cls):
        """
        Return the timestamp cutoff and daily-view date cutoff.

        Engagement rows use an exact rolling seven-day window.
        Daily views use the current local date and six preceding
        dates because ContentDailyView stores a DateField.
        """
        now = timezone.now()
        since = now - timedelta(days=cls.TRENDING_DAYS)
        since_date = (
            timezone.localdate(now)
            - timedelta(days=cls.TRENDING_DAYS - 1)
        )
        return since, since_date

    @staticmethod
    def _daily_views_subquery(*, since_date, filters, group_by):
        """Sum daily views for one correlated catalog item."""
        return (
            ContentDailyView.objects
            .filter(date__gte=since_date, **filters)
            .order_by()
            .values(group_by)
            .annotate(total=Sum("views_count"))
            .values("total")[:1]
        )

    @staticmethod
    def _count_subquery(*, model, filters, group_by):
        """
        Count matching rows for one correlated catalog item.

        Independent subqueries avoid multiplying engagement
        counts when multiple relationships are joined.
        """
        return (
            model.objects
            .filter(**filters)
            .order_by()
            .values(group_by)
            .annotate(total=Count("pk"))
            .values("total")[:1]
        )

    @staticmethod
    def _total_count_subquery(*, model, filters):
        """Count matching rows in a correlated scalar subquery."""
        return (
            model.objects
            .filter(**filters)
            .order_by()
            .values(_aggregate_group=Value(1))
            .annotate(total=Count("pk"))
            .values("total")[:1]
        )

    @staticmethod
    def _total_sum_subquery(*, model, filters, field):
        """Sum a field across matching rows in a scalar subquery."""
        return (
            model.objects
            .filter(**filters)
            .order_by()
            .values(_aggregate_group=Value(1))
            .annotate(total=Sum(field))
            .values("total")[:1]
        )

    @staticmethod
    def _integer_subquery(subquery):
        """Return an integer aggregate, defaulting to zero."""
        return Coalesce(
            Subquery(
                subquery,
                output_field=BigIntegerField(),
            ),
            Value(0),
            output_field=BigIntegerField(),
        )

    @classmethod
    def _daily_view_expression(
        cls,
        *,
        since_date,
        filters,
        group_by,
    ):
        return cls._integer_subquery(
            cls._daily_views_subquery(
                since_date=since_date,
                filters=filters,
                group_by=group_by,
            )
        )

    @classmethod
    def _recent_count_expression(
        cls,
        *,
        model,
        filters,
        group_by,
    ):
        return cls._integer_subquery(
            cls._count_subquery(
                model=model,
                filters=filters,
                group_by=group_by,
            )
        )

    @classmethod
    def _community_rating_count_expression(
        cls,
        *,
        target_type,
        target_field,
        recent_since=None,
    ):
        """
        Count rated, published community posts for one exact
        canonical song or album.

        When recent_since is provided, count only posts created
        within that rolling time window.

        This deliberately does not use Song.ratings_count or
        Album.ratings_count, which were maintained by the
        retired personal-rating system.
        """
        filters = {
            "target_type": target_type,
            target_field: OuterRef("pk"),
            "post__status": CommunityPost.Status.PUBLISHED,
            "post__rating__isnull": False,
        }

        if recent_since is not None:
            filters["post__created_at__gte"] = recent_since

        return cls._integer_subquery(
            cls._count_subquery(
                model=CommunityPostTarget,
                filters=filters,
                group_by=target_field,
            )
        )

    # ========================================================
    # TRENDING SONGS
    # ========================================================

    @classmethod
    def trending_songs(cls):
        since, since_date = cls._trending_window()

        community_views = cls._daily_view_expression(
            since_date=since_date,
            filters={
                "community_post__status": CommunityPost.Status.PUBLISHED,
                "community_post__target__target_type": (
                    CommunityPostTarget.TargetType.SONG
                ),
                "community_post__target__song_id": OuterRef("pk"),
            },
            group_by="community_post__target__song_id",
        )

        editorial_views = cls._daily_view_expression(
            since_date=since_date,
            filters={
                "editorial_article__status": (
                    EditorialArticle.Status.PUBLISHED
                ),
                "editorial_article__song_id": OuterRef("pk"),
            },
            group_by="editorial_article__song_id",
        )

        recent_likes = cls._recent_count_expression(
            model=CommunityPostLike,
            filters={
                "created_at__gte": since,
                "post__status": CommunityPost.Status.PUBLISHED,
                "post__target__target_type": (
                    CommunityPostTarget.TargetType.SONG
                ),
                "post__target__song_id": OuterRef("pk"),
            },
            group_by="post__target__song_id",
        )

        recent_post_favorites = cls._recent_count_expression(
            model=CommunityPostFavorite,
            filters={
                "created_at__gte": since,
                "post__status": CommunityPost.Status.PUBLISHED,
                "post__target__target_type": (
                    CommunityPostTarget.TargetType.SONG
                ),
                "post__target__song_id": OuterRef("pk"),
            },
            group_by="post__target__song_id",
        )

        recent_ratings = cls._community_rating_count_expression(
            target_type=CommunityPostTarget.TargetType.SONG,
            target_field="song_id",
            recent_since=since,
        )

        recent_discussions = cls._recent_count_expression(
            model=CommunityPostTarget,
            filters={
                "target_type": CommunityPostTarget.TargetType.SONG,
                "post__status": CommunityPost.Status.PUBLISHED,
                "post__created_at__gte": since,
                "song_id": OuterRef("pk"),
            },
            group_by="song_id",
        )

        community_rating_count = (
            cls._community_rating_count_expression(
                target_type=CommunityPostTarget.TargetType.SONG,
                target_field="song_id",
            )
        )

        return (
            Song.objects
            # Draft catalog entries may qualify for Trending.
            .annotate(
                recent_community_views=community_views,
                recent_editorial_views=editorial_views,
                recent_likes=recent_likes,
                recent_post_favorites=recent_post_favorites,
                recent_ratings=recent_ratings,
                recent_discussions=recent_discussions,
                community_rating_count=community_rating_count,
            )
            .annotate(
                recent_views=(
                    F("recent_community_views")
                    + F("recent_editorial_views")
                ),
            )
            .filter(
                Q(recent_views__gt=0)
                | Q(recent_likes__gt=0)
                | Q(recent_post_favorites__gt=0)
                | Q(recent_ratings__gt=0)
                | Q(recent_discussions__gt=0)
            )
            .select_related("album")
            .prefetch_related("artists", "featured_artists")
            .order_by(
                "-recent_views",
                "-recent_likes",
                "-recent_post_favorites",
                "-recent_discussions",
                "-recent_ratings",
                "-community_rating_count",
                "-published_at",
                "-pk",
            )[:cls.RESULT_LIMIT]
        )

    # ========================================================
    # TRENDING ALBUMS
    # ========================================================

    @classmethod
    def trending_albums(cls):
        since, since_date = cls._trending_window()

        community_views = cls._daily_view_expression(
            since_date=since_date,
            filters={
                "community_post__status": CommunityPost.Status.PUBLISHED,
                "community_post__target__target_type": (
                    CommunityPostTarget.TargetType.ALBUM
                ),
                "community_post__target__album_id": OuterRef("pk"),
            },
            group_by="community_post__target__album_id",
        )

        editorial_views = cls._daily_view_expression(
            since_date=since_date,
            filters={
                "editorial_article__status": (
                    EditorialArticle.Status.PUBLISHED
                ),
                "editorial_article__album_id": OuterRef("pk"),
            },
            group_by="editorial_article__album_id",
        )

        recent_likes = cls._recent_count_expression(
            model=CommunityPostLike,
            filters={
                "created_at__gte": since,
                "post__status": CommunityPost.Status.PUBLISHED,
                "post__target__target_type": (
                    CommunityPostTarget.TargetType.ALBUM
                ),
                "post__target__album_id": OuterRef("pk"),
            },
            group_by="post__target__album_id",
        )

        recent_post_favorites = cls._recent_count_expression(
            model=CommunityPostFavorite,
            filters={
                "created_at__gte": since,
                "post__status": CommunityPost.Status.PUBLISHED,
                "post__target__target_type": (
                    CommunityPostTarget.TargetType.ALBUM
                ),
                "post__target__album_id": OuterRef("pk"),
            },
            group_by="post__target__album_id",
        )

        recent_ratings = cls._community_rating_count_expression(
            target_type=CommunityPostTarget.TargetType.ALBUM,
            target_field="album_id",
            recent_since=since,
        )

        recent_discussions = cls._recent_count_expression(
            model=CommunityPostTarget,
            filters={
                "target_type": CommunityPostTarget.TargetType.ALBUM,
                "post__status": CommunityPost.Status.PUBLISHED,
                "post__created_at__gte": since,
                "album_id": OuterRef("pk"),
            },
            group_by="album_id",
        )

        community_rating_count = (
            cls._community_rating_count_expression(
                target_type=CommunityPostTarget.TargetType.ALBUM,
                target_field="album_id",
            )
        )

        return (
            Album.objects
            # Draft catalog entries may qualify for Trending.
            .annotate(
                recent_community_views=community_views,
                recent_editorial_views=editorial_views,
                recent_likes=recent_likes,
                recent_post_favorites=recent_post_favorites,
                recent_ratings=recent_ratings,
                recent_discussions=recent_discussions,
                community_rating_count=community_rating_count,
            )
            .annotate(
                recent_views=(
                    F("recent_community_views")
                    + F("recent_editorial_views")
                ),
            )
            .filter(
                Q(recent_views__gt=0)
                | Q(recent_likes__gt=0)
                | Q(recent_post_favorites__gt=0)
                | Q(recent_ratings__gt=0)
                | Q(recent_discussions__gt=0)
            )
            .prefetch_related("artists")
            .order_by(
                "-recent_views",
                "-recent_likes",
                "-recent_post_favorites",
                "-recent_discussions",
                "-recent_ratings",
                "-community_rating_count",
                "-release_date",
                "-published_at",
                "-pk",
            )[:cls.RESULT_LIMIT]
        )

    # ========================================================
    # TRENDING ARTISTS
    # ========================================================

    @classmethod
    def trending_artists(cls):
        since, since_date = cls._trending_window()

        # A community post targets only one catalog entity.
        # DISTINCT prevents a post being counted more than once
        # per artist through main-artist and featured-artist links.
        related_community_post_ids = (
            CommunityPostTarget.objects
            .filter(post__status=CommunityPost.Status.PUBLISHED)
            .filter(
                Q(artist_id=OuterRef("pk"))
                | Q(song__artists__pk=OuterRef("pk"))
                | Q(song__featured_artists__pk=OuterRef("pk"))
                | Q(album__artists__pk=OuterRef("pk"))
            )
            .order_by()
            .values("post_id")
            .distinct()
        )

        recent_community_views = cls._total_sum_subquery(
            model=ContentDailyView,
            filters={
                "date__gte": since_date,
                "community_post__status": CommunityPost.Status.PUBLISHED,
                "community_post_id__in": Subquery(
                    related_community_post_ids,
                ),
            },
            field="views_count",
        )

        # DISTINCT article IDs prevent an article linked to an
        # artist, song, and album from being counted repeatedly.
        related_editorial_article_ids = (
            EditorialArticle.objects
            .filter(status=EditorialArticle.Status.PUBLISHED)
            .filter(
                Q(artist_id=OuterRef("pk"))
                | Q(song__artists__pk=OuterRef("pk"))
                | Q(song__featured_artists__pk=OuterRef("pk"))
                | Q(album__artists__pk=OuterRef("pk"))
            )
            .order_by()
            .values("pk")
            .distinct()
        )

        recent_editorial_views = cls._total_sum_subquery(
            model=ContentDailyView,
            filters={
                "date__gte": since_date,
                "editorial_article__status": (
                    EditorialArticle.Status.PUBLISHED
                ),
                "editorial_article_id__in": Subquery(
                    related_editorial_article_ids,
                ),
            },
            field="views_count",
        )

        recent_likes = cls._total_count_subquery(
            model=CommunityPostLike,
            filters={
                "created_at__gte": since,
                "post__status": CommunityPost.Status.PUBLISHED,
                "post_id__in": Subquery(related_community_post_ids),
            },
        )

        recent_post_favorites = cls._total_count_subquery(
            model=CommunityPostFavorite,
            filters={
                "created_at__gte": since,
                "post__status": CommunityPost.Status.PUBLISHED,
                "post_id__in": Subquery(related_community_post_ids),
            },
        )

        recent_follows = cls._recent_count_expression(
            model=ArtistFollow,
            filters={
                "created_at__gte": since,
                "artist_id": OuterRef("pk"),
            },
            group_by="artist_id",
        )

        recent_songs = cls._recent_count_expression(
            model=Song,
            filters={
                "status": Song.Status.PUBLISHED,
                "published_at__gte": since,
                "artists__pk": OuterRef("pk"),
            },
            group_by="artists__pk",
        )

        recent_albums = cls._recent_count_expression(
            model=Album,
            filters={
                "status": Album.Status.PUBLISHED,
                "published_at__gte": since,
                "artists__pk": OuterRef("pk"),
            },
            group_by="artists__pk",
        )

        return (
            Artist.objects
            # Draft or inactive artists may qualify for Trending.
            # Featured Artists retains stricter eligibility.
            .annotate(
                recent_community_views=cls._integer_subquery(
                    recent_community_views,
                ),
                recent_editorial_views=cls._integer_subquery(
                    recent_editorial_views,
                ),
                recent_likes=cls._integer_subquery(recent_likes),
                recent_post_favorites=cls._integer_subquery(
                    recent_post_favorites,
                ),
                recent_follows=recent_follows,
                recent_songs=recent_songs,
                recent_albums=recent_albums,
            )
            .annotate(
                recent_views=(
                    F("recent_community_views")
                    + F("recent_editorial_views")
                ),
            )
            .filter(
                Q(recent_views__gt=0)
                | Q(recent_likes__gt=0)
                | Q(recent_post_favorites__gt=0)
                | Q(recent_follows__gt=0)
                | Q(recent_songs__gt=0)
                | Q(recent_albums__gt=0)
            )
            .order_by(
                "-recent_views",
                "-recent_likes",
                "-recent_post_favorites",
                "-recent_follows",
                "-recent_songs",
                "-recent_albums",
                "-followers_count",
                "name",
                "pk",
            )[:cls.RESULT_LIMIT]
        )

    # ========================================================
    # MOST DISCUSSED
    # ========================================================

    @classmethod
    def most_discussed_songs(cls):
        community_rating_count = (
            cls._community_rating_count_expression(
                target_type=CommunityPostTarget.TargetType.SONG,
                target_field="song_id",
            )
        )

        return (
            Song.objects
            .filter(status=Song.Status.PUBLISHED)
            .annotate(
                discussion_count=Count(
                    "community_post_targets__post",
                    filter=Q(
                        community_post_targets__post__status=(
                            CommunityPost.Status.PUBLISHED
                        ),
                    ),
                    distinct=True,
                ),
                community_rating_count=community_rating_count,
            )
            .filter(discussion_count__gt=0)
            .prefetch_related("artists", "featured_artists")
            .order_by(
                "-discussion_count",
                "-favorites_count",
                "-community_rating_count",
                "-published_at",
                "-pk",
            )[:cls.RESULT_LIMIT]
        )

    @classmethod
    def most_discussed_albums(cls):
        community_rating_count = (
            cls._community_rating_count_expression(
                target_type=CommunityPostTarget.TargetType.ALBUM,
                target_field="album_id",
            )
        )

        return (
            Album.objects
            .filter(status=Album.Status.PUBLISHED)
            .annotate(
                discussion_count=Count(
                    "community_post_targets__post",
                    filter=Q(
                        community_post_targets__post__status=(
                            CommunityPost.Status.PUBLISHED
                        ),
                    ),
                    distinct=True,
                ),
                community_rating_count=community_rating_count,
            )
            .filter(discussion_count__gt=0)
            .prefetch_related("artists")
            .order_by(
                "-discussion_count",
                "-favorites_count",
                "-community_rating_count",
                "-release_date",
                "-published_at",
                "-pk",
            )[:cls.RESULT_LIMIT]
        )

    # ========================================================
    # MOST FAVORITED
    # ========================================================

    @classmethod
    def most_favorited_songs(cls):
        community_post_favorites = cls._integer_subquery(
            cls._count_subquery(
                model=CommunityPostFavorite,
                filters={
                    "post__status": CommunityPost.Status.PUBLISHED,
                    "post__target__target_type": (
                        CommunityPostTarget.TargetType.SONG
                    ),
                    "post__target__song_id": OuterRef("pk"),
                },
                group_by="post__target__song_id",
            )
        )

        community_rating_count = (
            cls._community_rating_count_expression(
                target_type=CommunityPostTarget.TargetType.SONG,
                target_field="song_id",
            )
        )

        return (
            Song.objects
            # Imported catalog entries may remain drafts.
            # Exclude archived songs, but allow drafts and published.
            .exclude(status=Song.Status.ARCHIVED)
            .annotate(
                favorite_count=community_post_favorites,
                community_rating_count=community_rating_count,
            )
            .filter(favorite_count__gt=0)
            .prefetch_related("artists", "featured_artists")
            .order_by(
                "-favorite_count",
                "-community_rating_count",
                "-published_at",
                "-pk",
            )[:cls.RESULT_LIMIT]
        )

    @classmethod
    def most_favorited_albums(cls):
        community_post_favorites = cls._integer_subquery(
            cls._count_subquery(
                model=CommunityPostFavorite,
                filters={
                    "post__status": CommunityPost.Status.PUBLISHED,
                    "post__target__target_type": (
                        CommunityPostTarget.TargetType.ALBUM
                    ),
                    "post__target__album_id": OuterRef("pk"),
                },
                group_by="post__target__album_id",
            )
        )

        community_rating_count = (
            cls._community_rating_count_expression(
                target_type=CommunityPostTarget.TargetType.ALBUM,
                target_field="album_id",
            )
        )

        return (
            Album.objects
            # Imported catalog entries may remain drafts.
            # Exclude archived albums, but allow drafts and published.
            .exclude(status=Album.Status.ARCHIVED)
            .annotate(
                favorite_count=community_post_favorites,
                community_rating_count=community_rating_count,
            )
            .filter(favorite_count__gt=0)
            .prefetch_related("artists")
            .order_by(
                "-favorite_count",
                "-community_rating_count",
                "-release_date",
                "-published_at",
                "-pk",
            )[:cls.RESULT_LIMIT]
        )

    # ========================================================
    # TOP RATED
    # ========================================================

    @classmethod
    def top_rated_songs(cls):
        average_rating_subquery = (
            CommunityPostTarget.objects
            .filter(
                target_type=CommunityPostTarget.TargetType.SONG,
                song_id=OuterRef("pk"),
                post__status=CommunityPost.Status.PUBLISHED,
                post__rating__isnull=False,
            )
            .order_by()
            .values("song_id")
            .annotate(
                average=Avg("post__rating"),
            )
            .values("average")[:1]
        )

        rating_count_subquery = cls._count_subquery(
            model=CommunityPostTarget,
            filters={
                "target_type": CommunityPostTarget.TargetType.SONG,
                "song_id": OuterRef("pk"),
                "post__status": CommunityPost.Status.PUBLISHED,
                "post__rating__isnull": False,
            },
            group_by="song_id",
        )

        return (
            Song.objects
            # Include draft imports, but exclude archived songs.
            .exclude(status=Song.Status.ARCHIVED)
            .annotate(
                average_rating=Subquery(
                    average_rating_subquery,
                    output_field=DecimalField(
                        max_digits=3,
                        decimal_places=2,
                    ),
                ),
                rating_count=cls._integer_subquery(
                    rating_count_subquery,
                ),
            )
            .filter(
                rating_count__gte=cls.MIN_RATINGS_FOR_TOP_RATED,
                average_rating__gte=cls.MIN_AVERAGE_RATING_FOR_TOP_RATED,
            )
            .prefetch_related("artists", "featured_artists")
            .order_by(
                "-average_rating",
                "-rating_count",
                "-published_at",
                "-pk",
            )[:cls.RESULT_LIMIT]
        )

    @classmethod
    def top_rated_albums(cls):
        average_rating_subquery = (
            CommunityPostTarget.objects
            .filter(
                target_type=CommunityPostTarget.TargetType.ALBUM,
                album_id=OuterRef("pk"),
                post__status=CommunityPost.Status.PUBLISHED,
                post__rating__isnull=False,
            )
            .order_by()
            .values("album_id")
            .annotate(
                average=Avg("post__rating"),
            )
            .values("average")[:1]
        )

        rating_count_subquery = cls._count_subquery(
            model=CommunityPostTarget,
            filters={
                "target_type": CommunityPostTarget.TargetType.ALBUM,
                "album_id": OuterRef("pk"),
                "post__status": CommunityPost.Status.PUBLISHED,
                "post__rating__isnull": False,
            },
            group_by="album_id",
        )

        return (
            Album.objects
            # Include draft imports, but exclude archived albums.
            .exclude(status=Album.Status.ARCHIVED)
            .annotate(
                average_rating=Subquery(
                    average_rating_subquery,
                    output_field=DecimalField(
                        max_digits=3,
                        decimal_places=2,
                    ),
                ),
                rating_count=cls._integer_subquery(
                    rating_count_subquery,
                ),
            )
            .filter(
                rating_count__gte=cls.MIN_RATINGS_FOR_TOP_RATED,
                average_rating__gte=cls.MIN_AVERAGE_RATING_FOR_TOP_RATED,
            )
            .prefetch_related("artists")
            .order_by(
                "-average_rating",
                "-rating_count",
                "-release_date",
                "-published_at",
                "-pk",
            )[:cls.RESULT_LIMIT]
        )

    # ========================================================
    # FEATURED
    # ========================================================

    @classmethod
    def featured_songs(cls):
        return (
            Song.objects
            .filter(
                status=Song.Status.PUBLISHED,
                is_featured=True,
            )
            .prefetch_related("artists", "featured_artists")
            .order_by("-published_at", "-pk")[:cls.RESULT_LIMIT]
        )

    @classmethod
    def featured_albums(cls):
        return (
            Album.objects
            .filter(
                status=Album.Status.PUBLISHED,
                is_featured=True,
            )
            .prefetch_related("artists")
            .order_by("-published_at", "-pk")[:cls.RESULT_LIMIT]
        )

    @classmethod
    def featured_artists(cls):
        return (
            Artist.objects
            .filter(
                is_active=True,
                is_verified=True,
            )
            .order_by("name", "pk")[:cls.RESULT_LIMIT]
        )

    # ========================================================
    # RECENTLY RELEASED
    # ========================================================

    @classmethod
    def recently_released_songs(cls):
        return (
            Song.objects
            .filter(
                status=Song.Status.PUBLISHED,
                release_date__isnull=False,
            )
            .prefetch_related("artists", "featured_artists")
            .order_by(
                "-release_date",
                "-published_at",
                "-pk",
            )[:cls.RESULT_LIMIT]
        )

    @classmethod
    def recently_released_albums(cls):
        return (
            Album.objects
            .filter(
                status=Album.Status.PUBLISHED,
                release_date__isnull=False,
            )
            .prefetch_related("artists")
            .order_by(
                "-release_date",
                "-published_at",
                "-pk",
            )[:cls.RESULT_LIMIT]
        )
