from __future__ import annotations

from datetime import timedelta

from django.db import IntegrityError, transaction
from django.db.models import F
from django.db.models.functions import Greatest
from django.utils import timezone
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
        # Lock and recheck the article to avoid creating
        # comments while its publication status is changing.
        locked_article = (
            EditorialArticle.objects
            .select_for_update()
            .filter(pk=article.pk)
            .first()
        )

        if (
            locked_article is None
            or locked_article.status
            != EditorialArticle.Status.PUBLISHED
        ):
            raise ValidationError(
                "Comments can only be added to published articles."
            )

        locked_parent = None
        root_comment = None

        if parent is not None:
            locked_parent = (
                EditorialComment.objects
                .select_for_update()
                .filter(pk=parent.pk)
                .first()
            )

            if locked_parent is None:
                raise ValidationError(
                    "The parent comment does not exist."
                )

            if locked_parent.article_id != locked_article.pk:
                raise ValidationError(
                    "The parent comment does not belong to this article."
                )

            if (
                locked_parent.status
                != EditorialComment.Status.PUBLISHED
            ):
                raise ValidationError(
                    "You cannot reply to this comment."
                )

            # Direct replies point to their parent, which is
            # the root. Deeper replies inherit the same root.
            if locked_parent.parent_id is None:
                root_comment = locked_parent
            else:
                root_comment = locked_parent.root_comment

                # Defensive validation for legacy or malformed data.
                if root_comment is None:
                    raise ValidationError(
                        "This comment thread is invalid. "
                        "Please reply to another comment."
                    )

                if (
                    root_comment.article_id != locked_article.pk
                    or root_comment.parent_id is not None
                    or root_comment.status
                    != EditorialComment.Status.PUBLISHED
                ):
                    raise ValidationError(
                        "This comment thread is no longer available."
                    )

        try:
            comment = EditorialComment.objects.create(
                user=user,
                article=locked_article,
                parent=locked_parent,
                root_comment=root_comment,
                content=content.strip(),
            )
        except IntegrityError as exc:
            raise ValidationError(
                "Unable to create this comment."
            ) from exc

        EditorialArticle.objects.filter(
            pk=locked_article.pk,
        ).update(
            comments_count=F("comments_count") + 1,
        )

        if locked_parent is not None:
            EditorialComment.objects.filter(
                pk=locked_parent.pk,
            ).update(
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
        locked_comment = (
            EditorialComment.objects
            .select_for_update()
            .filter(pk=comment.pk)
            .first()
        )

        if (
            locked_comment is None
            or locked_comment.status
            != EditorialComment.Status.PUBLISHED
        ):
            raise ValidationError(
                "This comment cannot be edited."
            )

        # Comments can only be edited within 15 minutes
        # of their original creation time.
        edit_deadline = (
            locked_comment.created_at + timedelta(minutes=15)
        )

        if timezone.now() > edit_deadline:
            raise ValidationError(
                "Comments can only be edited within "
                "15 minutes of posting."
            )

        locked_comment.content = content.strip()
        locked_comment.is_edited = True

        locked_comment.save(
            update_fields=[
                "content",
                "is_edited",
                "updated_at",
            ],
        )

        return locked_comment

    @staticmethod
    @transaction.atomic
    def delete(
        *,
        comment: EditorialComment,
    ) -> None:
        # Fetch the latest state inside the transaction.
        locked_comment = (
            EditorialComment.objects
            .select_for_update()
            .filter(pk=comment.pk)
            .first()
        )

        if locked_comment is None:
            return

        article_id = locked_comment.article_id
        parent_id = locked_comment.parent_id

        # Lock the article so comment creation/deletion operations
        # for this article coordinate around the same row.
        article = (
            EditorialArticle.objects
            .select_for_update()
            .filter(pk=article_id)
            .first()
        )

        if article is None:
            return

        # Discover the entire subtree iteratively. This supports
        # unlimited nesting without recursive Python calls.
        all_deleted_ids = {locked_comment.pk}
        frontier = {locked_comment.pk}

        while frontier:
            child_ids = set(
                EditorialComment.objects.filter(
                    article_id=article_id,
                    parent_id__in=frontier,
                ).exclude(
                    status=EditorialComment.Status.REMOVED,
                ).values_list(
                    "pk",
                    flat=True,
                )
            )

            child_ids -= all_deleted_ids

            if not child_ids:
                break

            all_deleted_ids.update(child_ids)
            frontier = child_ids

        # Count only comments that currently contribute to the
        # public article counter.
        published_count = EditorialComment.objects.filter(
            pk__in=all_deleted_ids,
            status=EditorialComment.Status.PUBLISHED,
        ).count()

        # Soft-delete the subtree. Reports, likes, and moderation
        # history remain attached to the existing records.
        EditorialComment.objects.filter(
            pk__in=all_deleted_ids,
        ).exclude(
            status=EditorialComment.Status.REMOVED,
        ).update(
            status=EditorialComment.Status.REMOVED,
        )

        if published_count:
            EditorialArticle.objects.filter(
                pk=article_id,
            ).update(
                comments_count=Greatest(
                    F("comments_count") - published_count,
                    0,
                ),
            )

        # The deleted comment was one direct reply to its parent.
        # Descendant counts are handled by the subtree operation.
        if parent_id is not None:
            EditorialComment.objects.filter(
                pk=parent_id,
                status=EditorialComment.Status.PUBLISHED,
                replies_count__gt=0,
            ).update(
                replies_count=F("replies_count") - 1,
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