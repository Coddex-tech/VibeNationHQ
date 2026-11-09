from __future__ import annotations

from django.db.models import (
    BooleanField,
    Count,
    Exists,
    OuterRef,
    Q,
    F,
    Value,
)

from django.db import (
    transaction,
    IntegrityError,
)
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.exceptions import NotFound
from rest_framework import generics, status
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from music.api.pagination import (
    MusicPagination,
    EditorialCommentThreadPagination,
)
from music.api.permissions import IsOwner

from music.models import (
    EditorialArticle,
    EditorialArticleLike,
    EditorialArticleFavorite,
    EditorialComment,
    EditorialCommentLike,
    ContentDailyView,
)
from music.serializers.editorial import (
    EditorialArticleCardSerializer,
    EditorialArticleReportCreateSerializer,
    EditorialArticleReportSerializer,
    EditorialArticleSerializer,
    EditorialCommentCreateSerializer,
    EditorialCommentReportCreateSerializer,
    EditorialCommentReportSerializer,
    EditorialCommentSerializer,
    EditorialCommentUpdateSerializer,
)
from music.services.editorial import (
    EditorialArticleReportService,
    EditorialCommentReportService,
    EditorialCommentService,
)


# ============================================================
# EDITORIAL ARTICLE
# ============================================================

class EditorialArticleListAPIView(
    generics.ListAPIView,
):
    """
    Public list of published editorial articles.
    """

    serializer_class = EditorialArticleCardSerializer
    pagination_class = MusicPagination

    def get_queryset(self):
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
                "-published_at",
                "-created_at",
                "pk",
            )
        )

        return self._annotate_engagement_state(queryset)

    def _annotate_engagement_state(self, queryset):
        if not self.request.user.is_authenticated:
            return queryset.annotate(
                user_has_liked=Value(
                    False,
                    output_field=BooleanField(),
                ),
                user_has_favorited=Value(
                    False,
                    output_field=BooleanField(),
                ),
            )

        user_likes = EditorialArticleLike.objects.filter(
            user=self.request.user,
            article_id=OuterRef("pk"),
        )

        user_favorites = EditorialArticleFavorite.objects.filter(
            user=self.request.user,
            article_id=OuterRef("pk"),
        )

        return queryset.annotate(
            user_has_liked=Exists(user_likes),
            user_has_favorited=Exists(user_favorites),
        )


class EditorialArticleDetailAPIView(
    generics.RetrieveAPIView,
):
    """
    Public detail endpoint for a published editorial article.
    """

    serializer_class = EditorialArticleSerializer
    lookup_field = "slug"

    def get_queryset(self):
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
        )

        if not self.request.user.is_authenticated:
            return queryset.annotate(
                user_has_liked=Value(
                    False,
                    output_field=BooleanField(),
                ),
                user_has_favorited=Value(
                    False,
                    output_field=BooleanField(),
                ),
            )

        user_likes = EditorialArticleLike.objects.filter(
            user=self.request.user,
            article_id=OuterRef("pk"),
        )

        user_favorites = EditorialArticleFavorite.objects.filter(
            user=self.request.user,
            article_id=OuterRef("pk"),
        )

        return queryset.annotate(
            user_has_liked=Exists(user_likes),
            user_has_favorited=Exists(user_favorites),
        )


class EditorialArticleViewAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    queryset = EditorialArticle.objects.filter(
        status=EditorialArticle.Status.PUBLISHED,
    )

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        article = self.get_object()

        today = timezone.localdate()
        now = timezone.now()

        # Increment the lifetime view count only while the
        # article remains published.
        updated_rows = (
            EditorialArticle.objects
            .filter(
                pk=article.pk,
                status=EditorialArticle.Status.PUBLISHED,
            )
            .update(
                views_count=F("views_count") + 1,
            )
        )

        if updated_rows == 0:
            raise NotFound()

        daily_filter = {
            "editorial_article_id": article.pk,
            "date": today,
        }

        # Increment today's record atomically when it exists.
        daily_updated = ContentDailyView.objects.filter(
            **daily_filter,
        ).update(
            views_count=F("views_count") + 1,
            updated_at=now,
        )

        if daily_updated == 0:
            # Use a savepoint so an expected uniqueness conflict
            # does not break the surrounding transaction.
            try:
                with transaction.atomic():
                    ContentDailyView.objects.create(
                        **daily_filter,
                        views_count=1,
                    )

            except IntegrityError:
                # A concurrent request may have created the
                # same article/date record first.
                daily_record_exists = ContentDailyView.objects.filter(
                    **daily_filter,
                ).exists()

                if not daily_record_exists:
                    # This was not the expected uniqueness race.
                    raise

                daily_updated = ContentDailyView.objects.filter(
                    **daily_filter,
                ).update(
                    views_count=F("views_count") + 1,
                    updated_at=now,
                )

                if daily_updated != 1:
                    raise

        # Keep the existing response shape unchanged.
        article.refresh_from_db(fields=["views_count"])

        return Response({
            "views_count": article.views_count,
        })
    

