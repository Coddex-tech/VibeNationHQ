from django.contrib.auth import get_user_model
from django.db.models import (
    BooleanField,
    Count,
    Exists,
    OuterRef,
    Prefetch,
    Value,
)

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from music.api.pagination import MusicPagination

from music.models import (
    CommunityPost,
    CommunityPostComment,
    CommunityPostCommentLike,
    CommunityPostFavorite,
    CommunityPostLike,
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
        IsAuthenticatedOrReadOnly,
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
            .order_by("-created_at")
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

    Only authenticated users can record views.
    The post owner does not receive another view when
    refreshing the same page.
    """

    permission_classes = [IsAuthenticated]

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

        # A reload must not add another view for the post owner.
        # Other authenticated users can still receive a view
        # when they refresh the page.
        if is_owner and navigation_type == "reload":
            return Response(
                {
                    "views_count": post.views_count,
                    "counted": False,
                },
                status=status.HTTP_200_OK,
            )

        views_count = CommunityPostService.record_view(
            post=post,
        )

        if views_count is None:
            return Response(
                {"detail": "Community post not found."},
                status=status.HTTP_404_NOT_FOUND,
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
                IsAuthenticatedOrReadOnly(),
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


class CommunityPostFavoriteListAPIView(
    generics.ListAPIView
):
    """
    List the authenticated user's favorited community posts.

    Favorites are ordered by when they were saved, with the
    most recently favorited post first.

    The same CommunityPostSerializer used by the feed is returned,
    so favorite posts have the same representation as feed posts.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    pagination_class = MusicPagination

    serializer_class = CommunityPostSerializer

    def get_queryset(self):
        return (
            CommunityPostFavoriteService.get_user_favorites(
                user=self.request.user,
            )
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
        IsAuthenticatedOrReadOnly,
    ]

    def post(self, request, *args, **kwargs):
        post = self.get_object()

        CommunityPostFavoriteService.create(
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
                IsAuthenticatedOrReadOnly(),
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

        Create the comment through the service layer, then retrieve
        and return its complete serialized representation.
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

        # Create the comment or reply through the service layer.
        # The authenticated user is explicitly passed to the service.
        comment = CommunityPostCommentService.create(
            user=request.user,
            post=submitted_post,
            parent=serializer.validated_data.get("parent"),
            content=serializer.validated_data["content"],
        )

        # Record the interaction after successful comment creation.
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

        # Serialize the complete comment representation.
        output_serializer = CommunityPostCommentSerializer(
            comment,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )


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
                IsAuthenticatedOrReadOnly(),
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
        IsAuthenticatedOrReadOnly,
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
        IsAuthenticatedOrReadOnly,
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