from __future__ import annotations

import re

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, transaction
from django.db.models.functions import Lower

from notifications.services.notification import NotificationService

from music.models import (
    CommunityPost,
    CommunityPostComment,
    EditorialComment,
    UserMention,
)


User = get_user_model()


class MentionService:
    """
    Manages user mentions in supported VibeNationHQ content.

    Mention relationships are the source of truth for identifying
    users mentioned in a content item.

    Notifications are created only for newly added relationships.
    Repeated mentions of the same user in one content item create
    only one relationship and one notification.
    """

    SUPPORTED_TARGETS = (
        CommunityPost,
        CommunityPostComment,
        EditorialComment,
    )

    NOTIFICATION_TYPES = {
        CommunityPost: "community_post_mention",
        CommunityPostComment: "community_comment_mention",
        EditorialComment: "editorial_comment_mention",
    }

    # Django's default username characters, with a boundary that
    # prevents matching the @ portion of an email address.
    MENTION_PATTERN = re.compile(
        r"(?<![\w.+-])@(?P<username>[\w.@+-]+)",
        re.UNICODE,
    )

    # ========================================================
    # Internal helpers
    # ========================================================

    @classmethod
    def _validate_target(cls, content_object) -> None:
        if not isinstance(
            content_object,
            cls.SUPPORTED_TARGETS,
        ):
            raise ValueError(
                "Unsupported mention content target."
            )

        if content_object.pk is None:
            raise ValueError(
                "Mention target must be saved before "
                "mentions can be synchronized."
            )

    @classmethod
    def _extract_usernames(cls, content: str) -> set[str]:
        """
        Extract unique usernames from content.

        Matching is case-insensitive. Original username casing
        is preserved only in the content itself.
        """
        if not content:
            return set()

        return {
            match.group("username").casefold()
            for match in cls.MENTION_PATTERN.finditer(content)
        }

    @classmethod
    def _get_mentioned_users(
        cls,
        usernames: set[str],
    ) -> dict[str, AbstractBaseUser]:
        """
        Resolve usernames in one database query.

        Only active, non-staff platform accounts are eligible.
        """
        if not usernames:
            return {}

        users = (
            User.objects
            .annotate(
                normalized_username=Lower("username"),
            )
            .filter(
                normalized_username__in=usernames,
                is_active=True,
                is_staff=False,
            )
        )

        return {
            user.username.casefold(): user
            for user in users
        }

    @classmethod
    def _get_content_type(cls, content_object) -> ContentType:
        return ContentType.objects.get_for_model(
            content_object,
            for_concrete_model=False,
        )

    @classmethod
    def _create_notification(
        cls,
        *,
        mentioner,
        mentioned_user,
        content_object,
        mention,
    ) -> None:
        """
        Create an individual notification for a new mention.
        """
        if mentioner.pk == mentioned_user.pk:
            return

        notification_type = cls.NOTIFICATION_TYPES[
            type(content_object)
        ]

        NotificationService.create_event(
            recipient=mentioned_user,
            actor=mentioner,
            event_type=notification_type,
            target=content_object,
            metadata={
                "mention_id": str(mention.pk),
                "content_id": str(content_object.pk),
            },
        )

    # ========================================================
    # Public methods
    # ========================================================

    @classmethod
    def sync_mentions(
        cls,
        *,
        mentioner,
        content_object,
        content: str,
    ) -> list[UserMention]:
        """
        Synchronize mention relationships with the current
        content.

        Newly added mentions create notification events.
        Removed mentions have their relationships deleted.
        Unchanged mentions do not generate duplicate events.
        """
        cls._validate_target(content_object)

        usernames = cls._extract_usernames(content)

        mentioned_users = cls._get_mentioned_users(
            usernames,
        )

        content_type = cls._get_content_type(
            content_object,
        )

        with transaction.atomic():
            existing_mentions = list(
                UserMention.objects
                .select_for_update()
                .filter(
                    content_type=content_type,
                    object_id=str(content_object.pk),
                )
            )

            existing_by_user = {
                mention.mentioned_user_id: mention
                for mention in existing_mentions
            }

            desired_user_ids = {
                user.pk
                for user in mentioned_users.values()
            }

            # Remove relationships for mentions no longer present.
            removed_user_ids = (
                set(existing_by_user.keys())
                - desired_user_ids
            )

            if removed_user_ids:
                UserMention.objects.filter(
                    content_type=content_type,
                    object_id=str(content_object.pk),
                    mentioned_user_id__in=removed_user_ids,
                ).delete()

            synchronized_mentions = []

            for mentioned_user in mentioned_users.values():
                existing = existing_by_user.get(
                    mentioned_user.pk,
                )

                if existing is not None:
                    synchronized_mentions.append(existing)
                    continue

                try:
                    mention, created = (
                        UserMention.objects.get_or_create(
                            content_type=content_type,
                            object_id=str(content_object.pk),
                            mentioned_user=mentioned_user,
                            defaults={
                                "mentioner": mentioner,
                            },
                        )
                    )

                except IntegrityError:
                    mention = UserMention.objects.get(
                        content_type=content_type,
                        object_id=str(content_object.pk),
                        mentioned_user=mentioned_user,
                    )
                    created = False

                synchronized_mentions.append(mention)

                if created:
                    cls._create_notification(
                        mentioner=mentioner,
                        mentioned_user=mentioned_user,
                        content_object=content_object,
                        mention=mention,
                    )

            return synchronized_mentions

    @classmethod
    def delete_mentions(
        cls,
        *,
        content_object,
    ) -> int:
        """
        Delete all mention relationships associated with
        a content item.

        Call this from the corresponding content deletion
        service when the content is deleted or soft-deleted.
        """
        cls._validate_target(content_object)

        content_type = cls._get_content_type(
            content_object,
        )

        deleted_count, _ = UserMention.objects.filter(
            content_type=content_type,
            object_id=str(content_object.pk),
        ).delete()

        return deleted_count

    @classmethod
    def delete_mentions_for_objects(
        cls,
        *,
        target_model,
        object_ids,
    ) -> int:
        """
        Delete mentions belonging to multiple content objects
        using a single bulk query.

        Useful when deleting a comment and its entire reply
        subtree.
        """
        if target_model not in cls.SUPPORTED_TARGETS:
            raise ValueError("Unsupported mention content target.")

        normalized_object_ids = {
            str(object_id)
            for object_id in object_ids
            if object_id is not None
        }

        if not normalized_object_ids:
            return 0

        content_type = ContentType.objects.get_for_model(
            target_model,
            for_concrete_model=False,
        )

        deleted_count, _ = UserMention.objects.filter(
            content_type=content_type,
            object_id__in=normalized_object_ids,
        ).delete()

        return deleted_count