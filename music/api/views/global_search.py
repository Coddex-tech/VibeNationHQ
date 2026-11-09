from rest_framework import serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from music.serializers.global_search import (
    GlobalSearchResponseSerializer,
)
from music.services.global_search import (
    GlobalSearchService,
)


# ============================================================
# GLOBAL SEARCH — QUERY VALIDATION
# ============================================================


class GlobalSearchQuerySerializer(serializers.Serializer):
    """
    Validates query parameters accepted by the global search API.
    """

    CATEGORY_CHOICES = (
        ("songs", "Songs"),
        ("albums", "Albums"),
        ("artists", "Artists"),
        ("community_posts", "Community Posts"),
        ("editorial_articles", "Editorial Articles"),
        ("users", "Users"),
    )

    q = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        min_length=2,
        max_length=GlobalSearchService.MAX_QUERY_LENGTH,
    )

    type = serializers.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
    )

    page_size = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=GlobalSearchService.MAX_PAGE_SIZE,
        default=GlobalSearchService.DEFAULT_PAGE_SIZE,
    )

    songs_page = serializers.IntegerField(
        required=False,
        min_value=1,
        default=1,
    )

    albums_page = serializers.IntegerField(
        required=False,
        min_value=1,
        default=1,
    )

    artists_page = serializers.IntegerField(
        required=False,
        min_value=1,
        default=1,
    )

    community_posts_page = serializers.IntegerField(
        required=False,
        min_value=1,
        default=1,
    )

    editorial_articles_page = serializers.IntegerField(
        required=False,
        min_value=1,
        default=1,
    )

    users_page = serializers.IntegerField(
        required=False,
        min_value=1,
        default=1,
    )


# ============================================================
# GLOBAL SEARCH — API VIEW
# ============================================================


class GlobalSearchAPIView(GenericAPIView):
    """
    Unified public search endpoint for VibeNationHQ.

    Searches:
    - Songs
    - Albums
    - Artists
    - Community Posts
    - Editorial Articles
    - Public User Profiles

    Each category has independent pagination.

    Existing search endpoints remain unchanged.
    """

    serializer_class = GlobalSearchQuerySerializer
    permission_classes = [AllowAny]

    PAGE_PARAMETERS = (
        "songs_page",
        "albums_page",
        "artists_page",
        "community_posts_page",
        "editorial_articles_page",
        "users_page",
    )

    def get_service(self):
        return GlobalSearchService()

    def get(self, request, *args, **kwargs):
        # ----------------------------------------------------
        # Validate query parameters
        # ----------------------------------------------------

        query_serializer = self.get_serializer(
            data=request.query_params,
        )

        query_serializer.is_valid(
            raise_exception=True,
        )

        validated_data = query_serializer.validated_data

        query = validated_data["q"]
        category = validated_data.get("type")

        page_size = validated_data["page_size"]

        # ----------------------------------------------------
        # Build independent category page parameters
        # ----------------------------------------------------

        pages = {
            parameter.removesuffix("_page"): validated_data[parameter]
            for parameter in self.PAGE_PARAMETERS
            if parameter in validated_data
        }

        # ----------------------------------------------------
        # Execute global search
        # ----------------------------------------------------

        service = self.get_service()

        search_results = service.search(
            query=query,
            category=category,
            pages=pages,
            page_size=page_size,
            user=request.user,
        )

        # ----------------------------------------------------
        # Serialize category results
        # ----------------------------------------------------

        response_serializer = GlobalSearchResponseSerializer(
            search_results,
            context={
                "request": request,
            },
        )

        results = response_serializer.data

        # ----------------------------------------------------
        # Add category-specific pagination URLs
        # ----------------------------------------------------

        for category_name, page in search_results.items():
            page_parameter = (
                f"{category_name}_page"
            )

            results[category_name]["next"] = (
                self._build_page_url(
                    request=request,
                    parameter=page_parameter,
                    page_number=page.page + 1,
                )
                if page.has_next
                else None
            )

            results[category_name]["previous"] = (
                self._build_page_url(
                    request=request,
                    parameter=page_parameter,
                    page_number=page.page - 1,
                )
                if page.has_previous
                else None
            )

        # ----------------------------------------------------
        # Final response
        # ----------------------------------------------------

        return Response(
            {
                "query": query,
                "type": category or "all",
                "results": results,
            },
            status=status.HTTP_200_OK,
        )

    # ========================================================
    # Pagination URL helper
    # ========================================================

    @staticmethod
    def _build_page_url(
        *,
        request,
        parameter,
        page_number,
    ):
        """
        Preserve existing query parameters while changing
        only the requested category's page number.
        """

        query_params = request.query_params.copy()

        query_params[parameter] = str(page_number)

        base_url = request.build_absolute_uri(
            request.path,
        )

        return (
            f"{base_url}?{query_params.urlencode()}"
        )