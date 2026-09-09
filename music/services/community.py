from django.db import transaction, models, IntegrityError
from rest_framework.exceptions import ValidationError

from music.models import (
    CommunityPost,
    CommunityPostTarget,
    CommunityPostComment,
    EditorialArticle,
    CommunityPostReport,
    EditorialArticleReport,
    EditorialCommentReport,
    EditorialComment,
    CommunityPostCommentReport,

)


class CommunityPostService:
    @staticmethod
    @transaction.atomic
    def create(*, user, content, rating=None, target_data):
        """
        Create a community post and its target atomically.

        The serializer is responsible for validating target_data.
        This service is responsible for turning that validated data
        into database records.
        """

        post = CommunityPost.objects.create(
            user=user,
            content=content,
            rating=rating,
        )

        CommunityPostService._create_target(
            post=post,
            target_data=target_data,
        )

        return post

    @staticmethod
    def _create_target(*, post, target_data):
        """
        Create the CommunityPostTarget from already validated data.
        """

        target_type = target_data["target_type"]

        if target_type == CommunityPostTarget.TargetType.SONG:
            CommunityPostTarget.objects.create(
                post=post,
                target_type=target_type,
                song=target_data["song"],
            )

        elif target_type == CommunityPostTarget.TargetType.ALBUM:
            CommunityPostTarget.objects.create(
                post=post,
                target_type=target_type,
                album=target_data["album"],
            )

        elif target_type == CommunityPostTarget.TargetType.ARTIST:
            CommunityPostTarget.objects.create(
                post=post,
                target_type=target_type,
                artist=target_data["artist"],
            )

        elif target_type == CommunityPostTarget.TargetType.EXTERNAL:
            raise ValidationError(
                "External music targets are not supported yet."
            )

        else:
            raise ValidationError(
                "Invalid community post target type."
            )

    @staticmethod
    @transaction.atomic
    def update(*, post, content, rating=None):
        """
        Update the editable fields of a community post.

        The target is intentionally immutable.
        """

        post.content = content
        post.rating = rating
        post.is_edited = True

        post.save(
            update_fields=[
                "content",
                "rating",
                "is_edited",
                "updated_at",
            ]
        )

        return post

    @staticmethod
    @transaction.atomic
    def delete(*, post):
        """
        Permanently delete a community post.

        Related target/comments/likes/reports are expected to follow
        the model's configured cascade behavior.
        """

        post.delete()

class CommunityPostCommentService:
    @staticmethod
    @transaction.atomic
    def create(*, user, post, content, parent=None):
        """
        Create a comment or reply on a published community post.

        The post must be published.
        If parent is provided, it must belong to the same post
        and must itself be published.
        """

        if post.status != CommunityPost.Status.PUBLISHED:
            raise ValidationError(
                "You can only comment on published posts."
            )

        if parent is not None:
            if parent.post_id != post.pk:
                raise ValidationError(
                    "The parent comment must belong to the same post."
                )

            if parent.status != CommunityPostComment.Status.PUBLISHED:
                raise ValidationError(
                    "You can only reply to published comments."
                )

        comment = CommunityPostComment.objects.create(
            user=user,
            post=post,
            parent=parent,
            content=content,
        )

        CommunityPost.objects.filter(pk=post.pk).update(
            comments_count=models.F("comments_count") + 1,
        )

        if parent is not None:
            CommunityPostComment.objects.filter(pk=parent.pk).update(
                replies_count=models.F("replies_count") + 1,
            )

        return comment

    @staticmethod
    @transaction.atomic
    def update(*, comment, content):
        """
        Update comment content.

        The post and parent relationship are immutable.
        """

        comment.content = content
        comment.is_edited = True

        comment.save(
            update_fields=[
                "content",
                "is_edited",
                "updated_at",
            ]
        )

        return comment

    @staticmethod
    @transaction.atomic
    def delete(*, comment):
        """
        Delete a community comment safely.

        Decrements the post's comment counter and, when applicable,
        the parent's reply counter.
        """

        post_id = comment.post_id
        parent_id = comment.parent_id

        deleted, _ = CommunityPostComment.objects.filter(
            pk=comment.pk
        ).delete()

        if not deleted:
            return

        CommunityPost.objects.filter(
            pk=post_id,
            comments_count__gt=0,
        ).update(
            comments_count=models.F("comments_count") - 1,
        )

        if parent_id is not None:
            CommunityPostComment.objects.filter(
                pk=parent_id,
                replies_count__gt=0,
            ).update(
                replies_count=models.F("replies_count") - 1,
            )

class EditorialArticleReportService:
    @staticmethod
    @transaction.atomic
    def create(*, user, article, reason, details=""):
        """
        Report a published editorial article.
        """

        if article.status != EditorialArticle.Status.PUBLISHED:
            raise ValidationError(
                "You can only report published articles."
            )

        if EditorialArticleReport.objects.filter(
            user=user,
            article=article,
        ).exists():
            raise ValidationError(
                "You have already reported this article."
            )

        try:
            return EditorialArticleReport.objects.create(
                user=user,
                article=article,
                reason=reason,
                details=details,
            )
        except IntegrityError:
            raise ValidationError(
                "You have already reported this article."
            )


class CommunityPostReportService:
    @staticmethod
    @transaction.atomic
    def create(*, user, post, reason, details=""):
        """
        Report a published community post.
        """

        if post.status != CommunityPost.Status.PUBLISHED:
            raise ValidationError(
                "You can only report published posts."
            )

        if CommunityPostReport.objects.filter(
            user=user,
            post=post,
        ).exists():
            raise ValidationError(
                "You have already reported this post."
            )

        try:
            return CommunityPostReport.objects.create(
                user=user,
                post=post,
                reason=reason,
                details=details,
            )
        except IntegrityError:
            raise ValidationError(
                "You have already reported this post."
            )


class EditorialCommentReportService:
    @staticmethod
    @transaction.atomic
    def create(*, user, comment, reason, details=""):
        """
        Report a published editorial comment.
        """

        if comment.status != EditorialComment.Status.PUBLISHED:
            raise ValidationError(
                "You can only report published comments."
            )

        if comment.article.status != EditorialArticle.Status.PUBLISHED:
            raise ValidationError(
                "You can only report comments on published articles."
            )

        if EditorialCommentReport.objects.filter(
            user=user,
            comment=comment,
        ).exists():
            raise ValidationError(
                "You have already reported this comment."
            )

        try:
            return EditorialCommentReport.objects.create(
                user=user,
                comment=comment,
                reason=reason,
                details=details,
            )
        except IntegrityError:
            raise ValidationError(
                "You have already reported this comment."
            )


class CommunityPostCommentReportService:
    @staticmethod
    @transaction.atomic
    def create(*, user, comment, reason, details=""):
        """
        Report a published community post comment.
        """

        if comment.status != CommunityPostComment.Status.PUBLISHED:
            raise ValidationError(
                "You can only report published comments."
            )

        if comment.post.status != CommunityPost.Status.PUBLISHED:
            raise ValidationError(
                "You can only report comments on published posts."
            )

        if CommunityPostCommentReport.objects.filter(
            user=user,
            comment=comment,
        ).exists():
            raise ValidationError(
                "You have already reported this comment."
            )

        try:
            return CommunityPostCommentReport.objects.create(
                user=user,
                comment=comment,
                reason=reason,
                details=details,
            )
        except IntegrityError:
            raise ValidationError(
                "You have already reported this comment."
            )