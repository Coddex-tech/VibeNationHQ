from __future__ import annotations

from django.db import IntegrityError, transaction
from django.db.models import F
from django.db.models.functions import Greatest
from rest_framework.exceptions import ValidationError

from music.models import (
    EditorialArticle,
    EditorialArticleReport,
    EditorialComment,
    EditorialCommentReport,
)


class EditorialCommentService:
    @staticmethod
    @transaction.atomic
    def create(
        *,
        user,
        article: EditorialArticle,
        content: str,
        parent: EditorialComment | None = None,
    ) -> EditorialComment:
        if article.status != EditorialArticle.Status.PUBLISHED:
            raise ValidationError(
                "Comments can only be added to published articles."
            )

        if parent is not None:
            if parent.article_id != article.id:
                raise ValidationError(
                    "The parent comment does not belong to this article."
                )

            if parent.status != EditorialComment.Status.PUBLISHED:
                raise ValidationError(
                    "You cannot reply to this comment."
                )

        try:
            comment = EditorialComment.objects.create(
                user=user,
                article=article,
                parent=parent,
                content=content.strip(),
            )
        except IntegrityError as exc:
            raise ValidationError(
                "Unable to create this comment."
            ) from exc

        EditorialArticle.objects.filter(pk=article.pk).update(
            comments_count=F("comments_count") + 1,
        )

        if parent is not None:
            EditorialComment.objects.filter(pk=parent.pk).update(
                replies_count=F("replies_count") + 1,
            )

        return comment

    @staticmethod
    @transaction.atomic
    def update(
        *,
        comment: EditorialComment,
        content: str,
    ) -> EditorialComment:
        if comment.status != EditorialComment.Status.PUBLISHED:
            raise ValidationError(
                "This comment cannot be edited."
            )

        comment.content = content.strip()
        comment.is_edited = True
        comment.save(
            update_fields=[
                "content",
                "is_edited",
                "updated_at",
            ],
        )

        return comment

    @staticmethod
    @transaction.atomic
    def delete(
        *,
        comment: EditorialComment,
    ) -> None:
        article_id = comment.article_id
        parent_id = comment.parent_id

        comment_ids = EditorialComment.objects.filter(
            article_id=article_id,
        ).values_list(
            "id",
            flat=True,
        )

        descendant_ids = set(
            EditorialComment.objects.filter(
                article_id=article_id,
                parent_id__in=[comment.id],
            ).values_list(
                "id",
                flat=True,
            )
        )

        all_deleted_ids = {comment.id}

        while descendant_ids:
            all_deleted_ids.update(descendant_ids)

            descendant_ids = set(
                EditorialComment.objects.filter(
                    article_id=article_id,
                    parent_id__in=descendant_ids,
                ).values_list(
                    "id",
                    flat=True,
                )
            )

        deleted_count = len(all_deleted_ids)

        comment.delete()

        if deleted_count:
            EditorialArticle.objects.filter(
                pk=article_id,
            ).update(
                comments_count=Greatest(
                    F("comments_count") - deleted_count,
                    0,
                ),
            )

        if parent_id is not None:
            EditorialComment.objects.filter(
                pk=parent_id,
            ).update(
                replies_count=Greatest(
                    F("replies_count") - 1,
                    0,
                ),
            )


class EditorialArticleReportService:
    @staticmethod
    @transaction.atomic
    def create(
        *,
        user,
        article: EditorialArticle,
        reason: str,
        details: str = "",
    ) -> EditorialArticleReport:
        if article.status != EditorialArticle.Status.PUBLISHED:
            raise ValidationError(
                "Only published articles can be reported."
            )

        try:
            return EditorialArticleReport.objects.create(
                user=user,
                article=article,
                reason=reason,
                details=details.strip(),
            )
        except IntegrityError as exc:
            raise ValidationError(
                "You have already reported this article."
            ) from exc


class EditorialCommentReportService:
    @staticmethod
    @transaction.atomic
    def create(
        *,
        user,
        comment: EditorialComment,
        reason: str,
        details: str = "",
    ) -> EditorialCommentReport:
        if comment.status != EditorialComment.Status.PUBLISHED:
            raise ValidationError(
                "Only published comments can be reported."
            )

        if (
            comment.article.status
            != EditorialArticle.Status.PUBLISHED
        ):
            raise ValidationError(
                "Comments on unpublished articles cannot be reported."
            )

        try:
            return EditorialCommentReport.objects.create(
                user=user,
                comment=comment,
                reason=reason,
                details=details.strip(),
            )
        except IntegrityError as exc:
            raise ValidationError(
                "You have already reported this comment."
            ) from exc