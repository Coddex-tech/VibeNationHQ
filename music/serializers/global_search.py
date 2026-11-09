from rest_framework import serializers

from accounts.serializers.public_profile import PublicProfileSerializer
from music.serializers.catalog import (
    AlbumCardSerializer,
    ArtistCardSerializer,
    SongCardSerializer,
)
from music.serializers.community import CommunityPostSerializer
from music.serializers.editorial import (
    EditorialArticleCardSerializer,
)


# ============================================================
# GLOBAL SEARCH — USER
# ============================================================


class GlobalSearchUserSerializer(
    PublicProfileSerializer,
):
    """
    Lightweight public user representation for global search.

    Reuses the public profile image handling, but deliberately
    excludes profile fields and aggregate counts that are not
    needed in search results.

    is_following is read from the annotation added by
    GlobalSearchService, avoiding per-user database queries.
    """

    is_following = serializers.BooleanField(
        read_only=True,
        default=False,
    )

    class Meta:
        model = PublicProfileSerializer.Meta.model

        fields = [
            "id",
            "username",
            "display_name",
            "profile_image",
            "is_verified",
            "is_identity_verified",
            "is_following",
        ]

        read_only_fields = fields


# ============================================================
# GLOBAL SEARCH — EDITORIAL ARTICLE
# ============================================================


class GlobalSearchEditorialArticleSerializer(
    EditorialArticleCardSerializer,
):
    """
    Editorial search card.

    The existing editorial card serializer falls back to email
    when both full name and username are unavailable.

    Global search must never expose an email address, so this
    serializer uses only the user's display name or username.
    """

    def get_author(self, obj):
        author = obj.author

        return {
            "id": obj.author_id,
            "name": (
                getattr(author, "display_name", "")
                or getattr(author, "username", "")
            ),
        }


# ============================================================
# GLOBAL SEARCH — CATEGORY PAGE
# ============================================================


class GlobalSearchCategoryPageSerializer(
    serializers.Serializer,
):
    """
    Common response representation for one independently
    paginated global-search category.
    """

    count = serializers.IntegerField(read_only=True)
    page = serializers.IntegerField(read_only=True)
    page_size = serializers.IntegerField(read_only=True)

    has_next = serializers.BooleanField(read_only=True)
    has_previous = serializers.BooleanField(read_only=True)

    results = serializers.ListField(
        read_only=True,
    )


# ============================================================
# GLOBAL SEARCH — RESPONSE
# ============================================================


class GlobalSearchResponseSerializer(
    serializers.Serializer,
):
    """
    Unified response serializer for all six global-search
    categories.

    Expected input:
        {
            "songs": CategorySearchPage(...),
            "albums": CategorySearchPage(...),
            "artists": CategorySearchPage(...),
            "community_posts": CategorySearchPage(...),
            "editorial_articles": CategorySearchPage(...),
            "users": CategorySearchPage(...),
        }

    Catalog categories contain CatalogSearchResult objects.
    Their underlying model instances are extracted before
    passing them to the existing card serializers.
    """

    songs = serializers.SerializerMethodField()
    albums = serializers.SerializerMethodField()
    artists = serializers.SerializerMethodField()

    community_posts = serializers.SerializerMethodField()
    editorial_articles = serializers.SerializerMethodField()

    users = serializers.SerializerMethodField()

    # --------------------------------------------------------
    # Shared category representation
    # --------------------------------------------------------

    def _serialize_page(
        self,
        page,
        serializer_class,
        *,
        unwrap_catalog_results=False,
    ):
        results = page.results

        if unwrap_catalog_results:
            results = [
                result.object
                for result in results
            ]

        serialized_results = serializer_class(
            results,
            many=True,
            context=self.context,
        ).data

        return {
            "count": page.count,
            "page": page.page,
            "page_size": page.page_size,
            "has_next": page.has_next,
            "has_previous": page.has_previous,
            "results": serialized_results,
        }

    # --------------------------------------------------------
    # Catalog categories
    # --------------------------------------------------------

    def get_songs(self, obj):
        return self._serialize_page(
            obj["songs"],
            SongCardSerializer,
            unwrap_catalog_results=True,
        )

    def get_albums(self, obj):
        return self._serialize_page(
            obj["albums"],
            AlbumCardSerializer,
            unwrap_catalog_results=True,
        )

    def get_artists(self, obj):
        return self._serialize_page(
            obj["artists"],
            ArtistCardSerializer,
            unwrap_catalog_results=True,
        )

    # --------------------------------------------------------
    # Community and editorial categories
    # --------------------------------------------------------

    def get_community_posts(self, obj):
        return self._serialize_page(
            obj["community_posts"],
            CommunityPostSerializer,
        )

    def get_editorial_articles(self, obj):
        return self._serialize_page(
            obj["editorial_articles"],
            GlobalSearchEditorialArticleSerializer,
        )

    # --------------------------------------------------------
    # Public user category
    # --------------------------------------------------------

    def get_users(self, obj):
        return self._serialize_page(
            obj["users"],
            GlobalSearchUserSerializer,
        )