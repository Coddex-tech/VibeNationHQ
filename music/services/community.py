from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db import (
    transaction,
    models,
    IntegrityError,
)
from django.db.models import (
    Count,
    Exists,
    OuterRef,
    Prefetch,
    F,
)
from django.utils import timezone

from rest_framework.exceptions import ValidationError
from datetime import timedelta

from music.models import UserFollow


from music.models import (
    CommunityPost,
    CommunityPostTarget,
    CommunityPostComment,
    CommunityPostFavorite,
    EditorialArticle,
    CommunityPostReport,
    EditorialArticleReport,
    EditorialCommentReport,
    EditorialComment,
    CommunityPostCommentReport,
)

User = get_user_model()


class CommunityPostService:
    @staticmethod
    def _generate_unique_slug(*, content):
        """
        Generate a unique, readable slug for a community post.

        The slug is generated from the post content and truncated
        to fit the CommunityPost.slug field.

        Existing slugs are never changed by this helper.
        """

        max_length = CommunityPost._meta.get_field(
            "slug",
        ).max_length

        base_slug = slugify(content)[:max_length].strip("-")

        if not base_slug:
            base_slug = "community-post"

        slug = base_slug
        suffix = 2

        while CommunityPost.objects.filter(
            slug=slug,
        ).exists():
            suffix_text = f"-{suffix}"

            slug = (
                f"{base_slug[:max_length - len(suffix_text)]}"
                f"{suffix_text}"
            )

            suffix += 1

        return slug
    
    @staticmethod
    @transaction.atomic
    def create(
        *,
        user,
        content,
        rating=None,
        target_data=None,
    ):
        """
        Create a community post and, when provided, its target
        atomically.

        The serializer validates the incoming target structure.
        The service additionally enforces business rules so that
        direct service calls cannot create invalid rating/target
        combinations.

        A target is optional, so ordinary text-only community
        posts are supported.
        """

        if rating is not None:
            if target_data is None:
                raise ValidationError(
                    "A rating can only be added when "
                    "a song or album is attached."
                )

            target_type = target_data.get(
                "target_type",
            )

            if target_type not in {
                CommunityPostTarget.TargetType.SONG,
                CommunityPostTarget.TargetType.ALBUM,
            }:
                raise ValidationError(
                    "A rating can only be added to "
                    "a song or album."
                )

        post = CommunityPost.objects.create(
            user=user,
            content=content,
            rating=rating,
            slug=CommunityPostService._generate_unique_slug(
                content=content,
            ),
        )

        if target_data:
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

        Editing is permitted only within 30 minutes
        of the post's original creation time.

        The target and slug are intentionally immutable.

        A rating is only valid when the post has a Song
        or Album target.
        """

        edit_deadline = (
            post.created_at
            + timedelta(minutes=30)
        )

        if timezone.now() >= edit_deadline:
            raise ValidationError(
                "The 30-minute editing window has expired. "
                "This post can no longer be edited."
            )

        if rating is not None:
            target_type = (
                CommunityPostTarget.objects
                .filter(
                    post_id=post.pk,
                )
                .values_list(
                    "target_type",
                    flat=True,
                )
                .first()
            )

            if target_type not in {
                CommunityPostTarget.TargetType.SONG,
                CommunityPostTarget.TargetType.ALBUM,
            }:
                raise ValidationError(
                    "A rating can only be added to "
                    "a song or album."
                )

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
    def record_view(*, post):
        """
        Increment the view count for a published community post.

        F() performs the increment in the database, preventing
        simultaneous view requests from overwriting each other.

        Returns the updated view count, or None if the post
        is no longer published.
        """

        updated_rows = (
            CommunityPost.objects
            .filter(
                pk=post.pk,
                status=CommunityPost.Status.PUBLISHED,
            )
            .update(
                views_count=F("views_count") + 1,
            )
        )

        if updated_rows == 0:
            return None

        return (
            CommunityPost.objects
            .values_list(
                "views_count",
                flat=True,
            )
            .get(pk=post.pk)
        )

    @staticmethod
    @transaction.atomic
    def delete(*, post):
        """
        Soft-delete a community post by marking it as removed.
        Related records are retained for moderation and investigation
        """

        post.status = CommunityPost.Status.REMOVED
        post.save(
            update_fields=["status", "updated_at"]
        )


class CommunityPostCommentService:
    @staticmethod
    @transaction.atomic
    def create(*, user, post, content, parent=None):
        """
        Create a comment or reply on a published community post.

        Every reply stores a reference to its original root
        comment. Root comments keep root_comment=None.

        This supports efficient, paginated retrieval of an
        entire conversation without recursively querying
        every reply's children.
        """

        locked_post = (
            CommunityPost.objects
            .select_for_update()
            .filter(pk=post.pk)
            .first()
        )

        if (
            locked_post is None
            or locked_post.status
            != CommunityPost.Status.PUBLISHED
        ):
            raise ValidationError(
                "You can only comment on published posts."
            )

        locked_parent = None
        root_comment = None

        if parent is not None:
            locked_parent = (
                CommunityPostComment.objects
                .select_for_update()
                .filter(
                    pk=parent.pk,
                    post_id=locked_post.pk,
                )
                .first()
            )

            if locked_parent is None:
                raise ValidationError(
                    "The parent comment must belong to "
                    "the same post."
                )

            if (
                locked_parent.status
                != CommunityPostComment.Status.PUBLISHED
            ):
                raise ValidationError(
                    "You can only reply to published comments."
                )

            # If the parent is itself a reply, reuse its root.
            # Otherwise, the parent is the root comment.
            root_comment = (
                locked_parent.root_comment
                if locked_parent.root_comment_id is not None
                else locked_parent
            )

        comment = CommunityPostComment.objects.create(
            user=user,
            post=locked_post,
            parent=locked_parent,
            root_comment=root_comment,
            content=content,
        )

        CommunityPost.objects.filter(
            pk=locked_post.pk,
        ).update(
            comments_count=models.F("comments_count") + 1,
        )

        if locked_parent is not None:
            CommunityPostComment.objects.filter(
                pk=locked_parent.pk,
            ).update(
                replies_count=models.F("replies_count") + 1,
            )

        return comment


    @staticmethod
    @transaction.atomic
    def update(*, comment, content):
        """
        Update comment content within 15 minutes of creation.

        The editing deadline is based on created_at, so editing
        a comment does not restart the 15-minute window.

        The post and parent relationship are immutable.
        """

        # Re-fetch and lock the current database record.
        current_comment = (
            CommunityPostComment.objects
            .select_for_update()
            .filter(pk=comment.pk)
            .first()
        )

        if current_comment is None:
            raise ValidationError(
                "This comment no longer exists."
            )

        if (
            current_comment.status
            != CommunityPostComment.Status.PUBLISHED
        ):
            raise ValidationError(
                "Only published comments can be edited."
            )

        edit_deadline = (
            current_comment.created_at
            + timedelta(minutes=15)
        )

        if timezone.now() >= edit_deadline:
            raise ValidationError(
                "The 15-minute editing window has expired. "
                "This comment can no longer be edited."
            )

        current_comment.content = content
        current_comment.is_edited = True

        current_comment.save(
            update_fields=[
                "content",
                "is_edited",
                "updated_at",
            ]
        )

        return current_comment

    @staticmethod
    def _get_subtree_ids(comment_id):
        """
        Return the IDs of a comment and all of its descendants.

        Comment nesting is intentionally unlimited, so this uses
        iterative traversal rather than a fixed nesting depth.
        """

        comment_ids = {comment_id}
        current_level = [comment_id]

        while current_level:
            child_ids = list(
                CommunityPostComment.objects.filter(
                    parent_id__in=current_level,
                ).values_list(
                    "pk",
                    flat=True,
                )
            )

            child_ids = [
                child_id
                for child_id in child_ids
                if child_id not in comment_ids
            ]

            if not child_ids:
                break

            comment_ids.update(child_ids)
            current_level = child_ids

        return comment_ids

    
    @staticmethod
    @transaction.atomic
    def delete(*, comment):
        """
        Soft-delete a community comment or reply.

        The target comment and its published descendants are
        marked as REMOVED rather than physically deleted.

        This preserves comment records and their related
        moderation history while hiding the removed subtree
        from public API queries that require published status.

        Counters are decreased only for comments that were
        published when the deletion was processed.
        """

        comment_id = comment.pk

        # Lock the post to serialize comment-counter changes.
        post = (
            CommunityPost.objects
            .select_for_update()
            .filter(pk=comment.post_id)
            .first()
        )

        if post is None:
            return

        # Lock and re-check the target comment. This also
        # prevents a repeated delete from decrementing counters
        # a second time.
        current_comment = (
            CommunityPostComment.objects
            .select_for_update()
            .filter(pk=comment_id)
            .first()
        )

        if (
            current_comment is None
            or current_comment.status
            != CommunityPostComment.Status.PUBLISHED
        ):
            return

        parent_id = current_comment.parent_id

        # Lock the direct parent, if this is a reply.
        parent = None

        if parent_id is not None:
            parent = (
                CommunityPostComment.objects
                .select_for_update()
                .filter(pk=parent_id)
                .first()
            )

        # Collect the target and all descendants, regardless
        # of nesting depth.
        subtree_ids = (
            CommunityPostCommentService._get_subtree_ids(
                comment_id,
            )
        )

        # Only published records contribute to the public
        # comment counters.
        published_count = (
            CommunityPostComment.objects
            .filter(
                pk__in=subtree_ids,
                status=CommunityPostComment.Status.PUBLISHED,
            )
            .count()
        )

        # Mark published comments/replies in the subtree as
        # removed. No database rows or related records are
        # physically deleted.
        CommunityPostComment.objects.filter(
            pk__in=subtree_ids,
            status=CommunityPostComment.Status.PUBLISHED,
        ).update(
            status=CommunityPostComment.Status.REMOVED,
            updated_at=timezone.now(),
        )

        # Decrease the post's public comment count.
        if published_count > 0:
            CommunityPost.objects.filter(
                pk=post.pk,
                comments_count__gte=published_count,
            ).update(
                comments_count=(
                    models.F("comments_count")
                    - published_count
                ),
            )

        # Only the direct parent's reply count is reduced.
        # Descendant records remain in the database.
        if parent is not None:
            CommunityPostComment.objects.filter(
                pk=parent.pk,
                status=CommunityPostComment.Status.PUBLISHED,
                replies_count__gt=0,
            ).update(
                replies_count=models.F("replies_count") - 1,
            )


class CommunityPostFavoriteService:
    @staticmethod
    @transaction.atomic
    def create(*, user, post):
        """
        Favorite a published community post.

        A user can only favorite the same post once.
        """

        if post.status != CommunityPost.Status.PUBLISHED:
            raise ValidationError(
                "You can only favorite published posts."
            )

        if CommunityPostFavorite.objects.filter(
            user=user,
            post=post,
        ).exists():
            raise ValidationError(
                "You have already favorited this post."
            )

        try:
            return CommunityPostFavorite.objects.create(
                user=user,
                post=post,
            )
        except IntegrityError:
            raise ValidationError(
                "You have already favorited this post."
            )

    @staticmethod
    @transaction.atomic
    def delete(*, user, post):
        """
        Remove a post from the user's favorites.

        Deleting a non-existent favorite is intentionally a no-op,
        making the endpoint safe to call repeatedly.
        """

        CommunityPostFavorite.objects.filter(
            user=user,
            post=post,
        ).delete()
    
    @staticmethod
    def get_user_favorites(*, user):
        """
        Return the user's favorited published community posts.

        Favorites are ordered by when the user saved them, with the
        most recently favorited post first.

        The returned queryset is prepared to provide the same data
        required by the community post feed serializer while avoiding
        N+1 queries.

        Each post author is annotated with is_following, indicating
        whether the current user follows that author.
        """

        liked_posts = (
            CommunityPost.objects
            .filter(
                pk=OuterRef("pk"),
                likes__user_id=user.id,
            )
        )

        favorited_posts = (
            CommunityPostFavorite.objects
            .filter(
                user_id=user.id,
                post_id=OuterRef("pk"),
            )
        )

        author_follows = (
            UserFollow.objects
            .filter(
                follower=user,
                following_id=OuterRef("pk"),
            )
        )

        author_queryset = (
            User.objects
            .annotate(
                is_following=Exists(
                    author_follows,
                ),
            )
        )

        return (
            CommunityPost.objects
            .filter(
                status=CommunityPost.Status.PUBLISHED,
                favorites__user_id=user.id,
            )
            .select_related(
                "target",
                "target__song",
                "target__album",
                "target__artist",
            )
            .prefetch_related(
                Prefetch(
                    "user",
                    queryset=author_queryset,
                ),
                "target__song__artists",
                "target__song__featured_artists",
                "target__song__genres",
                "target__song__provider_identities",
                "target__album__artists",
            )
            .annotate(
                favorites_count=Count(
                    "favorites",
                    distinct=True,
                ),
                is_liked=Exists(
                    liked_posts,
                ),
                is_favorited=Exists(
                    favorited_posts,
                ),
            )
            .order_by(
                "-favorites__created_at",
            )
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