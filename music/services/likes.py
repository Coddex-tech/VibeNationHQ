from django.db import IntegrityError, models, transaction

from rest_framework.exceptions import ValidationError

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


# ============================================================
# EDITORIAL ARTICLE LIKES
# ============================================================

class EditorialArticleLikeService:
    """
    Business logic for users liking editorial articles.
    """

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user,
        article: EditorialArticle,
    ) -> EditorialArticleLike:
        """
        Like an editorial article.

        The article must be published.
        A user can only like an article once.
        """

        if article.status != EditorialArticle.Status.PUBLISHED:
            raise ValidationError(
                "You can only like published articles."
            )

        if EditorialArticleLike.objects.filter(
            user=user,
            article=article,
        ).exists():
            raise ValidationError(
                "You have already liked this article."
            )

        try:
            like = EditorialArticleLike.objects.create(
                user=user,
                article=article,
            )
        except IntegrityError:
            raise ValidationError(
                "You have already liked this article."
            )

        EditorialArticle.objects.filter(
            pk=article.pk,
        ).update(
            likes_count=models.F("likes_count") + 1,
        )

        return like

    @staticmethod
    @transaction.atomic
    def delete(
        *,
        like_instance: EditorialArticleLike,
    ) -> None:
        """
        Remove an article like and decrement likes_count.
        """

        article_id = like_instance.article_id

        deleted, _ = EditorialArticleLike.objects.filter(
            pk=like_instance.pk,
        ).delete()

        if not deleted:
            return

        EditorialArticle.objects.filter(
            pk=article_id,
            likes_count__gt=0,
        ).update(
            likes_count=models.F("likes_count") - 1,
        )


# ============================================================
# COMMUNITY POST LIKES
# ============================================================

class CommunityPostLikeService:
    """
    Business logic for users liking community posts.
    """

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user,
        post: CommunityPost,
    ) -> CommunityPostLike:
        """
        Like a community post.

        The post must be published.
        A user can only like a post once.
        """

        if post.status != CommunityPost.Status.PUBLISHED:
            raise ValidationError(
                "You can only like published posts."
            )

        if CommunityPostLike.objects.filter(
            user=user,
            post=post,
        ).exists():
            raise ValidationError(
                "You have already liked this post."
            )

        try:
            like = CommunityPostLike.objects.create(
                user=user,
                post=post,
            )
        except IntegrityError:
            raise ValidationError(
                "You have already liked this post."
            )

        CommunityPost.objects.filter(
            pk=post.pk,
        ).update(
            likes_count=models.F("likes_count") + 1,
        )

        return like

    @staticmethod
    @transaction.atomic
    def delete(
        *,
        like_instance: CommunityPostLike,
    ) -> None:
        """
        Remove a post like and decrement likes_count.
        """

        post_id = like_instance.post_id

        deleted, _ = CommunityPostLike.objects.filter(
            pk=like_instance.pk,
        ).delete()

        if not deleted:
            return

        CommunityPost.objects.filter(
            pk=post_id,
            likes_count__gt=0,
        ).update(
            likes_count=models.F("likes_count") - 1,
        )


# ============================================================
# EDITORIAL COMMENT LIKES
# ============================================================

class EditorialCommentLikeService:
    """
    Business logic for users liking editorial comments.
    """

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user,
        comment: EditorialComment,
    ) -> EditorialCommentLike:
        """
        Like an editorial comment.

        The comment and its article must both be published.
        A user can only like a comment once.
        """

        if comment.status != EditorialComment.Status.PUBLISHED:
            raise ValidationError(
                "You can only like published comments."
            )

        if comment.article.status != EditorialArticle.Status.PUBLISHED:
            raise ValidationError(
                "You can only like comments on published articles."
            )

        if EditorialCommentLike.objects.filter(
            user=user,
            comment=comment,
        ).exists():
            raise ValidationError(
                "You have already liked this comment."
            )

        try:
            like = EditorialCommentLike.objects.create(
                user=user,
                comment=comment,
            )
        except IntegrityError:
            raise ValidationError(
                "You have already liked this comment."
            )

        EditorialComment.objects.filter(
            pk=comment.pk,
        ).update(
            likes_count=models.F("likes_count") + 1,
        )

        return like

    @staticmethod
    @transaction.atomic
    def delete(
        *,
        like_instance: EditorialCommentLike,
    ) -> None:
        """
        Remove an editorial comment like.
        """

        comment_id = like_instance.comment_id

        deleted, _ = EditorialCommentLike.objects.filter(
            pk=like_instance.pk,
        ).delete()

        if not deleted:
            return

        EditorialComment.objects.filter(
            pk=comment_id,
            likes_count__gt=0,
        ).update(
            likes_count=models.F("likes_count") - 1,
        )


# ============================================================
# COMMUNITY POST COMMENT LIKES
# ============================================================

class CommunityPostCommentLikeService:
    """
    Business logic for users liking community post comments.
    """

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user,
        comment: CommunityPostComment,
    ) -> CommunityPostCommentLike:
        """
        Like a community post comment.

        The comment and its post must both be published.
        A user can only like a comment once.
        """

        if comment.status != CommunityPostComment.Status.PUBLISHED:
            raise ValidationError(
                "You can only like published comments."
            )

        if comment.post.status != CommunityPost.Status.PUBLISHED:
            raise ValidationError(
                "You can only like comments on published posts."
            )

        if CommunityPostCommentLike.objects.filter(
            user=user,
            comment=comment,
        ).exists():
            raise ValidationError(
                "You have already liked this comment."
            )

        try:
            like = CommunityPostCommentLike.objects.create(
                user=user,
                comment=comment,
            )
        except IntegrityError:
            raise ValidationError(
                "You have already liked this comment."
            )

        CommunityPostComment.objects.filter(
            pk=comment.pk,
        ).update(
            likes_count=models.F("likes_count") + 1,
        )

        return like

    @staticmethod
    @transaction.atomic
    def delete(
        *,
        like_instance: CommunityPostCommentLike,
    ) -> None:
        """
        Remove a community post comment like.
        """

        comment_id = like_instance.comment_id

        deleted, _ = CommunityPostCommentLike.objects.filter(
            pk=like_instance.pk,
        ).delete()

        if not deleted:
            return

        CommunityPostComment.objects.filter(
            pk=comment_id,
            likes_count__gt=0,
        ).update(
            likes_count=models.F("likes_count") - 1,
        )