from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from music.api.pagination import MusicPagination

from music.models import (
    CommunityPost,
    CommunityPostComment,
    CommunityPostLike,
    CommunityPostCommentLike,
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
    CommunityPostCommentService,
    CommunityPostReportService,
    CommunityPostCommentReportService,
)

from music.services.likes import (
    CommunityPostLikeService,
    CommunityPostCommentLikeService,
)

from music.api.permissions import IsOwner


class CommunityPostListCreateAPIView(generics.ListCreateAPIView):
    """
    List published community posts or create a new community post.
    """

    queryset = (
        CommunityPost.objects
        .filter(status=CommunityPost.Status.PUBLISHED)
        .select_related("user", "target")
        .prefetch_related(
            "target__song__artists",
            "target__song__featured_artists",
            "target__album__artists",
            "target__artist",
        )
        .order_by("-created_at")
    )

    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

    pagination_class = MusicPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommunityPostCreateSerializer

        return CommunityPostSerializer


class CommunityPostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a community post.
    """

    queryset = (
        CommunityPost.objects
        .filter(status=CommunityPost.Status.PUBLISHED)
        .select_related("user", "target")
        .prefetch_related(
            "target__song__artists",
            "target__song__featured_artists",
            "target__album__artists",
            "target__artist",
        )
    )

    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [
                IsAuthenticatedOrReadOnly(),
                IsOwner(),
            ]

        return [
            IsAuthenticatedOrReadOnly(),
        ]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return CommunityPostUpdateSerializer

        return CommunityPostSerializer


class CommunityPostCommentListCreateAPIView(generics.ListCreateAPIView):
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
            .select_related("user", "post", "parent")
            .order_by("created_at")
        )

        parent_id = self.request.query_params.get("parent")

        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        else:
            queryset = queryset.filter(parent__isnull=True)

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
        Create a comment/reply through the service layer,
        then return the created object using the read serializer.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = CommunityPostCommentService.create(
            user=request.user,
            post=serializer.validated_data["post"],
            parent=serializer.validated_data.get("parent"),
            content=serializer.validated_data["content"],
        )

        output_serializer = CommunityPostCommentSerializer(
            comment,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=201,
        )


class CommunityPostCommentDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update, or delete a community comment.
    """

    queryset = (
        CommunityPostComment.objects
        .filter(status=CommunityPostComment.Status.PUBLISHED)
        .select_related("user", "post", "parent")
        .order_by("created_at")
    )

    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [
                IsAuthenticatedOrReadOnly(),
                IsOwner(),
            ]

        return [
            IsAuthenticatedOrReadOnly(),
        ]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return CommunityPostCommentUpdateSerializer

        return CommunityPostCommentSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)

        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(raise_exception=True)

        comment = CommunityPostCommentService.update(
            comment=instance,
            content=serializer.validated_data["content"],
        )

        output_serializer = CommunityPostCommentSerializer(
            comment,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=200,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        CommunityPostCommentService.delete(
            comment=instance,
        )

        return Response(
            status=204,
        )


class CommunityPostLikeAPIView(generics.GenericAPIView):
    """
    Like or unlike a published community post.
    """

    queryset = CommunityPost.objects.filter(
        status=CommunityPost.Status.PUBLISHED
    )

    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

    def post(self, request, *args, **kwargs):
        post = self.get_object()

        like = CommunityPostLikeService.create(
            user=request.user,
            post=post,
        )

        post.refresh_from_db()

        return Response(
            {
                "liked": True,
                "likes_count": post.likes_count,
            },
            status=201,
        )

    def delete(self, request, *args, **kwargs):
        post = self.get_object()

        like = CommunityPostLike.objects.filter(
            user=request.user,
            post=post,
        ).first()

        if like is None:
            return Response(
                {
                    "liked": False,
                    "likes_count": post.likes_count,
                },
                status=200,
            )

        CommunityPostLikeService.delete(
            like_instance=like,
        )

        post.refresh_from_db()

        return Response(
            {
                "liked": False,
                "likes_count": post.likes_count,
            },
            status=200,
        )


class CommunityPostCommentLikeAPIView(generics.GenericAPIView):
    """
    Like or unlike a published community post comment.
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

        CommunityPostCommentLikeService.create(
            user=request.user,
            comment=comment,
        )

        comment.refresh_from_db()

        return Response(
            {
                "liked": True,
                "likes_count": comment.likes_count,
            },
            status=201,
        )

    def delete(self, request, *args, **kwargs):
        comment = self.get_object()

        like = CommunityPostCommentLike.objects.filter(
            user=request.user,
            comment=comment,
        ).first()

        if like is None:
            return Response(
                {
                    "liked": False,
                    "likes_count": comment.likes_count,
                },
                status=200,
            )

        CommunityPostCommentLikeService.delete(
            like_instance=like,
        )

        comment.refresh_from_db()

        return Response(
            {
                "liked": False,
                "likes_count": comment.likes_count,
            },
            status=200,
        )


class CommunityPostReportAPIView(generics.GenericAPIView):
    """
    Report a published community post.
    """

    queryset = CommunityPost.objects.filter(
        status=CommunityPost.Status.PUBLISHED
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
        serializer.is_valid(raise_exception=True)

        report = CommunityPostReportService.create(
            user=request.user,
            post=post,
            reason=serializer.validated_data["reason"],
            details=serializer.validated_data.get("details", ""),
        )

        output_serializer = CommunityPostReportSerializer(
            report,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=201,
        )


class CommunityPostCommentReportAPIView(generics.GenericAPIView):
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
        serializer.is_valid(raise_exception=True)

        report = CommunityPostCommentReportService.create(
            user=request.user,
            comment=comment,
            reason=serializer.validated_data["reason"],
            details=serializer.validated_data.get("details", ""),
        )

        output_serializer = CommunityPostCommentReportSerializer(
            report,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=201,
        )