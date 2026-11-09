from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import (
    BooleanField,
    Case,
    Count,
    Exists,
    ExpressionWrapper,
    F,
    FloatField,
    OuterRef,
    Prefetch,
    Value,
    When,
    Q,
)

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from datetime import timedelta

from music.api.pagination import (
    MusicPagination,
    CommunityCommentThreadPagination,
)
from accounts.api.permissions import (
    IsOrdinaryVibeNationUser,
    IsOrdinaryVibeNationUserOrReadOnly,
)

from music.models import (
    CommunityPost,
    CommunityPostComment,
    CommunityPostCommentLike,
    CommunityPostFavorite,
    CommunityPostLike,
    CommunityPostTarget,
    UserFollow,
)

from music.serializers.community import (
    CommunityPostCommentCreateSerializer,
    CommunityPostCommentSerializer,
    CommunityPostCommentUpdateSerializer,
    CommunityPostCreateSerializer,
    CommunityPostSerializer,
    CommunityPostUpdateSerializer,
    CommunityPostReportCreateSerializer,
    CommunityPostReportSerializer,
    CommunityPostCommentReportCreateSerializer,
    CommunityPostCommentReportSerializer,
)

from music.services.community import (
    CommunityPostService,
    CommunityPostCommentService,
    CommunityPostFavoriteService,
    CommunityPostReportService,
    CommunityPostCommentReportService,
)

from music.services.feed_interactions import (
    MusicFeedInteractionService,
)

from music.api.permissions import IsOwner


User = get_user_model()


