from __future__ import annotations

import uuid

from datetime import timedelta
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, transaction
from django.db.models import Q, Count
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from notifications.models import (
    Notification,
    NotificationCategoryPreference,
    NotificationDelivery,
    NotificationEvent,
    NotificationOutbox,
    NotificationPreference,
    PushSubscription,
)

def models_q_expiration(now):
    return (
        Q(expiration_time__isnull=True)
        | Q(expiration_time__gt=now)
    )

class NotificationService:
    """
    Central service for creating and deactivating notification events.

    Business services should call this service only after their
    corresponding persistent action has succeeded.

    NotificationEvent stores the individual action.
    Notification stores the item displayed in the notification centre.
    NotificationOutbox stores work that must be dispatched asynchronously.
    """

    COMMENT_GROUP_WINDOW = timedelta(hours=24)

    # ========================================================
    # EVENT CONFIGURATION
    # ========================================================

    EVENT_CONFIGURATION = {
        NotificationEvent.Type.FOLLOW: {
            "category": Notification.Category.FOLLOWERS,
            "notification_type": Notification.Type.NEW_FOLLOWER,
            "grouping": "daily",
        },

        NotificationEvent.Type.COMMUNITY_POST_LIKE: {
            "category": Notification.Category.ACTIVITY,
            "notification_type": Notification.Type.COMMUNITY_POST_LIKE,
            "grouping": "target",
        },
        NotificationEvent.Type.COMMUNITY_POST_COMMENT: {
            "category": Notification.Category.ACTIVITY,
            "notification_type": Notification.Type.COMMUNITY_POST_COMMENT,
            "grouping": "comment_window",
        },
        NotificationEvent.Type.COMMUNITY_COMMENT_LIKE: {
            "category": Notification.Category.ACTIVITY,
            "notification_type": Notification.Type.COMMUNITY_COMMENT_LIKE,
            "grouping": "target",
        },
        NotificationEvent.Type.COMMUNITY_COMMENT_REPLY: {
            "category": Notification.Category.ACTIVITY,
            "notification_type": Notification.Type.COMMUNITY_COMMENT_REPLY,
            "grouping": "individual",
        },

        NotificationEvent.Type.EDITORIAL_ARTICLE_LIKE: {
            "category": Notification.Category.ACTIVITY,
            "notification_type": Notification.Type.EDITORIAL_ARTICLE_LIKE,
            "grouping": "target",
        },
        NotificationEvent.Type.EDITORIAL_ARTICLE_COMMENT: {
            "category": Notification.Category.ACTIVITY,
            "notification_type": Notification.Type.EDITORIAL_ARTICLE_COMMENT,
            "grouping": "comment_window",
        },
        NotificationEvent.Type.EDITORIAL_COMMENT_LIKE: {
            "category": Notification.Category.ACTIVITY,
            "notification_type": Notification.Type.EDITORIAL_COMMENT_LIKE,
            "grouping": "target",
        },
        NotificationEvent.Type.EDITORIAL_COMMENT_REPLY: {
            "category": Notification.Category.ACTIVITY,
            "notification_type": Notification.Type.EDITORIAL_COMMENT_REPLY,
            "grouping": "individual",
        },

        NotificationEvent.Type.COMMUNITY_POST_MENTION: {
            "category": Notification.Category.MENTIONS,
            "notification_type": Notification.Type.COMMUNITY_POST_MENTION,
            "grouping": "individual",
        },
        NotificationEvent.Type.COMMUNITY_COMMENT_MENTION: {
            "category": Notification.Category.MENTIONS,
            "notification_type": Notification.Type.COMMUNITY_COMMENT_MENTION,
            "grouping": "individual",
        },
        NotificationEvent.Type.EDITORIAL_COMMENT_MENTION: {
            "category": Notification.Category.MENTIONS,
            "notification_type": Notification.Type.EDITORIAL_COMMENT_MENTION,
            "grouping": "individual",
        },

        NotificationEvent.Type.SYSTEM_ANNOUNCEMENT: {
            "category": Notification.Category.SYSTEM,
            "notification_type": Notification.Type.SYSTEM_ANNOUNCEMENT,
            "grouping": "individual",
        },
    }

    REVERSIBLE_EVENT_TYPES = {
        NotificationEvent.Type.FOLLOW,

        NotificationEvent.Type.COMMUNITY_POST_LIKE,
        NotificationEvent.Type.COMMUNITY_COMMENT_LIKE,

        NotificationEvent.Type.EDITORIAL_ARTICLE_LIKE,
        NotificationEvent.Type.EDITORIAL_COMMENT_LIKE,
    }

    # ========================================================
    # PREFERENCE HELPERS
    # ========================================================

    @classmethod
    def _get_preferences(cls, *, user) -> NotificationPreference:
        preferences, _ = NotificationPreference.objects.get_or_create(
            user=user,
        )
        return preferences

    @classmethod
    def _get_channel_preferences(
        cls,
        *,
        user,
        category: str,
    ) -> dict[str, bool]:
        """
        Resolve global and category-specific channel settings.

        A category setting can disable a channel globally enabled
        by the user's main notification preferences.
        """
        preferences = cls._get_preferences(user=user)

        category_preferences = (
            NotificationCategoryPreference.objects
            .filter(
                user=user,
                category=category,
            )
            .first()
        )

        in_app_enabled = preferences.in_app_enabled
        push_enabled = preferences.push_enabled

        if category_preferences is not None:
            in_app_enabled = (
                in_app_enabled
                and category_preferences.in_app_enabled
            )
            push_enabled = (
                push_enabled
                and category_preferences.push_enabled
            )

        return {
            "in_app": in_app_enabled,
            "push": push_enabled,
        }

    @classmethod
    def _get_recipient_timezone(cls, *, user) -> ZoneInfo:
        preferences = cls._get_preferences(user=user)

        try:
            return ZoneInfo(preferences.timezone)
        except ZoneInfoNotFoundError:
            raise ValidationError(
                {
                    "timezone": (
                        "The notification preference contains "
                        "an invalid IANA timezone."
                    )
                }
            )

    # ========================================================
    # TARGET HELPERS
    # ========================================================

    @staticmethod
    def _get_target_data(
        *,
        target=None,
    ) -> dict[str, Any]:
        if target is None:
            return {
                "content_type": None,
                "object_id": None,
            }

        content_type = ContentType.objects.get_for_model(
            target,
            for_concrete_model=False,
        )

        object_id = str(target.pk)

        if len(object_id) > 64:
            raise ValidationError(
                {
                    "target": (
                        "The target object's primary key "
                        "cannot exceed 64 characters."
                    )
                }
            )

        return {
            "content_type": content_type,
            "object_id": object_id,
        }

    @staticmethod
    def _targets_match(
        *,
        event: NotificationEvent,
        recipient,
        actor,
        event_type: str,
        target_data: dict,
    ) -> bool:
        return (
            event.recipient_id == recipient.pk
            and event.actor_id == (
                actor.pk if actor is not None else None
            )
            and event.event_type == event_type
            and event.target_content_type_id == (
                target_data["content_type"].pk
                if target_data["content_type"] is not None
                else None
            )
            and event.target_object_id == target_data["object_id"]
        )

    # ========================================================
    # GROUPING HELPERS
    # ========================================================

    @staticmethod
    def _make_target_grouping_key(
        *,
        recipient,
        event_type: str,
        target_data: dict,
    ) -> str:
        if target_data["content_type"] is None:
            raise ValidationError(
                {
                    "target": (
                        "A target is required for this "
                        "grouped notification type."
                    )
                }
            )

        return (
            f"target:{recipient.pk}:{event_type}:"
            f"{target_data['content_type'].pk}:"
            f"{target_data['object_id']}"
        )

    @classmethod
    def _make_daily_grouping_key(
        cls,
        *,
        recipient,
        event_type: str,
        user,
        now,
    ) -> str:
        recipient_timezone = cls._get_recipient_timezone(
            user=user,
        )

        local_date = now.astimezone(
            recipient_timezone,
        ).date()

        return (
            f"daily:{recipient.pk}:{event_type}:"
            f"{recipient_timezone.key}:{local_date.isoformat()}"
        )

    @classmethod
    def _get_comment_group(
        cls,
        *,
        recipient,
        event_type: str,
        target_data: dict,
        now,
    ) -> Notification | None:
        base_key = cls._make_target_grouping_key(
            recipient=recipient,
            event_type=event_type,
            target_data=target_data,
        )

        cutoff = now - cls.COMMENT_GROUP_WINDOW

        return (
            Notification.objects
            .filter(
                recipient=recipient,
                grouping_key__startswith=f"{base_key}:",
                latest_event_at__gte=cutoff,
                deleted_at__isnull=True,
            )
            .order_by("-latest_event_at", "-pk")
            .first()
        )
    
    @classmethod
    def _get_grouping_data(
        cls,
        *,
        recipient,
        user,
        event_type: str,
        grouping: str,
        target_data: dict,
        now,
    ) -> tuple[str | None, Notification | None]:
        if grouping == "individual":
            return None, None

        if grouping == "target":
            grouping_key = cls._make_target_grouping_key(
                recipient=recipient,
                event_type=event_type,
                target_data=target_data,
            )

            existing = (
                Notification.objects
                .select_for_update()
                .filter(
                    recipient=recipient,
                    grouping_key=grouping_key,
                )
                .first()
            )

            return grouping_key, existing

        if grouping == "daily":
            grouping_key = cls._make_daily_grouping_key(
                recipient=recipient,
                event_type=event_type,
                user=user,
                now=now,
            )

            existing = (
                Notification.objects
                .select_for_update()
                .filter(
                    recipient=recipient,
                    grouping_key=grouping_key,
                )
                .first()
            )

            return grouping_key, existing

        if grouping == "comment_window":
            existing = cls._get_comment_group(
                recipient=recipient,
                event_type=event_type,
                target_data=target_data,
                now=now,
            )

            if existing is not None:
                return existing.grouping_key, existing

            base_key = cls._make_target_grouping_key(
                recipient=recipient,
                event_type=event_type,
                target_data=target_data,
            )

            return f"{base_key}:{uuid.uuid4()}", None

        raise ValidationError(
            {"grouping": "Unsupported notification grouping strategy."}
        )

    # ========================================================
    # PUSH OUTBOX
    # ========================================================

    @classmethod
    def _create_push_outbox(
        cls,
        *,
        event: NotificationEvent,
        user,
        category: str,
    ) -> None:
        channels = cls._get_channel_preferences(
            user=user,
            category=category,
        )

        if not channels["push"]:
            return

        now = timezone.now()

        subscriptions = PushSubscription.objects.filter(
            user=user,
            is_active=True,
        ).filter(
            # Ignore subscriptions with an expired expiration time.
            models_q_expiration(now)
        )

        if not subscriptions.exists():
            return

        for subscription in subscriptions:
            NotificationDelivery.objects.get_or_create(
                event=event,
                subscription=subscription,
                channel=NotificationDelivery.Channel.PUSH,
            )

        NotificationOutbox.objects.get_or_create(
            idempotency_key=f"notification.push.event.{event.pk}",
            defaults={
                "task_type": "notification.dispatch_push",
                "event": event,
                "payload": {
                    "event_id": event.pk,
                },
            },
        )

    # ========================================================
    # CREATE EVENT
    # ========================================================

    @classmethod
    def create_event(
        cls,
        *,
        recipient,
        event_type: str,
        actor=None,
        target=None,
        metadata: dict | None = None,
        idempotency_key: uuid.UUID | None = None,
    ) -> NotificationEvent:
        """
        Record an action and create or update its notification.

        The caller must invoke this after the underlying business
        action has succeeded.

        Args:
            recipient:
                User receiving the notification.

            event_type:
                A NotificationEvent.Type value.

            actor:
                User who performed the action. Can be None for
                system-generated events.

            target:
                The primary object associated with the event.

            metadata:
                Additional event information, such as comment IDs.

            idempotency_key:
                Optional UUID preventing duplicate event creation.
        """
        configuration = cls.EVENT_CONFIGURATION.get(event_type)

        if configuration is None:
            raise ValidationError(
                {"event_type": "Unsupported notification event type."}
            )

        if actor is not None and actor.pk == recipient.pk:
            raise ValidationError(
                {
                    "recipient": (
                        "Users cannot receive notifications "
                        "for their own actions."
                    )
                }
            )

        if metadata is None:
            metadata = {}

        if not isinstance(metadata, dict):
            raise ValidationError(
                {"metadata": "Metadata must be a dictionary."}
            )

        target_data = cls._get_target_data(target=target)

        now = timezone.now()

        try:
            with transaction.atomic():
                # Serialise notification creation for this recipient.
                user_model = get_user_model()

                recipient = (
                    user_model.objects
                    .select_for_update()
                    .get(pk=recipient.pk)
                )

                if actor is not None:
                    actor = user_model.objects.get(pk=actor.pk)

                event = NotificationEvent.objects.create(
                    recipient=recipient,
                    actor=actor,
                    event_type=event_type,
                    target_content_type=target_data["content_type"],
                    target_object_id=target_data["object_id"],
                    metadata=metadata,
                    idempotency_key=idempotency_key,
                )

                category = configuration["category"]

                channels = cls._get_channel_preferences(
                    user=recipient,
                    category=category,
                )

                notification = None

                if channels["in_app"]:
                    grouping_key, existing_group = (
                        cls._get_grouping_data(
                            recipient=recipient,
                            user=recipient,
                            event_type=event_type,
                            grouping=configuration["grouping"],
                            target_data=target_data,
                            now=now,
                        )
                    )

                    if existing_group is not None:
                        notification = existing_group

                        notification.event_count = (
                            NotificationEvent.objects
                            .filter(
                                notification=notification,
                                is_active=True,
                            )
                            .count()
                        )

                        notification.latest_event_at = now
                        notification.read_at = None
                        notification.deleted_at = None

                        notification.metadata = {
                            **notification.metadata,
                            **metadata,
                            "latest_event_id": event.pk,
                            "latest_actor_id": (
                                actor.pk if actor is not None else None
                            ),
                        }

                        notification.save(
                            update_fields=[
                                "event_count",
                                "latest_event_at",
                                "read_at",
                                "deleted_at",
                                "metadata",
                                "updated_at",
                            ]
                        )

                    else:
                        notification = Notification.objects.create(
                            recipient=recipient,
                            category=category,
                            notification_type=(
                                configuration["notification_type"]
                            ),
                            grouping_key=grouping_key,
                            target_content_type=(
                                target_data["content_type"]
                            ),
                            target_object_id=target_data["object_id"],
                            metadata={
                                **metadata,
                                "latest_event_id": event.pk,
                                "latest_actor_id": (
                                    actor.pk
                                    if actor is not None
                                    else None
                                ),
                            },
                            event_count=0,
                            latest_event_at=now,
                        )

                    event.notification = notification
                    event.save(update_fields=["notification"])

                    notification.event_count += 1
                    notification.save(
                        update_fields=[
                            "event_count",
                            "updated_at",
                        ]
                    )

                cls._create_push_outbox(
                    event=event,
                    user=recipient,
                    category=category,
                )

                return event

        except IntegrityError:
            # A duplicate idempotency key may have been submitted
            # concurrently. Check whether it represents the same event.
            if idempotency_key is None:
                raise

            existing = (
                NotificationEvent.objects
                .filter(idempotency_key=idempotency_key)
                .first()
            )

            if existing is None:
                raise

            if not cls._targets_match(
                event=existing,
                recipient=recipient,
                actor=actor,
                event_type=event_type,
                target_data=target_data,
            ):
                raise ValidationError(
                    {
                        "idempotency_key": (
                            "This idempotency key has already been "
                            "used for a different event."
                        )
                    }
                )

            return existing

    # ========================================================
    # DEACTIVATE EVENTS
    # ========================================================

    @classmethod
    def deactivate_events(
        cls,
        *,
        recipient,
        event_type: str,
        actor,
        target=None,
    ) -> int:
        """
        Deactivate existing events after an action is reversed.

        Reversible events:
        - Follow: target is optional.
        - Like interactions: target is required.

        Event history is retained. Notification counts are
        recalculated from the remaining active events.

        Returns the number of deactivated events.
        """
        if event_type not in cls.REVERSIBLE_EVENT_TYPES:
            raise ValidationError(
                {
                    "event_type": (
                        "This notification event type cannot "
                        "be deactivated."
                    )
                }
            )

        is_follow_event = (
            event_type == NotificationEvent.Type.FOLLOW
        )

        if not is_follow_event and target is None:
            raise ValidationError(
                {
                    "target": (
                        "A target is required when deactivating "
                        "this notification event."
                    )
                }
            )

        target_data = (
            cls._get_target_data(target=target)
            if target is not None
            else None
        )

        with transaction.atomic():
            user_model = get_user_model()

            recipient = (
                user_model.objects
                .select_for_update()
                .get(pk=recipient.pk)
            )

            events = NotificationEvent.objects.filter(
                recipient=recipient,
                actor=actor,
                event_type=event_type,
                is_active=True,
            )

            if target_data is not None:
                events = events.filter(
                    target_content_type=target_data["content_type"],
                    target_object_id=target_data["object_id"],
                )

            notification_ids = list(
                events.exclude(
                    notification__isnull=True,
                ).values_list(
                    "notification_id",
                    flat=True,
                ).distinct()
            )

            deactivated_count = events.update(is_active=False)

            for notification_id in notification_ids:
                notification = (
                    Notification.objects
                    .select_for_update()
                    .filter(pk=notification_id)
                    .first()
                )

                if notification is None:
                    continue

                active_count = (
                    NotificationEvent.objects
                    .filter(
                        notification=notification,
                        is_active=True,
                    )
                    .count()
                )

                notification.event_count = active_count

                if active_count == 0:
                    notification.deleted_at = timezone.now()

                notification.save(
                    update_fields=[
                        "event_count",
                        "deleted_at",
                        "updated_at",
                    ]
                )

            return deactivated_count