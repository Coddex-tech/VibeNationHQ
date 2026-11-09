from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import (
    BooleanField,
    Count,
    Exists,
    OuterRef,
    Prefetch,
    Q,
    QuerySet,
    Value,
)

from music.models import (
    Album,
    Artist,
    CommunityPost,
    CommunityPostFavorite,
    CommunityPostLike,
    EditorialArticle,
    Song,
    UserFollow,
)

from music.services.catalog_search import (
    MusicCatalogSearchService,
)


User = get_user_model()


@dataclass(frozen=True, slots=True)
class CategorySearchPage:
    """
    Paginated results for one global-search category.
    """

    category: str
    count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool
    results: list[Any]


class GlobalSearchService:
    """
    Coordinates global search across VibeNationHQ.

    Supported categories:
        - songs
        - albums
        - artists
        - community_posts
        - editorial_articles
        - users

    Each category has independent pagination.

    The service is read-only and does not handle HTTP
    request or response serialization.
    """

    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 20
    MAX_QUERY_LENGTH = 200
    MIN_QUERY_LENGTH = 2

    CATEGORIES = (
        "songs",
        "albums",
        "artists",
        "community_posts",
        "editorial_articles",
        "users",
    )

    PAGE_PARAMETERS = {
        "songs": "songs_page",
        "albums": "albums_page",
        "artists": "artists_page",
        "community_posts": "community_posts_page",
        "editorial_articles": "editorial_articles_page",
        "users": "users_page",
    }

    CATALOG_ENTITY_TYPES = {
        "songs": "song",
        "albums": "album",
        "artists": "artist",
    }

    def __init__(self):
        self.catalog_search = MusicCatalogSearchService()

    # ========================================================
    # Public API
    # ========================================================

    def search(
        self,
        *,
        query: str,
        category: str | None = None,
        pages: dict[str, int] | None = None,
        page_size: int = DEFAULT_PAGE_SIZE,
        user=None,
    ) -> dict[str, CategorySearchPage]:
        """
        Search all categories or one selected category.

        Args:
            query:
                Search phrase.

            category:
                Optional category restriction.

            pages:
                Independent page numbers keyed by category.

            page_size:
                Number of results per category.

            user:
                Authenticated requesting user, or None.

        Returns:
            A dictionary containing one CategorySearchPage
            for each supported category.

        Categories outside a selected category are returned
        as empty pages.
        """

        normalized_query = self._validate_query(query)

        normalized_category = self._validate_category(
            category,
        )

        normalized_pages = self._normalize_pages(
            pages or {},
        )

        normalized_page_size = self._normalize_page_size(
            page_size,
        )

        results = {}

        for current_category in self.CATEGORIES:
            current_page = normalized_pages.get(
                current_category,
                1,
            )

            if (
                normalized_category is not None
                and current_category != normalized_category
            ):
                results[current_category] = (
                    self._empty_page(
                        category=current_category,
                        page=current_page,
                        page_size=normalized_page_size,
                    )
                )
                continue

            results[current_category] = (
                self._search_category(
                    category=current_category,
                    query=normalized_query,
                    page=current_page,
                    page_size=normalized_page_size,
                    user=user,
                )
            )

        return results

    # ========================================================
    # Category dispatch
    # ========================================================

    def _search_category(
        self,
        *,
        category: str,
        query: str,
        page: int,
        page_size: int,
        user=None,
    ) -> CategorySearchPage:

        offset = (page - 1) * page_size

        if category in self.CATALOG_ENTITY_TYPES:
            return self._search_catalog_category(
                category=category,
                query=query,
                page=page,
                page_size=page_size,
                offset=offset,
            )

        if category == "community_posts":
            return self._search_community_posts(
                query=query,
                page=page,
                page_size=page_size,
                offset=offset,
                user=user,
            )

        if category == "editorial_articles":
            return self._search_editorial_articles(
                query=query,
                page=page,
                page_size=page_size,
                offset=offset,
            )

        if category == "users":
            return self._search_users(
                query=query,
                page=page,
                page_size=page_size,
                offset=offset,
                user=user,
            )

        raise ValueError(
            f"Unsupported global search category: {category}."
        )

    # ========================================================
    # Canonical music catalog
    # ========================================================

    def _search_catalog_category(
        self,
        *,
        category: str,
        query: str,
        page: int,
        page_size: int,
        offset: int,
    ) -> CategorySearchPage:

        entity_type = self.CATALOG_ENTITY_TYPES[category]

        # MusicCatalogSearchService currently supports a maximum
        # limit of 20, matching this service's page-size maximum.
        results, count = (
            self.catalog_search.search_with_count(
                query=query,
                entity_type=entity_type,
                limit=page_size,
                offset=offset,
                public_only=True,
            )
        )

        return CategorySearchPage(
            category=category,
            count=count,
            page=page,
            page_size=page_size,
            has_next=offset + len(results) < count,
            has_previous=page > 1 and offset > 0,
            results=results,
        )

    # ========================================================
    # Community posts
    # ========================================================

    def _search_community_posts(
    self,
    *,
    query: str,
    page: int,
    page_size: int,
    offset: int,
    user=None,
    ) -> CategorySearchPage:

        # ----------------------------------------------------
        # Annotate each post author with follow relationships
        # ----------------------------------------------------

        author_queryset = User.objects.all()

        if user is not None and user.is_authenticated:
            author_follows = UserFollow.objects.filter(
                follower=user,
                following_id=OuterRef("pk"),
            )

            author_follows_back = UserFollow.objects.filter(
                follower_id=OuterRef("pk"),
                following=user,
            )

            author_queryset = author_queryset.annotate(
                is_following=Exists(
                    author_follows,
                ),
                is_following_you=Exists(
                    author_follows_back,
                ),
            )
        else:
            author_queryset = author_queryset.annotate(
                is_following=Value(
                    False,
                    output_field=BooleanField(),
                ),
                is_following_you=Value(
                    False,
                    output_field=BooleanField(),
                ),
            )

        # ----------------------------------------------------
        # Published community posts matching the search
        # ----------------------------------------------------

        queryset = (
            CommunityPost.objects
            .filter(
                status=CommunityPost.Status.PUBLISHED,
            )
            .filter(
                self._text_filter(
                    query,
                    ("content",),
                )
            )
            .select_related(
                "target",
                "target__song",
                "target__song__album",
                "target__album",
                "target__artist",
            )
            .prefetch_related(
                Prefetch(
                    "user",
                    queryset=author_queryset,
                ),
                "target__song__artists",
                "target__song__featured_artists",
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

        # ----------------------------------------------------
        # Current user's post engagement states
        # ----------------------------------------------------

        if user is not None and user.is_authenticated:
            liked_posts = CommunityPostLike.objects.filter(
                user=user,
                post_id=OuterRef("pk"),
            )

            favorited_posts = CommunityPostFavorite.objects.filter(
                user=user,
                post_id=OuterRef("pk"),
            )

            queryset = queryset.annotate(
                is_liked=Exists(
                    liked_posts,
                ),
                is_favorited=Exists(
                    favorited_posts,
                ),
            )
        else:
            queryset = queryset.annotate(
                is_liked=Value(
                    False,
                    output_field=BooleanField(),
                ),
                is_favorited=Value(
                    False,
                    output_field=BooleanField(),
                ),
            )

        queryset = queryset.order_by(
            "-created_at",
            "-pk",
        )

        return self._paginate_queryset(
            category="community_posts",
            queryset=queryset,
            page=page,
            page_size=page_size,
            offset=offset,
        )

    # ========================================================
    # Editorial articles
    # ========================================================

    def _search_editorial_articles(
        self,
        *,
        query: str,
        page: int,
        page_size: int,
        offset: int,
    ) -> CategorySearchPage:

        queryset = EditorialArticle.objects.filter(
            status=EditorialArticle.Status.PUBLISHED,
        ).filter(
            self._text_filter(
                query,
                ("title", "excerpt"),
            )
        )

        queryset = (
            queryset
            .select_related(
                "author",
                "song",
                "song__album",
                "artist",
                "album",
            )
            .prefetch_related(
                "genres",
                "song__artists",
                "song__featured_artists",
                "album__artists",
            )
            .order_by(
                "-published_at",
                "-created_at",
                "-pk",
            )
        )

        return self._paginate_queryset(
            category="editorial_articles",
            queryset=queryset,
            page=page,
            page_size=page_size,
            offset=offset,
        )

    # ========================================================
    # Public user profiles
    # ========================================================

    def _search_users(
        self,
        *,
        query: str,
        page: int,
        page_size: int,
        offset: int,
        user=None,
    ) -> CategorySearchPage:

        queryset = User.objects.filter(
            is_active=True,
            is_staff=False,
            is_superuser=False,
            onboarding_completed=True,
        ).filter(
            self._text_filter(
                query,
                ("username", "display_name"),
            )
        )

        if user is not None and user.is_authenticated:
            queryset = queryset.annotate(
                is_following=Exists(
                    UserFollow.objects.filter(
                        follower=user,
                        following=OuterRef("pk"),
                    )
                )
            )
        else:
            queryset = queryset.annotate(
                is_following=Value(
                    False,
                    output_field=BooleanField(),
                )
            )

        queryset = queryset.order_by(
            "username",
            "pk",
        )

        return self._paginate_queryset(
            category="users",
            queryset=queryset,
            page=page,
            page_size=page_size,
            offset=offset,
        )

    # ========================================================
    # Queryset helpers
    # ========================================================

    @staticmethod
    def _text_filter(
        query: str,
        fields: tuple[str, ...],
    ) -> Q:
        """
        Build an AND-across-tokens search filter.

        Every query token must match at least one searchable
        field, while different tokens may match different fields.
        """

        tokens = query.split()

        combined_filter = Q()

        for token in tokens:
            token_filter = Q()

            for field in fields:
                token_filter |= Q(
                    **{f"{field}__icontains": token}
                )

            combined_filter &= token_filter

        return combined_filter

    @staticmethod
    def _paginate_queryset(
        *,
        category: str,
        queryset: QuerySet,
        page: int,
        page_size: int,
        offset: int,
    ) -> CategorySearchPage:

        count = queryset.count()

        results = list(
            queryset[offset:offset + page_size]
        )

        return CategorySearchPage(
            category=category,
            count=count,
            page=page,
            page_size=page_size,
            has_next=offset + len(results) < count,
            has_previous=page > 1 and offset > 0,
            results=results,
        )

    # ========================================================
    # Validation and normalization
    # ========================================================

    @classmethod
    def _validate_query(
        cls,
        query: str,
    ) -> str:

        if not isinstance(query, str):
            raise ValueError(
                "Search query must be a string."
            )

        query = query.strip()

        if len(query) > cls.MAX_QUERY_LENGTH:
            raise ValueError(
                "Search query is too long."
            )

        if len(query) < cls.MIN_QUERY_LENGTH:
            raise ValueError(
                "Search query must contain at least 2 characters."
            )

        return query

    @classmethod
    def _validate_category(
        cls,
        category: str | None,
    ) -> str | None:

        if category is None:
            return None

        if not isinstance(category, str):
            raise ValueError(
                "Search category must be a string."
            )

        category = category.strip().lower()

        if category not in cls.CATEGORIES:
            raise ValueError(
                f"Unsupported global search category: {category}."
            )

        return category

    @classmethod
    def _normalize_pages(
        cls,
        pages: dict[str, int],
    ) -> dict[str, int]:

        normalized = {}

        for category, page in pages.items():
            if category not in cls.CATEGORIES:
                raise ValueError(
                    f"Unsupported pagination category: {category}."
                )

            if isinstance(page, bool) or not isinstance(page, int):
                raise ValueError(
                    f"Page number for {category} must be an integer."
                )

            if page < 1:
                raise ValueError(
                    f"Page number for {category} must be at least 1."
                )

            normalized[category] = page

        return normalized

    @classmethod
    def _normalize_page_size(
        cls,
        page_size: int,
    ) -> int:

        if isinstance(page_size, bool) or not isinstance(page_size, int):
            raise ValueError(
                "Page size must be an integer."
            )

        if page_size < 1:
            raise ValueError(
                "Page size must be at least 1."
            )

        return min(
            page_size,
            cls.MAX_PAGE_SIZE,
        )

    @staticmethod
    def _empty_page(
        *,
        category: str,
        page: int,
        page_size: int,
    ) -> CategorySearchPage:

        return CategorySearchPage(
            category=category,
            count=0,
            page=page,
            page_size=page_size,
            has_next=False,
            has_previous=False,
            results=[],
        )