class CommunityPostListCreateAPIView(
    generics.ListCreateAPIView
):
    """
    List published community posts or create a new
    community post.
    """

    permission_classes = [
        IsOrdinaryVibeNationUserOrReadOnly,
    ]

    pagination_class = MusicPagination

    def get_queryset(self):
        """
        Return published community posts with the current
        user's like/favorite state and total favorite count
        efficiently annotated.

        The is_liked and is_favorited annotations use EXISTS
        rather than separate queries for every post, preventing
        N+1 queries.

        favorites_count is calculated dynamically from the
        CommunityPostFavorite relationship.

        Song provider identities are also prefetched so
        canonical song targets can expose their provider
        preview URL without additional queries.
        """

        author_queryset = User.objects.all()

        if self.request.user.is_authenticated:
            author_follows = UserFollow.objects.filter(
                follower=self.request.user,
                following_id=OuterRef("pk"),
            )

            author_queryset = author_queryset.annotate(
                is_following=Exists(
                    author_follows,
                ),
            )
        else:
            author_queryset = author_queryset.annotate(
                is_following=Value(
                    False,
                    output_field=BooleanField(),
                ),
            )

        queryset = (
            CommunityPost.objects
            .filter(
                status=CommunityPost.Status.PUBLISHED,
            )
            .select_related(
                "target",
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
                "target__artist",
            )
            .annotate(
                favorites_count=Count(
                    "favorites",
                    distinct=True,
                ),
            )
        )

        if self.request.user.is_authenticated:
            liked_posts = CommunityPostLike.objects.filter(
                user=self.request.user,
                post_id=OuterRef("pk"),
            )

            favorited_posts = CommunityPostFavorite.objects.filter(
                user=self.request.user,
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

        # ----------------------------------------------------
        # Optional song / album / artist filtering
        # ----------------------------------------------------

        target_filters = self.get_target_filters()

        if target_filters is not None:
            target_type, target_id = target_filters

            queryset = queryset.filter(
                target__target_type=target_type,
            )

            if target_type == CommunityPostTarget.TargetType.SONG:
                queryset = queryset.filter(
                    target__song_id=target_id,
                )

            elif target_type == CommunityPostTarget.TargetType.ALBUM:
                queryset = queryset.filter(
                    target__album_id=target_id,
                )

            elif target_type == CommunityPostTarget.TargetType.ARTIST:
                queryset = queryset.filter(
                    target__artist_id=target_id,
                )

        # ----------------------------------------------------
        # Latest / Relevant ordering
        # ----------------------------------------------------

        ordering = self.request.query_params.get(
            "ordering",
            "latest",
        ).strip().lower()

        if ordering not in {"latest", "relevant"}:
            raise ValidationError({
                "ordering": (
                    "Choose either 'latest' or 'relevant'."
                ),
            })

        if ordering == "latest":
            return queryset.order_by(
                "-created_at",
                "-pk",
            )

        # Relevant ranking:
        #
        # Likes:       3 points each
        # Comments:    5 points each
        # Views:       0.1 points each
        #
        # Recency bonus:
        # Last 24 hours: 20 points
        # Last 7 days:   10 points
        # Last 30 days:   3 points
        #
        # These are initial tunable weights, not a claim
        # that they are a universally optimal ranking.

        now = timezone.now()

        queryset = queryset.annotate(
            _engagement_score=ExpressionWrapper(
                F("likes_count") * Value(3.0)
                + F("comments_count") * Value(5.0)
                + F("views_count") * Value(0.1),
                output_field=FloatField(),
            ),
        )

        queryset = queryset.annotate(
            _recency_score=Case(
                When(
                    created_at__gte=now - timedelta(days=1),
                    then=Value(20.0),
                ),
                When(
                    created_at__gte=now - timedelta(days=7),
                    then=Value(10.0),
                ),
                When(
                    created_at__gte=now - timedelta(days=30),
                    then=Value(3.0),
                ),
                default=Value(0.0),
                output_field=FloatField(),
            ),
        )

        queryset = queryset.annotate(
            _relevance_score=ExpressionWrapper(
                F("_engagement_score")
                + F("_recency_score"),
                output_field=FloatField(),
            ),
        )

        return queryset.order_by(
            "-_relevance_score",
            "-created_at",
            "-pk",
        )

    def get_target_filters(self):
        """
        Validate optional target filters for song, album,
        and artist community-post lists.

        Both target_type and target_id must be supplied
        together. If neither is supplied, the endpoint
        returns the general community feed.
        """

        target_type = self.request.query_params.get(
            "target_type",
        )
        target_id = self.request.query_params.get(
            "target_id",
        )

        if not target_type and not target_id:
            return None

        if not target_type or not target_id:
            raise ValidationError({
                "target": (
                    "Both target_type and target_id "
                    "must be supplied together."
                ),
            })

        allowed_types = {
            CommunityPostTarget.TargetType.SONG,
            CommunityPostTarget.TargetType.ALBUM,
            CommunityPostTarget.TargetType.ARTIST,
        }

        if target_type not in allowed_types:
            raise ValidationError({
                "target_type": (
                    "Choose song, album, or artist."
                ),
            })

        if not target_id.isdigit() or int(target_id) < 1:
            raise ValidationError({
                "target_id": (
                    "A positive numeric target ID is required."
                ),
            })

        return target_type, int(target_id)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommunityPostCreateSerializer

        return CommunityPostSerializer

    def create(self, request, *args, **kwargs):
        """
        Validate the incoming post data, create the post
        through the service layer, then return the complete
        read representation.
        """

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        post = CommunityPostService.create(
            user=request.user,
            content=serializer.validated_data["content"],
            rating=serializer.validated_data.get(
                "rating",
            ),
            target_data=serializer.validated_data.get(
                "target",
            ),
        )

        # Reload the object using the same optimized queryset
        # used by the feed so the response has all required
        # related objects available, including is_liked,
        # is_favorited, favorites_count, and the prefetched
        # provider preview URL.
        post = (
            self.get_queryset()
            .get(pk=post.pk)
        )

        output_serializer = CommunityPostSerializer(
            post,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class CommunityPostViewAPIView(generics.GenericAPIView):
    """
    Record a view of a published community post.

    Only authenticated ordinary users can record views.

    The post owner does not generate recommendation-history
    events from viewing their own post.

    The existing view-count behavior is preserved:
    an owner's reload does not add another view.
    """

    permission_classes = [
        IsOrdinaryVibeNationUser,
    ]

    def post(self, request, *args, **kwargs):
        post = CommunityPost.objects.filter(
            pk=kwargs.get("pk"),
            status=CommunityPost.Status.PUBLISHED,
        ).first()

        if post is None:
            return Response(
                {"detail": "Community post not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        navigation_type = request.data.get("navigation_type")

        is_owner = post.user_id == request.user.pk

        # Preserve existing behavior: an owner's reload
        # does not increase the post's view count.
        if is_owner and navigation_type == "reload":
            return Response(
                {
                    "views_count": post.views_count,
                    "counted": False,
                },
                status=status.HTTP_200_OK,
            )

        with transaction.atomic():
            views_count = CommunityPostService.record_view(
                post=post,
            )

            if views_count is None:
                return Response(
                    {"detail": "Community post not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Do not use the creator's own views to personalize
            # recommendations for that creator.
            if not is_owner:
                MusicFeedInteractionService.record_community_post_view(
                    user=request.user,
                    post=post,
                )

        return Response(
            {
                "views_count": views_count,
                "counted": True,
            },
            status=status.HTTP_200_OK,
        )


class CommunityPostDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update, or delete a community post.
    """

    lookup_field = "pk"

    def get_queryset(self):
        """
        Return the requested published community post with
        the current user's like/favorite state and total
        favorite count efficiently annotated.

        Song provider identities are also prefetched so
        canonical song targets can expose their provider
        preview URL without additional queries.
        """

        author_queryset = User.objects.all()

        if self.request.user.is_authenticated:
            author_follows = UserFollow.objects.filter(
                follower=self.request.user,
                following_id=OuterRef("pk"),
            )

            author_queryset = author_queryset.annotate(
                is_following=Exists(
                    author_follows,
                ),
            )
        else:
            author_queryset = author_queryset.annotate(
                is_following=Value(
                    False,
                    output_field=BooleanField(),
                ),
            )

        queryset = (
            CommunityPost.objects
            .filter(
                status=CommunityPost.Status.PUBLISHED,
            )
            .select_related(
                "target",
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
                "target__artist",
            )
            .annotate(
                favorites_count=Count(
                    "favorites",
                    distinct=True,
                ),
            )
        )

        if self.request.user.is_authenticated:
            liked_posts = CommunityPostLike.objects.filter(
                user=self.request.user,
                post_id=OuterRef("pk"),
            )

            favorited_posts = CommunityPostFavorite.objects.filter(
                user=self.request.user,
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

        return queryset

    def get_permissions(self):
        if self.request.method in [
            "PUT",
            "PATCH",
            "DELETE",
        ]:
            return [
                IsOrdinaryVibeNationUser(),
                IsOwner(),
            ]
        return [
            IsAuthenticatedOrReadOnly(),
        ]

    def get_serializer_class(self):
        if self.request.method in [
            "PUT",
            "PATCH",
        ]:
            return CommunityPostUpdateSerializer

        return CommunityPostSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop(
            "partial",
            False,
        )

        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        content = serializer.validated_data.get(
            "content",
            instance.content,
        )

        rating = serializer.validated_data.get(
            "rating",
            instance.rating,
        )

        post = CommunityPostService.update(
            post=instance,
            content=content,
            rating=rating,
        )

        # Reload the object using the optimized queryset
        # so the response contains all required related data,
        # including the current user's like/favorite states,
        # favorite count, and the prefetched provider preview URL.
        post = (
            self.get_queryset()
            .get(pk=post.pk)
        )

        output_serializer = CommunityPostSerializer(
            post,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        CommunityPostService.delete(
            post=instance,
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class CommunityPostFavoriteAPIView(
    generics.GenericAPIView
):
    """
    Favorite or unfavorite a published community post.
    """

    queryset = CommunityPost.objects.filter(
        status=CommunityPost.Status.PUBLISHED,
    )

    permission_classes = [
        IsOrdinaryVibeNationUser,
    ]

    def post(self, request, *args, **kwargs):
        post = self.get_object()

        with transaction.atomic():
            CommunityPostFavoriteService.create(
                user=request.user,
                post=post,
            )

            MusicFeedInteractionService.record_community_post_favorite(
                user=request.user,
                post=post,
            )

            favorites_count = (
                CommunityPostFavorite.objects
                .filter(
                    post_id=post.pk,
                )
                .count()
            )

        return Response(
            {
                "favorited": True,
                "favorites_count": favorites_count,
            },
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        post = self.get_object()

        CommunityPostFavoriteService.delete(
            user=request.user,
            post=post,
        )

        favorites_count = (
            CommunityPostFavorite.objects
            .filter(
                post_id=post.pk,
            )
            .count()
        )

        return Response(
            {
                "favorited": False,
                "favorites_count": favorites_count,
            },
            status=status.HTTP_200_OK,
        )


class CommunityPostCommentListCreateAPIView(
    generics.ListCreateAPIView
):
    """
    List comments for a published community post
    or create a new comment/reply.
    """

    pagination_class = MusicPagination

    def get_queryset(self):
        queryset = (
            CommunityPostComment.objects
            .filter(
                post_id=self.kwargs["post_id"],
                post__status=CommunityPost.Status.PUBLISHED,
                status=CommunityPostComment.Status.PUBLISHED,
            )
            .select_related(
                "user",
                "post",
                "parent",
            )
            .order_by("created_at")
        )

        if self.request.user.is_authenticated:
            liked_comments = CommunityPostCommentLike.objects.filter(
                user=self.request.user,
                comment_id=OuterRef("pk"),
            )

            queryset = queryset.annotate(
                is_liked=Exists(
                    liked_comments,
                ),
            )
        else:
            queryset = queryset.annotate(
                is_liked=Value(
                    False,
                    output_field=BooleanField(),
                ),
            )

        queryset = queryset.annotate(
            thread_replies_count=Count(
                "thread_replies",
                filter=Q(
                    thread_replies__status=(
                        CommunityPostComment.Status.PUBLISHED
                    ),
                    thread_replies__post__status=(
                        CommunityPost.Status.PUBLISHED
                    ),
                ),
            )
        )

        parent_id = self.request.query_params.get("parent")

        if parent_id:
            queryset = queryset.filter(
                parent_id=parent_id,
            )
        else:
            queryset = queryset.filter(
                parent__isnull=True,
            )
        return queryset

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsOrdinaryVibeNationUser(),
            ]
        return []

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommunityPostCommentCreateSerializer
        return CommunityPostCommentSerializer

    def create(self, request, *args, **kwargs):
        """
        Validate the incoming comment data and ensure the submitted
        post matches the post specified in the URL.

        Create the comment and record its interaction history
        atomically, then return its complete serialized representation.
        """

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        # The URL determines which post this endpoint targets.
        # Do not allow the request body to specify a different post.
        url_post_id = self.kwargs["post_id"]
        submitted_post = serializer.validated_data["post"]

        if str(submitted_post.pk) != str(url_post_id):
            raise ValidationError(
                {
                    "post": (
                        "The submitted post does not match "
                        "the post specified in the URL."
                    ),
                },
            )

        # Create the comment and record its interaction together.
        with transaction.atomic():
            comment = CommunityPostCommentService.create(
                user=request.user,
                post=submitted_post,
                parent=serializer.validated_data.get("parent"),
                content=serializer.validated_data["content"],
            )

            MusicFeedInteractionService.record_community_post_comment(
                user=request.user,
                post=comment.post,
            )

        # Reload the new comment independently of get_queryset().
        # get_queryset() applies list-specific filters, including
        # parent__isnull=True for top-level comments.
        liked_comments = CommunityPostCommentLike.objects.filter(
            user=request.user,
            comment_id=OuterRef("pk"),
        )

        comment = (
            CommunityPostComment.objects
            .filter(
                pk=comment.pk,
                post__status=CommunityPost.Status.PUBLISHED,
                status=CommunityPostComment.Status.PUBLISHED,
            )
            .select_related(
                "user",
                "post",
                "parent",
            )
            .annotate(
                is_liked=Exists(
                    liked_comments,
                ),
            )
            .get()
        )

        output_serializer = CommunityPostCommentSerializer(
            comment,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class CommunityPostCommentThreadAPIView(
    generics.ListAPIView
):
    """
    Paginated list of all published descendants of a root
    community comment.

    Unlike the ordinary comments endpoint, this endpoint
    includes replies at every nesting level.

    The response count represents all published descendants
    of the root comment.
    """

    serializer_class = CommunityPostCommentSerializer
    pagination_class = CommunityCommentThreadPagination
    permission_classes = []

    def get_queryset(self):
        post_id = self.kwargs["post_id"]
        root_comment_id = self.kwargs["root_comment_id"]

        # Confirm that the requested root is a published,
        # top-level comment belonging to this published post.
        root_comment = get_object_or_404(
            CommunityPostComment.objects.filter(
                post_id=post_id,
                parent__isnull=True,
                status=CommunityPostComment.Status.PUBLISHED,
                post__status=CommunityPost.Status.PUBLISHED,
            ),
            pk=root_comment_id,
        )

        queryset = (
            CommunityPostComment.objects
            .filter(
                post_id=post_id,
                root_comment_id=root_comment.pk,
                status=CommunityPostComment.Status.PUBLISHED,
                post__status=CommunityPost.Status.PUBLISHED,
            )
            .select_related(
                "user",
                "post",
                "parent",
                "root_comment",
            )
            .order_by("created_at", "pk")
        )

        # Preserve the current user's like state without
        # issuing a separate like query for each reply.
        if self.request.user.is_authenticated:
            liked_comments = CommunityPostCommentLike.objects.filter(
                user=self.request.user,
                comment_id=OuterRef("pk"),
            )

            queryset = queryset.annotate(
                is_liked=Exists(liked_comments),
            )
        else:
            queryset = queryset.annotate(
                is_liked=Value(
                    False,
                    output_field=BooleanField(),
                ),
            )
        return queryset


class CommunityPostCommentDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update, or soft-delete a community comment.
    """

    lookup_field = "pk"

    def get_queryset(self):
        queryset = (
            CommunityPostComment.objects
            .filter(
                status=CommunityPostComment.Status.PUBLISHED,
                post__status=CommunityPost.Status.PUBLISHED,
            )
            .select_related(
                "user",
                "post",
                "parent",
            )
            .order_by("created_at")
        )

        if self.request.user.is_authenticated:
            liked_comments = CommunityPostCommentLike.objects.filter(
                user=self.request.user,
                comment_id=OuterRef("pk"),
            )

            queryset = queryset.annotate(
                is_liked=Exists(
                    liked_comments,
                ),
            )
        else:
            queryset = queryset.annotate(
                is_liked=Value(
                    False,
                    output_field=BooleanField(),
                ),
            )

        return queryset

    def get_permissions(self):
        if self.request.method in [
            "PUT",
            "PATCH",
            "DELETE",
        ]:
            return [
                IsOrdinaryVibeNationUser(),
                IsOwner(),
            ]

        return [
            IsAuthenticatedOrReadOnly(),
        ]

    def get_serializer_class(self):
        if self.request.method in [
            "PUT",
            "PATCH",
        ]:
            return CommunityPostCommentUpdateSerializer

        return CommunityPostCommentSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop(
            "partial",
            False,
        )

        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        content = serializer.validated_data.get(
            "content",
            instance.content,
        )

        comment = CommunityPostCommentService.update(
            comment=instance,
            content=content,
        )

        # Reload so the response contains the current user's
        # like state and the post creator's ID.
        comment = (
            self.get_queryset()
            .get(pk=comment.pk)
        )

        output_serializer = CommunityPostCommentSerializer(
            comment,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        CommunityPostCommentService.delete(
            comment=instance,
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class CommunityPostReportAPIView(
    generics.GenericAPIView
):
    """
    Report a published community post.
    """

    queryset = CommunityPost.objects.filter(
        status=CommunityPost.Status.PUBLISHED,
    )

    permission_classes = [
        IsOrdinaryVibeNationUser,
    ]

    def post(self, request, *args, **kwargs):
        post = self.get_object()

        serializer = CommunityPostReportCreateSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )

        serializer.is_valid(
            raise_exception=True,
        )

        report = CommunityPostReportService.create(
            user=request.user,
            post=post,
            reason=serializer.validated_data["reason"],
            details=serializer.validated_data.get(
                "details",
                "",
            ),
        )

        output_serializer = CommunityPostReportSerializer(
            report,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class CommunityPostCommentReportAPIView(
    generics.GenericAPIView
):
    """
    Report a published community post comment.
    """

    queryset = (
        CommunityPostComment.objects
        .filter(
            status=CommunityPostComment.Status.PUBLISHED,
            post__status=CommunityPost.Status.PUBLISHED,
        )
    )

    permission_classes = [
        IsOrdinaryVibeNationUser,
    ]

    def post(self, request, *args, **kwargs):
        comment = self.get_object()

        serializer = CommunityPostCommentReportCreateSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )

        serializer.is_valid(
            raise_exception=True,
        )

        report = CommunityPostCommentReportService.create(
            user=request.user,
            comment=comment,
            reason=serializer.validated_data["reason"],
            details=serializer.validated_data.get(
                "details",
                "",
            ),
        )

        output_serializer = CommunityPostCommentReportSerializer(
            report,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )