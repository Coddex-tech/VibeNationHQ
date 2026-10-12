from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from music.models import (
    EditorialArticle,
    EditorialArticleLike,
    CommunityPost,
    CommunityPostLike,
    EditorialComment,
    EditorialCommentLike,
    CommunityPostComment,
    CommunityPostCommentLike,
)

from music.services.likes import (
    EditorialArticleLikeService,
    CommunityPostLikeService,
    EditorialCommentLikeService,
    CommunityPostCommentLikeService,
)

from music.services.feed_interactions import (
    MusicFeedInteractionService,
)


# ============================================================
# EDITORIAL ARTICLE LIKE
# ============================================================

class EditorialArticleLikeAPIView(generics.GenericAPIView):
    """
    Like or unlike an editorial article.

    POST   -> like article
    DELETE -> unlike article
    """

    queryset = EditorialArticle.objects.filter(
        status=EditorialArticle.Status.PUBLISHED,
    )
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        article = self.get_object()

        EditorialArticleLikeService.create(
            user=request.user,
            article=article,
        )

        # Record the successful like as feed history.
        MusicFeedInteractionService.record_editorial_like(
            user=request.user,
            article=article,
        )

        article.refresh_from_db()

        return Response(
            {
                "liked": True,
                "likes_count": article.likes_count,
            },
            status=201,
        )

    def delete(self, request, *args, **kwargs):
        article = self.get_object()

        like = EditorialArticleLike.objects.filter(
            user=request.user,
            article=article,
        ).first()

        if like is None:
            return Response(
                {
                    "liked": False,
                    "likes_count": article.likes_count,
                },
                status=200,
            )

        EditorialArticleLikeService.delete(
            like_instance=like,
        )

        article.refresh_from_db()

        return Response(
            {
                "liked": False,
                "likes_count": article.likes_count,
            },
            status=200,
        )


# ============================================================
# COMMUNITY POST LIKE
# ============================================================

class CommunityPostLikeAPIView(generics.GenericAPIView):
    """
    Like or unlike a community post.

    POST   -> like post
    DELETE -> unlike post
    """

    queryset = CommunityPost.objects.filter(
        status=CommunityPost.Status.PUBLISHED,
    )
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        post = self.get_object()

        CommunityPostLikeService.create(
            user=request.user,
            post=post,
        )

        # Record the successful like as feed history.
        MusicFeedInteractionService.record_community_post_like(
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


# ============================================================
# EDITORIAL COMMENT LIKE
# ============================================================

class EditorialCommentLikeAPIView(generics.GenericAPIView):
    """
    Like or unlike an editorial comment or reply.

    POST   -> like comment
    DELETE -> unlike comment
    """

    queryset = (
        EditorialComment.objects
        .filter(
            status=EditorialComment.Status.PUBLISHED,
            article__status=EditorialArticle.Status.PUBLISHED,
        )
        .select_related("article")
    )
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        comment = self.get_object()

        EditorialCommentLikeService.create(
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

        like = EditorialCommentLike.objects.filter(
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

        EditorialCommentLikeService.delete(
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


# ============================================================
# COMMUNITY POST COMMENT LIKE
# ============================================================

class CommunityPostCommentLikeAPIView(generics.GenericAPIView):
    """
    Like or unlike a community post comment or reply.

    POST   -> like comment
    DELETE -> unlike comment
    """

    queryset = (
        CommunityPostComment.objects
        .filter(
            status=CommunityPostComment.Status.PUBLISHED,
            post__status=CommunityPost.Status.PUBLISHED,
        )
        .select_related("post")
    )
    permission_classes = [IsAuthenticatedOrReadOnly]

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