from urllib.parse import urlencode

from django.db import transaction
from django.db.models import Exists, OuterRef

from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from accounts.api.permissions import IsOrdinaryVibeNationUser

from music.api.pagination import MusicPagination

from music.models import (
    Album,
    AlbumFavorite,
    CommunityPost,
    CommunityPostFavorite,
    EditorialArticle,
    EditorialArticleFavorite,
    EditorialArticleLike,
    Song,
    SongFavorite,
)

from music.serializers.favorites import (
    AlbumFavoriteCreateSerializer,
    AlbumFavoriteSerializer,
    SongFavoriteCreateSerializer,
    SongFavoriteSerializer,
    EditorialArticleFavoriteCreateSerializer,
    EditorialArticleFavoriteSerializer,
)

from music.serializers.community import CommunityPostSerializer
from music.serializers.editorial import EditorialArticleCardSerializer

from music.services.favorites import (
    AlbumFavoriteService,
    SongFavoriteService,
    EditorialArticleFavoriteService,
)

from music.services.community import CommunityPostFavoriteService

from music.services.feed_interactions import (
    MusicFeedInteractionService,
)


class SongFavoriteAPIView(generics.GenericAPIView):
    queryset = Song.objects.filter(status=Song.Status.PUBLISHED)
    permission_classes = [IsOrdinaryVibeNationUser]

    def post(self, request, *args, **kwargs):
        song = self.get_object()

        serializer = SongFavoriteCreateSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            favorite = SongFavoriteService.create(
                user=request.user,
                song=song,
            )

            MusicFeedInteractionService.record_song_favorite(
                user=request.user,
                song=song,
            )

        output_serializer = SongFavoriteSerializer(
            favorite,
            context=self.get_serializer_context(),
        )

        song.refresh_from_db()

        return Response(
            {
                "favorited": True,
                "favorites_count": song.favorites_count,
                "favorite": output_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        song = self.get_object()

        favorite = SongFavorite.objects.filter(
            user=request.user,
            song=song,
        ).first()

        if favorite is None:
            return Response(
                {
                    "favorited": False,
                    "favorites_count": song.favorites_count,
                },
                status=status.HTTP_200_OK,
            )

        SongFavoriteService.delete(
            favorite_instance=favorite,
        )

        song.refresh_from_db()

        return Response(
            {
                "favorited": False,
                "favorites_count": song.favorites_count,
            },
            status=status.HTTP_200_OK,
        )


class AlbumFavoriteAPIView(generics.GenericAPIView):
    queryset = Album.objects.filter(status=Album.Status.PUBLISHED)
    permission_classes = [IsOrdinaryVibeNationUser]

    def post(self, request, *args, **kwargs):
        album = self.get_object()

        serializer = AlbumFavoriteCreateSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            favorite = AlbumFavoriteService.create(
                user=request.user,
                album=album,
            )

            MusicFeedInteractionService.record_album_favorite(
                user=request.user,
                album=album,
            )

        output_serializer = AlbumFavoriteSerializer(
            favorite,
            context=self.get_serializer_context(),
        )

        album.refresh_from_db()

        return Response(
            {
                "favorited": True,
                "favorites_count": album.favorites_count,
                "favorite": output_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        album = self.get_object()

        favorite = AlbumFavorite.objects.filter(
            user=request.user,
            album=album,
        ).first()

        if favorite is None:
            return Response(
                {
                    "favorited": False,
                    "favorites_count": album.favorites_count,
                },
                status=status.HTTP_200_OK,
            )

        AlbumFavoriteService.delete(
            favorite_instance=favorite,
        )

        album.refresh_from_db()

        return Response(
            {
                "favorited": False,
                "favorites_count": album.favorites_count,
            },
            status=status.HTTP_200_OK,
        )


class EditorialArticleFavoriteAPIView(generics.GenericAPIView):
    """Favorite or unfavorite a published editorial article."""

    queryset = EditorialArticle.objects.filter(
        status=EditorialArticle.Status.PUBLISHED,
    )

    permission_classes = [IsOrdinaryVibeNationUser]

    def post(self, request, *args, **kwargs):
        article = self.get_object()

        serializer = EditorialArticleFavoriteCreateSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            favorite = EditorialArticleFavoriteService.create(
                user=request.user,
                article=article,
            )

            MusicFeedInteractionService.record_editorial_favorite(
                user=request.user,
                article=article,
            )

        output_serializer = EditorialArticleFavoriteSerializer(
            favorite,
            context=self.get_serializer_context(),
        )

        article.refresh_from_db()

        return Response(
            {
                "favorited": True,
                "favorites_count": article.favorites_count,
                "favorite": output_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        article = self.get_object()

        favorite = EditorialArticleFavorite.objects.filter(
            user=request.user,
            article=article,
        ).first()

        if favorite is None:
            return Response(
                {
                    "favorited": False,
                    "favorites_count": article.favorites_count,
                },
                status=status.HTTP_200_OK,
            )

        EditorialArticleFavoriteService.delete(
            favorite_instance=favorite,
        )

        article.refresh_from_db()

        return Response(
            {
                "favorited": False,
                "favorites_count": article.favorites_count,
            },
            status=status.HTTP_200_OK,
        )


class CommunityPostFavoriteAPIView(generics.GenericAPIView):
    """Favorite or unfavorite a published community post."""

    queryset = CommunityPost.objects.filter(
        status=CommunityPost.Status.PUBLISHED,
    )

    permission_classes = [IsOrdinaryVibeNationUser]

    def post(self, request, *args, **kwargs):
        post = self.get_object()

        with transaction.atomic():
            favorite = CommunityPostFavoriteService.create(
                user=request.user,
                post=post,
            )

            MusicFeedInteractionService.record_community_post_favorite(
                user=request.user,
                post=post,
            )

        output_serializer = CommunityPostSerializer(
            post,
            context=self.get_serializer_context(),
        )

        post.refresh_from_db()

        return Response(
            {
                "favorited": True,
                "favorites_count": post.favorites_count,
                "favorite": {
                    "id": favorite.pk,
                    "created_at": favorite.created_at,
                },
                "post": output_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        post = self.get_object()

        favorite = CommunityPostFavorite.objects.filter(
            user=request.user,
            post=post,
        ).first()

        if favorite is None:
            return Response(
                {
                    "favorited": False,
                    "favorites_count": post.favorites_count,
                },
                status=status.HTTP_200_OK,
            )

        CommunityPostFavoriteService.delete(
            favorite_instance=favorite,
        )

        post.refresh_from_db()

        return Response(
            {
                "favorited": False,
                "favorites_count": post.favorites_count,
            },
            status=status.HTTP_200_OK,
        )


class CombinedFavoritesListAPIView(generics.GenericAPIView):
    """
    List a user's favorited community posts and editorial articles.

    Optional query parameter:
        type=community_post
        type=editorial

    Omitting type returns both content types, ordered by the
    actual favorite timestamp, newest first.

    Pagination uses page-number semantics and returns:
        count, next, previous, results

    To keep database work bounded, fetch only the first
    offset + page_size favorite records from each applicable
    favorite table before merging and slicing the results.
    """

    permission_classes = [IsOrdinaryVibeNationUser]
    pagination_class = MusicPagination

    VALID_TYPES = {
        "community_post",
        "editorial",
    }

    def get(self, request, *args, **kwargs):
        favorite_type = request.query_params.get("type")

        if favorite_type and favorite_type not in self.VALID_TYPES:
            raise ValidationError(
                {
                    "type": (
                        "Choose 'community_post' or 'editorial', "
                        "or omit this parameter to retrieve all favorites."
                    ),
                }
            )

        page = self._get_positive_integer(
            request.query_params.get("page", "1"),
            parameter="page",
        )

        page_size = self._get_page_size(
            request.query_params.get("page_size"),
        )

        offset = (page - 1) * page_size
        fetch_limit = offset + page_size

        community_count = 0
        editorial_count = 0

        community_rows = []
        editorial_rows = []

        # Fetch community post favorites when requested, or
        # when no type filter is supplied.
        if favorite_type in (None, "community_post"):
            community_favorites = (
                CommunityPostFavorite.objects
                .filter(
                    user=request.user,
                    post__status=CommunityPost.Status.PUBLISHED,
                )
                .order_by("-created_at", "-pk")
            )

            community_count = community_favorites.count()

            community_rows = list(
                community_favorites.values(
                    "post_id",
                    "created_at",
                    "pk",
                )[:fetch_limit]
            )

        # Fetch editorial article favorites when requested, or
        # when no type filter is supplied.
        if favorite_type in (None, "editorial"):
            editorial_favorites = (
                EditorialArticleFavorite.objects
                .filter(
                    user=request.user,
                    article__status=EditorialArticle.Status.PUBLISHED,
                )
                .order_by("-created_at", "-pk")
            )

            editorial_count = editorial_favorites.count()

            editorial_rows = list(
                editorial_favorites.values(
                    "article_id",
                    "created_at",
                    "pk",
                )[:fetch_limit]
            )

        count = community_count + editorial_count

        # Reject page numbers that start beyond the available
        # results, consistent with page-number pagination.
        if page > 1 and offset >= count:
            raise NotFound("Invalid page.")

        # Use the existing optimized community service queryset
        # so CommunityPostSerializer receives its expected
        # annotations and related objects.
        community_ids = [
            row["post_id"]
            for row in community_rows
        ]

        community_posts = {}

        if community_ids:
            community_queryset = (
                CommunityPostFavoriteService.get_user_favorites(
                    user=request.user,
                )
                .filter(pk__in=community_ids)
            )

            community_posts = {
                post.pk: post
                for post in community_queryset
            }

        # Prepare editorial article engagement state and related
        # objects for EditorialArticleCardSerializer.
        editorial_ids = [
            row["article_id"]
            for row in editorial_rows
        ]

        editorial_articles = {}

        if editorial_ids:
            user_likes = EditorialArticleLike.objects.filter(
                user=request.user,
                article_id=OuterRef("pk"),
            )

            user_favorites = EditorialArticleFavorite.objects.filter(
                user=request.user,
                article_id=OuterRef("pk"),
            )

            article_queryset = (
                EditorialArticle.objects
                .filter(
                    pk__in=editorial_ids,
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
                .annotate(
                    user_has_liked=Exists(user_likes),
                    user_has_favorited=Exists(user_favorites),
                )
            )

            editorial_articles = {
                article.pk: article
                for article in article_queryset
            }

        # Merge both content types using the timestamp from
        # each favorite record, not the content creation date.
        merged = []

        for row in community_rows:
            post = community_posts.get(row["post_id"])

            if post is not None:
                merged.append(
                    {
                        "content_type": "community_post",
                        "favorited_at": row["created_at"],
                        "content": post,
                        "sort_id": row["pk"],
                    }
                )

        for row in editorial_rows:
            article = editorial_articles.get(row["article_id"])

            if article is not None:
                merged.append(
                    {
                        "content_type": "editorial",
                        "favorited_at": row["created_at"],
                        "content": article,
                        "sort_id": row["pk"],
                    }
                )

        # Sort newest favorite first. The favorite record's PK
        # provides a deterministic tie-breaker for equal timestamps.
        merged.sort(
            key=lambda item: (
                item["favorited_at"],
                item["content_type"],
                item["sort_id"],
            ),
            reverse=True,
        )

        page_items = merged[offset:offset + page_size]

        results = []

        for item in page_items:
            if item["content_type"] == "community_post":
                content = CommunityPostSerializer(
                    item["content"],
                    context=self.get_serializer_context(),
                ).data
            else:
                content = EditorialArticleCardSerializer(
                    item["content"],
                    context=self.get_serializer_context(),
                ).data

            results.append(
                {
                    "content_type": item["content_type"],
                    "favorited_at": item["favorited_at"],
                    "content": content,
                }
            )

        return Response(
            {
                "count": count,
                "next": (
                    self._page_url(
                        page + 1,
                        page_size,
                        favorite_type,
                    )
                    if offset + page_size < count
                    else None
                ),
                "previous": (
                    self._page_url(
                        page - 1,
                        page_size,
                        favorite_type,
                    )
                    if page > 1
                    else None
                ),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_positive_integer(value, *, parameter):
        try:
            number = int(value)
        except (TypeError, ValueError):
            raise ValidationError(
                {parameter: "Enter a valid positive integer."}
            )

        if number < 1:
            raise ValidationError(
                {parameter: "Enter a valid positive integer."}
            )

        return number

    def _get_page_size(self, value):
        if value is None:
            return self.pagination_class.page_size

        page_size = self._get_positive_integer(
            value,
            parameter="page_size",
        )

        return min(
            page_size,
            self.pagination_class.max_page_size,
        )

    def _page_url(self, page, page_size, favorite_type):
        query_params = self.request.query_params.copy()
        query_params["page"] = str(page)
        query_params["page_size"] = str(page_size)

        if favorite_type:
            query_params["type"] = favorite_type
        else:
            query_params.pop("type", None)

        url = self.request.build_absolute_uri(
            self.request.path,
        )

        return f"{url}?{urlencode(query_params, doseq=True)}"