# ============================================================
# EDITORIAL COMMENTS
# ============================================================
class EditorialCommentListCreateAPIView(
    generics.ListCreateAPIView,
):
    """
    Public list of published comments/replies for an article.

    GET:
        Without ?parent:
            returns top-level comments.

        With ?parent=<comment_id>:
            returns direct replies to that comment.

    POST:
        Creates a new top-level comment or reply.
    """

    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

    pagination_class = MusicPagination

    def get_queryset(self):
        article = self._get_article()

        queryset = (
            EditorialComment.objects
            .filter(
                article=article,
                status=EditorialComment.Status.PUBLISHED,
            )
            .select_related(
                "user",
                "article",
                "parent",
            )
            .annotate(
                thread_replies_count=Count(
                    "thread_replies",
                    filter=Q(
                        thread_replies__status=EditorialComment.Status.PUBLISHED,
                        thread_replies__article_id=article.pk,
                    ),
                    distinct=True,
                ),
            )
            .order_by("created_at", "pk")
        )

        parent_value = self.request.query_params.get(
            "parent",
        )

        if parent_value is None or not parent_value.strip():
            queryset = queryset.filter(
                parent__isnull=True,
            )
        else:
            try:
                parent_id = int(parent_value)
            except (TypeError, ValueError):
                return queryset.none()

            queryset = queryset.filter(
                parent_id=parent_id,
            )

        return self._annotate_like_state(
            queryset,
        )

    def _annotate_like_state(self, queryset):
        if not self.request.user.is_authenticated:
            return queryset.annotate(
                user_has_liked=Value(
                    False,
                    output_field=BooleanField(),
                ),
            )

        user_likes = EditorialCommentLike.objects.filter(
            user=self.request.user,
            comment_id=OuterRef("pk"),
        )

        return queryset.annotate(
            user_has_liked=Exists(user_likes),
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return EditorialCommentCreateSerializer

        return EditorialCommentSerializer

    def _get_article(self):
        return get_object_or_404(
            EditorialArticle.objects.filter(
                status=EditorialArticle.Status.PUBLISHED,
            ),
            pk=self.kwargs["article_id"],
        )

    def perform_create(self, serializer):
        article = self._get_article()

        parent = serializer.validated_data.get(
            "parent",
        )

        comment = EditorialCommentService.create(
            user=self.request.user,
            article=article,
            content=serializer.validated_data[
                "content"
            ],
            parent=parent,
        )

        self._created_comment = comment

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        self.perform_create(serializer)

        response_serializer = EditorialCommentSerializer(
            self._created_comment,
            context=self.get_serializer_context(),
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# EDITORIAL COMMENT THREAD
# ============================================================
class EditorialCommentThreadAPIView(
    generics.ListAPIView,
):
    """
    Paginated list of all published descendants of a
    top-level editorial comment.

    Replies retain their immediate parent relationship,
    allowing the frontend to reconstruct nested threads.
    """

    serializer_class = EditorialCommentSerializer
    pagination_class = EditorialCommentThreadPagination
    permission_classes = []

    def get_queryset(self):
        article = get_object_or_404(
            EditorialArticle.objects.filter(
                status=EditorialArticle.Status.PUBLISHED,
            ),
            pk=self.kwargs["article_id"],
        )

        root_comment = get_object_or_404(
            EditorialComment.objects.filter(
                article=article,
                parent__isnull=True,
                status=EditorialComment.Status.PUBLISHED,
            ),
            pk=self.kwargs["root_comment_id"],
        )

        queryset = (
            EditorialComment.objects
            .filter(
                article=article,
                root_comment_id=root_comment.pk,
                status=EditorialComment.Status.PUBLISHED,
            )
            .select_related(
                "user",
                "article",
                "parent",
                "root_comment",
            )
            .order_by(
                "created_at",
                "pk",
            )
        )

        if not self.request.user.is_authenticated:
            return queryset.annotate(
                user_has_liked=Value(
                    False,
                    output_field=BooleanField(),
                ),
            )

        user_likes = EditorialCommentLike.objects.filter(
            user=self.request.user,
            comment_id=OuterRef("pk"),
        )

        return queryset.annotate(
            user_has_liked=Exists(user_likes),
        )


class EditorialCommentDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView,
):
    """
    Retrieve, update, or delete an editorial comment.

    Only the comment owner may edit or delete it.
    """

    serializer_class = EditorialCommentSerializer

    lookup_field = "pk"

    def get_queryset(self):
        queryset = (
            EditorialComment.objects
            .filter(
                status=EditorialComment.Status.PUBLISHED,
                article__status=EditorialArticle.Status.PUBLISHED,
            )
            .select_related(
                "user",
                "article",
                "parent",
            )
        )

        if not self.request.user.is_authenticated:
            return queryset.annotate(
                user_has_liked=Value(
                    False,
                    output_field=BooleanField(),
                ),
            )

        user_likes = EditorialCommentLike.objects.filter(
            user=self.request.user,
            comment_id=OuterRef("pk"),
        )

        return queryset.annotate(
            user_has_liked=Exists(user_likes),
        )

    def get_serializer_class(self):
        if self.request.method in {
            "PUT",
            "PATCH",
        }:
            return EditorialCommentUpdateSerializer

        return EditorialCommentSerializer

    def get_permissions(self):
        if self.request.method in {
            "PUT",
            "PATCH",
            "DELETE",
        }:
            return [
                IsAuthenticatedOrReadOnly(),
                IsOwner(),
            ]

        return [
            IsAuthenticatedOrReadOnly(),
        ]

    def perform_update(self, serializer):
        EditorialCommentService.update(
            comment=self.get_object(),
            content=serializer.validated_data[
                "content"
            ],
        )

    def perform_destroy(self, instance):
        EditorialCommentService.delete(
            comment=instance,
        )


# ============================================================
# EDITORIAL ARTICLE REPORT
# ============================================================


class EditorialArticleReportAPIView(
    APIView,
):
    """
    Submit a report against a published editorial article.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, pk):
        article = get_object_or_404(
            EditorialArticle.objects.filter(
                status=EditorialArticle.Status.PUBLISHED,
            ),
            pk=pk,
        )

        serializer = EditorialArticleReportCreateSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        report = EditorialArticleReportService.create(
            user=request.user,
            article=article,
            reason=serializer.validated_data[
                "reason"
            ],
            details=serializer.validated_data.get(
                "details",
                "",
            ),
        )

        response_serializer = EditorialArticleReportSerializer(
            report,
            context={"request": request},
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# EDITORIAL COMMENT REPORT
# ============================================================
class EditorialCommentReportAPIView(
    APIView,
):
    """
    Submit a report against a published editorial comment.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, pk):
        comment = get_object_or_404(
            EditorialComment.objects.filter(
                status=EditorialComment.Status.PUBLISHED,
                article__status=EditorialArticle.Status.PUBLISHED,
            ).select_related(
                "article",
            ),
            pk=pk,
        )

        serializer = EditorialCommentReportCreateSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        report = EditorialCommentReportService.create(
            user=request.user,
            comment=comment,
            reason=serializer.validated_data[
                "reason"
            ],
            details=serializer.validated_data.get(
                "details",
                "",
            ),
        )

        response_serializer = EditorialCommentReportSerializer(
            report,
            context={"request": request},
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )