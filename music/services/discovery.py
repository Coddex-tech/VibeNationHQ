from datetime import timedelta

from django.db.models import Avg, Count, Q, F
from django.db.models.functions import Greatest
from django.utils import timezone

from music.models import (
    Album,
    AlbumFavorite,
    AlbumRating,
    Artist,
    ArtistFollow,
    CommunityPost,
    CommunityPostTarget,
    Song,
    SongFavorite,
    SongRating,
)


class DiscoveryService:
    """
    Business logic for VibeNation music discovery.

    Discovery is based on existing catalog and community engagement
    data. No additional counters are introduced here.
    """

    RESULT_LIMIT = 10
    TRENDING_DAYS = 7
    MIN_RATINGS_FOR_TOP_RATED = 5

    # ========================================================
    # TRENDING
    # ========================================================

    @classmethod
    def trending_songs(cls):
        since = timezone.now() - timedelta(days=cls.TRENDING_DAYS)

        return (
            Song.objects
            .filter(status=Song.Status.PUBLISHED)
            .annotate(
                recent_favorites=Count(
                    "favorites",
                    filter=Q(
                        favorites__created_at__gte=since
                    ),
                    distinct=True,
                ),
                recent_ratings=Count(
                    "ratings",
                    filter=Q(
                        ratings__created_at__gte=since
                    ),
                    distinct=True,
                ),
                recent_discussions=Count(
                    "community_post_targets__post",
                    filter=Q(
                        community_post_targets__post__status=CommunityPost.Status.PUBLISHED,
                        community_post_targets__post__created_at__gte=since,
                    ),
                    distinct=True,
                ),
            )
            .filter(
                Q(recent_favorites__gt=0)
                | Q(recent_ratings__gt=0)
                | Q(recent_discussions__gt=0)
            )
            .select_related("album")
            .prefetch_related(
                "artists",
                "featured_artists",
            )
            .order_by(
                "-recent_favorites",
                "-recent_ratings",
                "-recent_discussions",
                "-favorites_count",
                "-ratings_count",
                "-published_at",
            )[:cls.RESULT_LIMIT]
        )

    @classmethod
    def trending_albums(cls):
        since = timezone.now() - timedelta(days=cls.TRENDING_DAYS)

        return (
            Album.objects
            .filter(status=Album.Status.PUBLISHED)
            .annotate(
                recent_favorites=Count(
                    "favorites",
                    filter=Q(
                        favorites__created_at__gte=since
                    ),
                    distinct=True,
                ),
                recent_ratings=Count(
                    "ratings",
                    filter=Q(
                        ratings__created_at__gte=since
                    ),
                    distinct=True,
                ),
                recent_discussions=Count(
                    "community_post_targets__post",
                    filter=Q(
                        community_post_targets__post__status=CommunityPost.Status.PUBLISHED,
                        community_post_targets__post__created_at__gte=since,
                    ),
                    distinct=True,
                ),
            )
            .filter(
                Q(recent_favorites__gt=0)
                | Q(recent_ratings__gt=0)
                | Q(recent_discussions__gt=0)
            )
            .prefetch_related("artists")
            .order_by(
                "-recent_favorites",
                "-recent_ratings",
                "-recent_discussions",
                "-favorites_count",
                "-ratings_count",
                "-release_date",
                "-published_at",
            )[:cls.RESULT_LIMIT]
        )

    @classmethod
    def trending_artists(cls):
        since = timezone.now() - timedelta(days=cls.TRENDING_DAYS)

        return (
            Artist.objects
            .filter(is_active=True)
            .annotate(
                recent_follows=Count(
                    "followers",
                    filter=Q(
                        followers__created_at__gte=since
                    ),
                    distinct=True,
                ),
                recent_songs=Count(
                    "songs",
                    filter=Q(
                        songs__status=Song.Status.PUBLISHED,
                        songs__published_at__gte=since,
                    ),
                    distinct=True,
                ),
                recent_albums=Count(
                    "albums",
                    filter=Q(
                        albums__status=Album.Status.PUBLISHED,
                        albums__published_at__gte=since,
                    ),
                    distinct=True,
                ),
            )
            .filter(
                Q(recent_follows__gt=0)
                | Q(recent_songs__gt=0)
                | Q(recent_albums__gt=0)
            )
            .order_by(
                "-recent_follows",
                "-recent_songs",
                "-recent_albums",
                "-followers_count",
                "name",
            )[:cls.RESULT_LIMIT]
        )

    # ========================================================
    # MOST DISCUSSED
    # ========================================================

    @classmethod
    def most_discussed_songs(cls):
        return (
            Song.objects
            .filter(status=Song.Status.PUBLISHED)
            .annotate(
                discussion_count=Count(
                    "community_post_targets__post",
                    filter=Q(
                        community_post_targets__post__status=CommunityPost.Status.PUBLISHED,
                    ),
                    distinct=True,
                ),
            )
            .filter(discussion_count__gt=0)
            .prefetch_related(
                "artists",
                "featured_artists",
            )
            .order_by(
                "-discussion_count",
                "-favorites_count",
                "-ratings_count",
                "-published_at",
            )[:cls.RESULT_LIMIT]
        )

    @classmethod
    def most_discussed_albums(cls):
        return (
            Album.objects
            .filter(status=Album.Status.PUBLISHED)
            .annotate(
                discussion_count=Count(
                    "community_post_targets__post",
                    filter=Q(
                        community_post_targets__post__status=CommunityPost.Status.PUBLISHED,
                    ),
                    distinct=True,
                ),
            )
            .filter(discussion_count__gt=0)
            .prefetch_related("artists")
            .order_by(
                "-discussion_count",
                "-favorites_count",
                "-ratings_count",
                "-release_date",
                "-published_at",
            )[:cls.RESULT_LIMIT]
        )

    # ========================================================
    # MOST FAVOURITED
    # ========================================================

    @classmethod
    def most_favorited_songs(cls):
        return (
            Song.objects
            .filter(status=Song.Status.PUBLISHED)
            .annotate(
                actual_favorite_count=Count(
                    "favorites",
                    distinct=True,
                ),
            )
            .annotate(
                favorite_count=Greatest(
                    F("favorites_count"),
                    F("actual_favorite_count"),
                ),
            )
            .filter(favorite_count__gt=0)
            .prefetch_related("artists", "featured_artists")
            .order_by(
                "-favorite_count",
                "-favorites_count",
                "-ratings_count",
                "-published_at",
            )[:cls.RESULT_LIMIT]
        )

    @classmethod
    def most_favorited_albums(cls):
        return (
            Album.objects
            .filter(status=Album.Status.PUBLISHED)
            .annotate(
                actual_favorite_count=Count(
                    "favorites",
                    distinct=True,
                ),
            )
            .annotate(
                favorite_count=Greatest(
                    F("favorites_count"),
                    F("actual_favorite_count"),
                ),
            )
            .filter(favorite_count__gt=0)
            .prefetch_related("artists")
            .order_by(
                "-favorite_count",
                "-favorites_count",
                "-ratings_count",
                "-published_at",
            )[:cls.RESULT_LIMIT]
        )

    # ========================================================
    # TOP RATED
    # ========================================================

    @classmethod
    def top_rated_songs(cls):
        return (
            Song.objects
            .filter(status=Song.Status.PUBLISHED)
            .annotate(
                average_rating=Avg("ratings__rating"),
                rating_count=Count(
                    "ratings",
                    distinct=True,
                ),
            )
            .filter(
                rating_count__gte=cls.MIN_RATINGS_FOR_TOP_RATED,
            )
            .prefetch_related("artists", "featured_artists")
            .order_by(
                "-average_rating",
                "-rating_count",
                "-ratings_count",
                "-published_at",
            )[:cls.RESULT_LIMIT]
        )

    @classmethod
    def top_rated_albums(cls):
        return (
            Album.objects
            .filter(status=Album.Status.PUBLISHED)
            .annotate(
                average_rating=Avg("ratings__rating"),
                rating_count=Count(
                    "ratings",
                    distinct=True,
                ),
            )
            .filter(
                rating_count__gte=cls.MIN_RATINGS_FOR_TOP_RATED,
            )
            .prefetch_related("artists")
            .order_by(
                "-average_rating",
                "-rating_count",
                "-ratings_count",
                "-release_date",
                "-published_at",
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
            .prefetch_related(
                "artists",
                "featured_artists",
            )
            .order_by("-published_at")[:cls.RESULT_LIMIT]
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
            .order_by("-published_at")[:cls.RESULT_LIMIT]
        )

    @classmethod
    def featured_artists(cls):
        return (
            Artist.objects
            .filter(
                is_active=True,
                is_verified=True,
            )
            .order_by("name")[:cls.RESULT_LIMIT]
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
            .prefetch_related(
                "artists",
                "featured_artists",
            )
            .order_by(
                "-release_date",
                "-published_at",
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
            )[:cls.RESULT_LIMIT]
        )