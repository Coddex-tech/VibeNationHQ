
from __future__ import annotations

import uuid

from datetime import datetime, timedelta, timezone as datetime_timezone
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

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
from notifications.services.notification import NotificationService


User = get_user_model()


class NotificationServiceTestCase(TestCase):
    """
    Tests for the central notification service.

    Covers event creation, notification grouping, preferences,
    idempotency, push scheduling, and event deactivation.
    """

    @classmethod
    def setUpTestData(cls):
        cls.recipient = User.objects.create_user(
            email="recipient@example.com",
            username="recipient",
            password="TestPassword123!",
        )

        cls.actor_one = User.objects.create_user(
            email="actor-one@example.com",
            username="actor_one",
            password="TestPassword123!",
        )

        cls.actor_two = User.objects.create_user(
            email="actor-two@example.com",
            username="actor_two",
            password="TestPassword123!",
        )

        cls.target_one = User.objects.create_user(
            email="target-one@example.com",
            username="target_one",
            password="TestPassword123!",
        )

        cls.target_two = User.objects.create_user(
            email="target-two@example.com",
            username="target_two",
            password="TestPassword123!",
        )

    # ========================================================
    # FOLLOW NOTIFICATIONS
    # ========================================================

    def test_follow_creates_notification_and_event(self):
        event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.FOLLOW,
        )

        notification = event.notification

        self.assertIsNotNone(notification)
        self.assertEqual(event.recipient, self.recipient)
        self.assertEqual(event.actor, self.actor_one)

        self.assertEqual(
            event.event_type,
            NotificationEvent.Type.FOLLOW,
        )

        self.assertEqual(
            notification.notification_type,
            Notification.Type.NEW_FOLLOWER,
        )

        self.assertEqual(
            notification.category,
            Notification.Category.FOLLOWERS,
        )

        self.assertEqual(notification.event_count, 1)
        self.assertIsNone(notification.read_at)

    def test_follow_events_from_same_day_are_grouped(self):
        first_event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.FOLLOW,
        )

        second_event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_two,
            event_type=NotificationEvent.Type.FOLLOW,
        )

        self.assertEqual(
            first_event.notification_id,
            second_event.notification_id,
        )

        self.assertEqual(
            Notification.objects.filter(
                recipient=self.recipient,
                category=Notification.Category.FOLLOWERS,
            ).count(),
            1,
        )

        notification = first_event.notification

        notification.refresh_from_db()

        self.assertEqual(notification.event_count, 2)

        self.assertEqual(
            NotificationEvent.objects.filter(
                notification=notification,
                is_active=True,
            ).count(),
            2,
        )

    def test_new_follow_activity_resets_group_to_unread(self):
        first_event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.FOLLOW,
        )

        notification = first_event.notification

        notification.read_at = notification.created_at
        notification.save(update_fields=["read_at"])

        self.assertTrue(notification.is_read)

        second_event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_two,
            event_type=NotificationEvent.Type.FOLLOW,
        )

        notification.refresh_from_db()

        self.assertEqual(
            first_event.notification_id,
            second_event.notification_id,
        )

        self.assertFalse(notification.is_read)
        self.assertIsNone(notification.read_at)
        self.assertEqual(notification.event_count, 2)

    def test_follow_events_after_midnight_in_recipient_timezone_use_new_group(self):
        NotificationPreference.objects.create(
            user=self.recipient,
            timezone="America/Los_Angeles",
        )

        before_midnight = datetime(
            2026, 11, 12, 7, 30,
            tzinfo=datetime_timezone.utc,
        )

        after_midnight = datetime(
            2026, 11, 12, 8, 30,
            tzinfo=datetime_timezone.utc,
        )

        with patch(
            "notifications.services.notification.timezone.now",
            return_value=before_midnight,
        ):
            first_event = NotificationService.create_event(
                recipient=self.recipient,
                actor=self.actor_one,
                event_type=NotificationEvent.Type.FOLLOW,
            )

        with patch(
            "notifications.services.notification.timezone.now",
            return_value=after_midnight,
        ):
            second_event = NotificationService.create_event(
                recipient=self.recipient,
                actor=self.actor_two,
                event_type=NotificationEvent.Type.FOLLOW,
            )

        self.assertNotEqual(
            first_event.notification_id,
            second_event.notification_id,
        )

        self.assertEqual(
            Notification.objects.filter(
                recipient=self.recipient,
                category=Notification.Category.FOLLOWERS,
            ).count(),
            2,
        )

    # ========================================================
    # TARGET-GROUPED NOTIFICATIONS
    # ========================================================

    def test_likes_on_same_target_are_grouped(self):
        first_event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.COMMUNITY_POST_LIKE,
            target=self.target_one,
        )

        second_event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_two,
            event_type=NotificationEvent.Type.COMMUNITY_POST_LIKE,
            target=self.target_one,
        )

        self.assertEqual(
            first_event.notification_id,
            second_event.notification_id,
        )

        notification = first_event.notification

        notification.refresh_from_db()

        self.assertEqual(notification.event_count, 2)

        self.assertEqual(
            NotificationEvent.objects.filter(
                notification=notification,
                is_active=True,
            ).count(),
            2,
        )

    def test_likes_on_different_targets_create_separate_notifications(self):
        first_event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.COMMUNITY_POST_LIKE,
            target=self.target_one,
        )

        second_event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_two,
            event_type=NotificationEvent.Type.COMMUNITY_POST_LIKE,
            target=self.target_two,
        )

        self.assertNotEqual(
            first_event.notification_id,
            second_event.notification_id,
        )

        self.assertEqual(
            Notification.objects.filter(
                recipient=self.recipient,
                notification_type=(
                    Notification.Type.COMMUNITY_POST_LIKE
                ),
            ).count(),
            2,
        )

    # ========================================================
    # COMMENT-WINDOW GROUPING
    # ========================================================

    def test_comments_on_same_target_within_24_hours_are_grouped(self):
        first_time = datetime(
            2026, 11, 12, 10, 0,
            tzinfo=datetime_timezone.utc,
        )

        second_time = first_time + timedelta(hours=12)

        with patch(
            "notifications.services.notification.timezone.now",
            return_value=first_time,
        ):
            first_event = NotificationService.create_event(
                recipient=self.recipient,
                actor=self.actor_one,
                event_type=NotificationEvent.Type.COMMUNITY_POST_COMMENT,
                target=self.target_one,
            )

        with patch(
            "notifications.services.notification.timezone.now",
            return_value=second_time,
        ):
            second_event = NotificationService.create_event(
                recipient=self.recipient,
                actor=self.actor_two,
                event_type=NotificationEvent.Type.COMMUNITY_POST_COMMENT,
                target=self.target_one,
            )

        self.assertEqual(
            first_event.notification_id,
            second_event.notification_id,
        )

        notification = Notification.objects.get(
            pk=first_event.notification_id,
        )

        self.assertEqual(notification.event_count, 2)

    def test_comment_after_24_hour_inactivity_creates_new_group(self):
        first_time = datetime(
            2026, 11, 12, 10, 0,
            tzinfo=datetime_timezone.utc,
        )

        second_time = first_time + timedelta(hours=24, minutes=1)

        with patch(
            "notifications.services.notification.timezone.now",
            return_value=first_time,
        ):
            first_event = NotificationService.create_event(
                recipient=self.recipient,
                actor=self.actor_one,
                event_type=NotificationEvent.Type.COMMUNITY_POST_COMMENT,
                target=self.target_one,
            )

        with patch(
            "notifications.services.notification.timezone.now",
            return_value=second_time,
        ):
            second_event = NotificationService.create_event(
                recipient=self.recipient,
                actor=self.actor_two,
                event_type=NotificationEvent.Type.COMMUNITY_POST_COMMENT,
                target=self.target_one,
            )

        self.assertNotEqual(
            first_event.notification_id,
            second_event.notification_id,
        )

        self.assertEqual(
            Notification.objects.filter(
                recipient=self.recipient,
                notification_type=(
                    Notification.Type.COMMUNITY_POST_COMMENT
                ),
            ).count(),
            2,
        )

    # ========================================================
    # INDIVIDUAL NOTIFICATIONS
    # ========================================================

    def test_system_announcements_create_individual_notifications(self):
        first_event = NotificationService.create_event(
            recipient=self.recipient,
            event_type=NotificationEvent.Type.SYSTEM_ANNOUNCEMENT,
            metadata={
                "title": "Platform update",
                "message": "A new feature is available.",
            },
        )

        second_event = NotificationService.create_event(
            recipient=self.recipient,
            event_type=NotificationEvent.Type.SYSTEM_ANNOUNCEMENT,
            metadata={
                "title": "Maintenance notice",
                "message": "Scheduled maintenance is coming.",
            },
        )

        self.assertNotEqual(
            first_event.notification_id,
            second_event.notification_id,
        )

        self.assertEqual(
            Notification.objects.filter(
                recipient=self.recipient,
                notification_type=(
                    Notification.Type.SYSTEM_ANNOUNCEMENT
                ),
            ).count(),
            2,
        )

        self.assertIsNone(first_event.actor)
        self.assertIsNone(second_event.actor)

    # ========================================================
    # IDEMPOTENCY
    # ========================================================

    def test_repeated_event_with_same_idempotency_key_is_not_duplicated(self):
        idempotency_key = uuid.uuid4()

        first_event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.FOLLOW,
            idempotency_key=idempotency_key,
        )

        retry_event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.FOLLOW,
            idempotency_key=idempotency_key,
        )

        self.assertEqual(first_event.pk, retry_event.pk)

        self.assertEqual(
            NotificationEvent.objects.filter(
                idempotency_key=idempotency_key,
            ).count(),
            1,
        )

        self.assertEqual(
            Notification.objects.filter(
                recipient=self.recipient,
            ).count(),
            1,
        )

        self.assertEqual(
            first_event.notification.event_count,
            1,
        )

    def test_reusing_idempotency_key_for_different_event_is_rejected(self):
        idempotency_key = uuid.uuid4()

        NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.FOLLOW,
            idempotency_key=idempotency_key,
        )

        with self.assertRaises(ValidationError):
            NotificationService.create_event(
                recipient=self.recipient,
                actor=self.actor_two,
                event_type=NotificationEvent.Type.FOLLOW,
                idempotency_key=idempotency_key,
            )

        self.assertEqual(
            NotificationEvent.objects.filter(
                idempotency_key=idempotency_key,
            ).count(),
            1,
        )

    # ========================================================
    # NOTIFICATION PREFERENCES
    # ========================================================

    def test_disabling_in_app_does_not_disable_event_history(self):
        NotificationPreference.objects.create(
            user=self.recipient,
            in_app_enabled=False,
            push_enabled=False,
        )

        event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.FOLLOW,
        )

        self.assertIsNone(event.notification)

        self.assertEqual(
            NotificationEvent.objects.filter(
                recipient=self.recipient,
            ).count(),
            1,
        )

        self.assertEqual(
            Notification.objects.filter(
                recipient=self.recipient,
            ).count(),
            0,
        )

    def test_category_preference_can_disable_in_app_notifications(self):
        NotificationCategoryPreference.objects.create(
            user=self.recipient,
            category=Notification.Category.FOLLOWERS,
            in_app_enabled=False,
            push_enabled=True,
        )

        event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.FOLLOW,
        )

        self.assertIsNone(event.notification)

        self.assertTrue(
            NotificationEvent.objects.filter(
                pk=event.pk,
            ).exists()
        )

    def test_disabling_push_does_not_disable_in_app_notifications(self):
        NotificationPreference.objects.create(
            user=self.recipient,
            in_app_enabled=True,
            push_enabled=False,
        )

        event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.FOLLOW,
        )

        self.assertIsNotNone(event.notification)

        self.assertFalse(
            NotificationOutbox.objects.filter(
                event=event,
            ).exists()
        )

    # ========================================================
    # PUSH DELIVERY AND OUTBOX
    # ========================================================

    def test_push_enabled_creates_delivery_and_outbox(self):
        subscription = PushSubscription.objects.create(
            user=self.recipient,
            endpoint="https://push.example.com/subscription/one",
            p256dh_key="test-p256dh-key",
            auth_key="test-auth-key",
        )

        event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.FOLLOW,
        )

        delivery = NotificationDelivery.objects.get(
            event=event,
            subscription=subscription,
        )

        self.assertEqual(
            delivery.status,
            NotificationDelivery.Status.PENDING,
        )

        outbox = NotificationOutbox.objects.get(
            event=event,
        )

        self.assertEqual(
            outbox.task_type,
            "notification.dispatch_push",
        )

        self.assertEqual(
            outbox.payload,
            {"event_id": event.pk},
        )

        self.assertEqual(
            outbox.status,
            NotificationOutbox.Status.PENDING,
        )

    def test_expired_push_subscription_is_ignored(self):
        from django.utils import timezone

        subscription = PushSubscription.objects.create(
            user=self.recipient,
            endpoint="https://push.example.com/subscription/expired",
            p256dh_key="test-p256dh-key",
            auth_key="test-auth-key",
            expiration_time=timezone.now() - timedelta(days=1),
        )

        event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.FOLLOW,
        )

        self.assertFalse(
            NotificationDelivery.objects.filter(
                event=event,
                subscription=subscription,
            ).exists()
        )

        self.assertFalse(
            NotificationOutbox.objects.filter(
                event=event,
            ).exists()
        )

    def test_in_app_disabled_but_push_enabled_still_schedules_push(self):
        NotificationPreference.objects.create(
            user=self.recipient,
            in_app_enabled=False,
            push_enabled=True,
        )

        subscription = PushSubscription.objects.create(
            user=self.recipient,
            endpoint="https://push.example.com/subscription/two",
            p256dh_key="test-p256dh-key",
            auth_key="test-auth-key",
        )

        event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.FOLLOW,
        )

        self.assertIsNone(event.notification)

        self.assertTrue(
            NotificationDelivery.objects.filter(
                event=event,
                subscription=subscription,
            ).exists()
        )

        self.assertTrue(
            NotificationOutbox.objects.filter(
                event=event,
            ).exists()
        )

    # ========================================================
    # EVENT DEACTIVATION
    # ========================================================

    
    def test_deactivating_follow_updates_notification_count(self):
        first_event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.FOLLOW,
        )

        second_event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_two,
            event_type=NotificationEvent.Type.FOLLOW,
        )

        notification = first_event.notification
        notification.refresh_from_db()

        self.assertEqual(notification.event_count, 2)

        deactivated_count = NotificationService.deactivate_events(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.FOLLOW,
        )

        notification.refresh_from_db()
        first_event.refresh_from_db()
        second_event.refresh_from_db()

        self.assertEqual(deactivated_count, 1)
        self.assertFalse(first_event.is_active)
        self.assertTrue(second_event.is_active)
        self.assertEqual(notification.event_count, 1)
        self.assertIsNone(notification.deleted_at)


    def test_deactivating_last_event_soft_deletes_notification(self):
        event = NotificationService.create_event(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.FOLLOW,
        )

        notification = event.notification

        deactivated_count = NotificationService.deactivate_events(
            recipient=self.recipient,
            actor=self.actor_one,
            event_type=NotificationEvent.Type.FOLLOW,
        )

        notification.refresh_from_db()
        event.refresh_from_db()

        self.assertEqual(deactivated_count, 1)
        self.assertFalse(event.is_active)
        self.assertEqual(notification.event_count, 0)
        self.assertIsNotNone(notification.deleted_at)

    def test_deactivate_like_requires_target(self):
        with self.assertRaises(ValidationError):
            NotificationService.deactivate_events(
                recipient=self.recipient,
                event_type=NotificationEvent.Type.COMMUNITY_POST_LIKE,
                actor=self.actor_one,
            )

    def test_deactivate_unsupported_event_type(self):
        with self.assertRaises(ValidationError):
            NotificationService.deactivate_events(
                recipient=self.recipient,
                event_type=NotificationEvent.Type.COMMUNITY_POST_COMMENT,
                actor=self.actor_one,
            )

    # ========================================================
    # VALIDATION
    # ========================================================

    def test_users_cannot_receive_notifications_for_own_actions(self):
        with self.assertRaises(ValidationError):
            NotificationService.create_event(
                recipient=self.recipient,
                actor=self.recipient,
                event_type=NotificationEvent.Type.FOLLOW,
            )

        self.assertEqual(
            NotificationEvent.objects.filter(
                recipient=self.recipient,
            ).count(),
            0,
        )

    def test_unsupported_event_type_is_rejected(self):
        with self.assertRaises(ValidationError):
            NotificationService.create_event(
                recipient=self.recipient,
                actor=self.actor_one,
                event_type="unsupported_event",
            )

        self.assertEqual(
            NotificationEvent.objects.filter(
                recipient=self.recipient,
            ).count(),
            0,
        )
