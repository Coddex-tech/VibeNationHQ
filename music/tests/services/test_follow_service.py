
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from music.models import UserFollow
from music.services.follows import UserFollowService
from notifications.models import NotificationEvent


User = get_user_model()


class UserFollowServiceTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.follower = User.objects.create_user(
            email="follower@example.com",
            username="follower",
            password="TestPassword123!",
        )

        cls.followed = User.objects.create_user(
            email="followed@example.com",
            username="followed",
            password="TestPassword123!",
        )

        cls.another_followed = User.objects.create_user(
            email="another@example.com",
            username="another",
            password="TestPassword123!",
        )

    def get_follow_events(self, *, recipient=None, actor=None):
        events = NotificationEvent.objects.filter(
            event_type=NotificationEvent.Type.FOLLOW,
        )

        if recipient is not None:
            events = events.filter(recipient=recipient)

        if actor is not None:
            events = events.filter(actor=actor)

        return events

    # --------------------------------------------------
    # Create follow
    # --------------------------------------------------

    def test_create_follow_creates_relationship(self):
        follow = UserFollowService.create(
            follower=self.follower,
            following=self.followed,
        )

        self.assertIsInstance(follow, UserFollow)

        self.assertTrue(
            UserFollow.objects.filter(
                follower=self.follower,
                following=self.followed,
            ).exists()
        )

    def test_create_follow_creates_notification_event(self):
        UserFollowService.create(
            follower=self.follower,
            following=self.followed,
        )

        event = self.get_follow_events(
            recipient=self.followed,
            actor=self.follower,
        ).get()

        self.assertEqual(
            event.event_type,
            NotificationEvent.Type.FOLLOW,
        )
        self.assertTrue(event.is_active)

    def test_create_follow_does_not_notify_follower(self):
        UserFollowService.create(
            follower=self.follower,
            following=self.followed,
        )

        self.assertFalse(
            self.get_follow_events(
                recipient=self.follower,
                actor=self.follower,
            ).exists()
        )

    def test_create_follow_rejects_self_follow(self):
        with self.assertRaises(ValidationError):
            UserFollowService.create(
                follower=self.follower,
                following=self.follower,
            )

        self.assertFalse(
            UserFollow.objects.filter(
                follower=self.follower,
                following=self.follower,
            ).exists()
        )

        self.assertFalse(
            self.get_follow_events().exists()
        )

    def test_create_follow_rejects_duplicate_follow(self):
        UserFollowService.create(
            follower=self.follower,
            following=self.followed,
        )

        with self.assertRaises(ValidationError):
            UserFollowService.create(
                follower=self.follower,
                following=self.followed,
            )

        self.assertEqual(
            UserFollow.objects.filter(
                follower=self.follower,
                following=self.followed,
            ).count(),
            1,
        )

        self.assertEqual(
            self.get_follow_events(
                recipient=self.followed,
                actor=self.follower,
            ).count(),
            1,
        )

    # --------------------------------------------------
    # Delete follow
    # --------------------------------------------------

    def test_delete_follow_removes_relationship(self):
        follow = UserFollowService.create(
            follower=self.follower,
            following=self.followed,
        )

        UserFollowService.delete(
            follow_instance=follow,
        )

        self.assertFalse(
            UserFollow.objects.filter(
                follower=self.follower,
                following=self.followed,
            ).exists()
        )

    def test_delete_follow_deactivates_notification_event(self):
        follow = UserFollowService.create(
            follower=self.follower,
            following=self.followed,
        )

        UserFollowService.delete(
            follow_instance=follow,
        )

        event = self.get_follow_events(
            recipient=self.followed,
            actor=self.follower,
        ).get()

        self.assertFalse(event.is_active)

    def test_delete_follow_preserves_notification_event_history(self):
        follow = UserFollowService.create(
            follower=self.follower,
            following=self.followed,
        )

        event_id = self.get_follow_events(
            recipient=self.followed,
            actor=self.follower,
        ).get().pk

        UserFollowService.delete(
            follow_instance=follow,
        )

        self.assertTrue(
            NotificationEvent.objects.filter(
                pk=event_id,
            ).exists()
        )

    def test_delete_follow_does_not_deactivate_another_users_event(self):
        first_follow = UserFollowService.create(
            follower=self.follower,
            following=self.followed,
        )

        UserFollowService.create(
            follower=self.follower,
            following=self.another_followed,
        )

        UserFollowService.delete(
            follow_instance=first_follow,
        )

        first_event = self.get_follow_events(
            recipient=self.followed,
            actor=self.follower,
        ).get()

        second_event = self.get_follow_events(
            recipient=self.another_followed,
            actor=self.follower,
        ).get()

        self.assertFalse(first_event.is_active)
        self.assertTrue(second_event.is_active)

    def test_delete_nonexistent_follow_does_not_raise_error(self):
        follow = UserFollowService.create(
            follower=self.follower,
            following=self.followed,
        )

        follow_id = follow.pk

        UserFollowService.delete(
            follow_instance=follow,
        )

        # Calling delete again should be harmless.
        UserFollowService.delete(
            follow_instance=follow,
        )

        self.assertFalse(
            UserFollow.objects.filter(
                pk=follow_id,
            ).exists()
        )
