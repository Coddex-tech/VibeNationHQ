from __future__ import annotations

from datetime import timedelta
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient

from notifications.models import (
    Notification,
    NotificationEvent,
)


User = get_user_model()


class NotificationListAPITests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="notification@example.com",
            username="notificationuser",
            password="StrongPassword123!",
            onboarding_completed=True,
        )

        cls.other_user = User.objects.create_user(
            email="other@example.com",
            username="otheruser",
            password="StrongPassword123!",
            onboarding_completed=True,
        )

        cls.actors = [
            User.objects.create_user(
                email=f"actor{i}@example.com",
                username=f"actor{i}",
                password="StrongPassword123!",
                onboarding_completed=True,
            )
            for i in range(1, 7)
        ]

    def setUp(self):
        self.client = APIClient()

        self.url = reverse("notification-list")

    def authenticate(self, user=None):
        self.client.force_authenticate(
            user=user or self.user,
        )

    # ========================================================
    # HELPERS
    # ========================================================

    def create_notification(
        self,
        *,
        recipient=None,
        notification_type=Notification.Type.SYSTEM_ANNOUNCEMENT,
        category=Notification.Category.SYSTEM,
        latest_event_at=None,
        event_count=0,
        deleted_at=None,
    ):
        return Notification.objects.create(
            recipient=recipient or self.user,
            category=category,
            notification_type=notification_type,
            event_count=event_count,
            latest_event_at=(
                latest_event_at or timezone.now()
            ),
            deleted_at=deleted_at,
        )

    def create_event(
        self,
        *,
        notification,
        actor,
        event_type=NotificationEvent.Type.SYSTEM_ANNOUNCEMENT,
        is_active=True,
    ):
        return NotificationEvent.objects.create(
            notification=notification,
            recipient=notification.recipient,
            actor=actor,
            event_type=event_type,
            is_active=is_active,
        )

    def get_next_cursor(self, response):
        next_url = response.data["next"]

        self.assertIsNotNone(next_url)

        query_params = parse_qs(
            urlparse(next_url).query,
        )

        return query_params["cursor"][0]

    # ========================================================
    # AUTHENTICATION AND PERMISSIONS
    # ========================================================

    def test_unauthenticated_user_cannot_access_notifications(
        self,
    ):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_authenticated_user_can_access_notification_list(
        self,
    ):
        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "results",
            response.data,
        )

    # ========================================================
    # RECIPIENT ISOLATION
    # ========================================================

    def test_user_only_receives_own_notifications(self):
        own_notification = self.create_notification()

        other_notification = self.create_notification(
            recipient=self.other_user,
        )

        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        returned_ids = {
            item["id"]
            for item in response.data["results"]
        }

        self.assertIn(
            own_notification.pk,
            returned_ids,
        )

        self.assertNotIn(
            other_notification.pk,
            returned_ids,
        )

    def test_other_users_notifications_never_appear_on_next_page(
        self,
    ):
        now = timezone.now()

        for index in range(25):
            self.create_notification(
                latest_event_at=now + timedelta(
                    seconds=index,
                ),
            )

        for index in range(5):
            self.create_notification(
                recipient=self.other_user,
                latest_event_at=now + timedelta(
                    seconds=100 + index,
                ),
            )

        self.authenticate()

        first_response = self.client.get(self.url)

        self.assertEqual(
            first_response.status_code,
            200,
        )

        cursor = self.get_next_cursor(first_response)

        second_response = self.client.get(
            self.url,
            {"cursor": cursor},
        )

        self.assertEqual(
            second_response.status_code,
            200,
        )

        all_results = (
            first_response.data["results"]
            + second_response.data["results"]
        )

        self.assertEqual(
            len(all_results),
            25,
        )

        for item in all_results:
            notification = Notification.objects.get(
                pk=item["id"],
            )

            self.assertEqual(
                notification.recipient_id,
                self.user.pk,
            )

    # ========================================================
    # SOFT DELETION
    # ========================================================

    def test_deleted_notifications_are_excluded(self):
        visible_notification = self.create_notification()

        deleted_notification = self.create_notification(
            deleted_at=timezone.now(),
        )

        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        returned_ids = {
            item["id"]
            for item in response.data["results"]
        }

        self.assertIn(
            visible_notification.pk,
            returned_ids,
        )

        self.assertNotIn(
            deleted_notification.pk,
            returned_ids,
        )

    # ========================================================
    # NOTIFICATION SERIALIZATION
    # ========================================================

    def test_notification_returns_expected_fields(self):
        notification = self.create_notification()

        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        item = next(
            item
            for item in response.data["results"]
            if item["id"] == notification.pk
        )

        expected_fields = {
            "id",
            "category",
            "notification_type",
            "metadata",
            "target",
            "event_count",
            "is_read",
            "read_at",
            "actors",
            "latest_event_at",
            "created_at",
        }

        self.assertEqual(
            set(item.keys()),
            expected_fields,
        )

        self.assertFalse(item["is_read"])
        self.assertEqual(item["event_count"], 0)
        self.assertEqual(item["actors"], [])
        self.assertIsNone(item["target"])

    def test_read_notification_returns_correct_read_state(
        self,
    ):
        notification = self.create_notification()

        notification.read_at = timezone.now()
        notification.save(update_fields=["read_at"])

        self.authenticate()

        response = self.client.get(self.url)

        item = next(
            item
            for item in response.data["results"]
            if item["id"] == notification.pk
        )

        self.assertTrue(item["is_read"])
        self.assertIsNotNone(item["read_at"])

    # ========================================================
    # ACTOR SERIALIZATION
    # ========================================================

    def test_notification_returns_latest_three_active_actors(
        self,
    ):
        notification = self.create_notification(
            notification_type=(
                Notification.Type.COMMUNITY_POST_LIKE
            ),
            category=Notification.Category.ACTIVITY,
            event_count=5,
        )

        for actor in self.actors[:5]:
            self.create_event(
                notification=notification,
                actor=actor,
                event_type=(
                    NotificationEvent.Type.COMMUNITY_POST_LIKE
                ),
            )

        self.authenticate()

        response = self.client.get(self.url)

        item = next(
            item
            for item in response.data["results"]
            if item["id"] == notification.pk
        )

        self.assertEqual(
            len(item["actors"]),
            3,
        )

        returned_actor_ids = [
            actor["id"]
            for actor in item["actors"]
        ]

        expected_actor_ids = [
            actor.pk
            for actor in reversed(self.actors[:5][-3:])
        ]

        self.assertEqual(
            returned_actor_ids,
            expected_actor_ids,
        )

        self.assertEqual(
            item["event_count"],
            5,
        )

    def test_inactive_events_are_excluded_from_actors(
        self,
    ):
        notification = self.create_notification(
            notification_type=(
                Notification.Type.COMMUNITY_POST_LIKE
            ),
            category=Notification.Category.ACTIVITY,
            event_count=2,
        )

        active_actor = self.actors[0]
        inactive_actor = self.actors[1]

        self.create_event(
            notification=notification,
            actor=active_actor,
            event_type=(
                NotificationEvent.Type.COMMUNITY_POST_LIKE
            ),
            is_active=True,
        )

        self.create_event(
            notification=notification,
            actor=inactive_actor,
            event_type=(
                NotificationEvent.Type.COMMUNITY_POST_LIKE
            ),
            is_active=False,
        )

        self.authenticate()

        response = self.client.get(self.url)

        item = next(
            item
            for item in response.data["results"]
            if item["id"] == notification.pk
        )

        self.assertEqual(
            len(item["actors"]),
            1,
        )

        self.assertEqual(
            item["actors"][0]["id"],
            active_actor.pk,
        )

    def test_deleted_actor_does_not_break_notification_serialization(
        self,
    ):
        notification = self.create_notification(
            notification_type=(
                Notification.Type.COMMUNITY_POST_LIKE
            ),
            category=Notification.Category.ACTIVITY,
            event_count=1,
        )

        deleted_actor = self.actors[0]

        self.create_event(
            notification=notification,
            actor=deleted_actor,
            event_type=(
                NotificationEvent.Type.COMMUNITY_POST_LIKE
            ),
        )

        deleted_actor.delete()

        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        item = next(
            item
            for item in response.data["results"]
            if item["id"] == notification.pk
        )

        self.assertEqual(
            item["actors"],
            [],
        )

    # ========================================================
    # CURSOR PAGINATION
    # ========================================================

    def test_notification_list_uses_twenty_item_pages(self):
        now = timezone.now()

        for index in range(25):
            self.create_notification(
                latest_event_at=now + timedelta(
                    seconds=index,
                ),
            )

        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data["results"]),
            20,
        )

        self.assertIsNotNone(
            response.data["next"],
        )

        self.assertIsNone(
            response.data["previous"],
        )

    def test_cursor_pagination_returns_remaining_notifications(
        self,
    ):
        now = timezone.now()

        for index in range(25):
            self.create_notification(
                latest_event_at=now + timedelta(
                    seconds=index,
                ),
            )

        self.authenticate()

        first_response = self.client.get(self.url)

        cursor = self.get_next_cursor(first_response)

        second_response = self.client.get(
            self.url,
            {"cursor": cursor},
        )

        self.assertEqual(
            second_response.status_code,
            200,
        )

        self.assertEqual(
            len(second_response.data["results"]),
            5,
        )

        self.assertIsNone(
            second_response.data["next"],
        )

    def test_cursor_pagination_does_not_return_duplicates(
        self,
    ):
        now = timezone.now()

        for index in range(45):
            self.create_notification(
                latest_event_at=now + timedelta(
                    seconds=index,
                ),
            )

        self.authenticate()

        first_response = self.client.get(self.url)

        first_ids = [
            item["id"]
            for item in first_response.data["results"]
        ]

        cursor = self.get_next_cursor(first_response)

        second_response = self.client.get(
            self.url,
            {"cursor": cursor},
        )

        second_ids = [
            item["id"]
            for item in second_response.data["results"]
        ]

        self.assertEqual(
            len(first_ids),
            20,
        )

        self.assertEqual(
            len(second_ids),
            20,
        )

        self.assertTrue(
            set(first_ids).isdisjoint(second_ids),
        )

    def test_cursor_pagination_preserves_newest_first_order(
        self,
    ):
        now = timezone.now()

        notifications = [
            self.create_notification(
                latest_event_at=now + timedelta(
                    seconds=index,
                ),
            )
            for index in range(25)
        ]

        expected_ids = [
            notification.pk
            for notification in reversed(notifications)
        ]

        self.authenticate()

        first_response = self.client.get(self.url)

        cursor = self.get_next_cursor(first_response)

        second_response = self.client.get(
            self.url,
            {"cursor": cursor},
        )

        returned_ids = [
            item["id"]
            for item in (
                first_response.data["results"]
                + second_response.data["results"]
            )
        ]

        self.assertEqual(
            returned_ids,
            expected_ids,
        )

    # ========================================================
    # QUERY PERFORMANCE
    # ========================================================

    def test_notification_list_avoids_n_plus_one_actor_queries(
        self,
    ):
        now = timezone.now()

        for index in range(20):
            notification = self.create_notification(
                notification_type=(
                    Notification.Type.COMMUNITY_POST_LIKE
                ),
                category=Notification.Category.ACTIVITY,
                latest_event_at=now + timedelta(
                    seconds=index,
                ),
                event_count=3,
            )

            for actor in self.actors[:3]:
                self.create_event(
                    notification=notification,
                    actor=actor,
                    event_type=(
                        NotificationEvent.Type.COMMUNITY_POST_LIKE
                    ),
                )

        self.authenticate()

        with self.assertNumQueries(3):
            response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data["results"]),
            20,
        )