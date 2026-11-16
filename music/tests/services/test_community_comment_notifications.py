from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from music.models import CommunityPost, CommunityPostComment
from music.services.community import CommunityPostCommentService

from notifications.models import (
    Notification,
    NotificationEvent,
)


User = get_user_model()


class CommunityPostCommentNotificationTests(TestCase):
    COMMUNITY_POST_COMMENT = "community_post_comment"
    COMMUNITY_COMMENT_REPLY = "community_comment_reply"

    @classmethod
    def setUpTestData(cls):
        cls.post_owner = User.objects.create_user(
            username="post_owner",
            email="postowner@example.com",
            password="test-password",
        )

        cls.commenter = User.objects.create_user(
            username="commenter",
            email="commenter@example.com",
            password="test-password",
        )

        cls.second_commenter = User.objects.create_user(
            username="second_commenter",
            email="secondcommenter@example.com",
            password="test-password",
        )

        cls.reply_author = User.objects.create_user(
            username="reply_author",
            email="replyauthor@example.com",
            password="test-password",
        )

        cls.post = CommunityPost.objects.create(
            user=cls.post_owner,
            content="Testing community post comments.",
            slug="notification-test-post",
        )

    def get_events(self, *, recipient, event_type):
        return NotificationEvent.objects.filter(
            recipient=recipient,
            event_type=event_type,
        )

    # ========================================================
    # Top-level comment notifications
    # ========================================================

    def test_top_level_comment_notifies_post_owner(self):
        comment = CommunityPostCommentService.create(
            user=self.commenter,
            post=self.post,
            content="This is a top-level comment.",
        )

        event = self.get_events(
            recipient=self.post_owner,
            event_type=self.COMMUNITY_POST_COMMENT,
        ).get()

        self.assertEqual(event.actor, self.commenter)
        self.assertEqual(event.target, self.post)

        self.assertEqual(
            event.metadata["comment_id"],
            str(comment.pk),
        )

        notification = event.notification

        self.assertIsNotNone(notification)
        self.assertEqual(notification.recipient, self.post_owner)
        self.assertEqual(
            notification.category,
            Notification.Category.ACTIVITY,
        )
        self.assertEqual(notification.event_count, 1)

        self.assertEqual(
            ContentType.objects.get_for_model(self.post),
            event.target_content_type,
        )

    def test_top_level_comment_does_not_notify_commenter(self):
        CommunityPostCommentService.create(
            user=self.commenter,
            post=self.post,
            content="A top-level comment.",
        )

        self.assertFalse(
            self.get_events(
                recipient=self.commenter,
                event_type=self.COMMUNITY_POST_COMMENT,
            ).exists()
        )

    def test_multiple_top_level_comments_on_same_post_are_grouped(self):
        first_comment = CommunityPostCommentService.create(
            user=self.commenter,
            post=self.post,
            content="First comment.",
        )

        second_comment = CommunityPostCommentService.create(
            user=self.second_commenter,
            post=self.post,
            content="Second comment.",
        )

        events = self.get_events(
            recipient=self.post_owner,
            event_type=self.COMMUNITY_POST_COMMENT,
        ).order_by("created_at")

        self.assertEqual(events.count(), 2)

        first_event = events.get(
            metadata__comment_id=str(first_comment.pk),
        )

        second_event = events.get(
            metadata__comment_id=str(second_comment.pk),
        )

        self.assertEqual(
            first_event.target_object_id,
            str(self.post.pk),
        )
        self.assertEqual(
            second_event.target_object_id,
            str(self.post.pk),
        )

        self.assertEqual(
            first_event.notification_id,
            second_event.notification_id,
        )

        notification = first_event.notification

        self.assertEqual(notification.event_count, 2)
        self.assertEqual(notification.recipient, self.post_owner)

    def test_post_owner_comment_does_not_notify_post_owner(self):
        CommunityPostCommentService.create(
            user=self.post_owner,
            post=self.post,
            content="Commenting on my own post.",
        )

        self.assertFalse(
            self.get_events(
                recipient=self.post_owner,
                event_type=self.COMMUNITY_POST_COMMENT,
            ).exists()
        )

    # ========================================================
    # Reply notifications
    # ========================================================

    def test_reply_notifies_direct_parent_comment_author(self):
        parent = CommunityPostComment.objects.create(
            user=self.reply_author,
            post=self.post,
            content="This is the parent comment.",
        )

        reply = CommunityPostCommentService.create(
            user=self.commenter,
            post=self.post,
            parent=parent,
            content="This is a reply.",
        )

        event = self.get_events(
            recipient=self.reply_author,
            event_type=self.COMMUNITY_COMMENT_REPLY,
        ).get()

        self.assertEqual(event.actor, self.commenter)
        self.assertEqual(event.target, reply)

        self.assertEqual(
            event.metadata["comment_id"],
            str(reply.pk),
        )
        self.assertEqual(
            event.metadata["parent_comment_id"],
            str(parent.pk),
        )
        self.assertEqual(
            event.metadata["root_comment_id"],
            str(parent.pk),
        )

        self.assertIsNotNone(event.notification)
        self.assertEqual(
            event.notification.recipient,
            self.reply_author,
        )

    def test_replies_create_individual_notifications(self):
        parent = CommunityPostComment.objects.create(
            user=self.reply_author,
            post=self.post,
            content="Parent comment.",
        )

        first_reply = CommunityPostCommentService.create(
            user=self.commenter,
            post=self.post,
            parent=parent,
            content="First reply.",
        )

        second_reply = CommunityPostCommentService.create(
            user=self.second_commenter,
            post=self.post,
            parent=parent,
            content="Second reply.",
        )

        events = self.get_events(
            recipient=self.reply_author,
            event_type=self.COMMUNITY_COMMENT_REPLY,
        )

        self.assertEqual(events.count(), 2)

        first_event = events.get(
            target_object_id=str(first_reply.pk),
        )

        second_event = events.get(
            target_object_id=str(second_reply.pk),
        )

        self.assertIsNotNone(first_event.notification)
        self.assertIsNotNone(second_event.notification)

        self.assertNotEqual(
            first_event.notification_id,
            second_event.notification_id,
        )

        self.assertEqual(
            first_event.notification.event_count,
            1,
        )
        self.assertEqual(
            second_event.notification.event_count,
            1,
        )

        self.assertIsNone(
            first_event.notification.grouping_key,
        )
        self.assertIsNone(
            second_event.notification.grouping_key,
        )

    def test_nested_reply_notifies_direct_parent_author(self):
        root_comment = CommunityPostComment.objects.create(
            user=self.post_owner,
            post=self.post,
            content="Root comment.",
        )

        first_reply = CommunityPostComment.objects.create(
            user=self.reply_author,
            post=self.post,
            parent=root_comment,
            root_comment=root_comment,
            content="First-level reply.",
        )

        nested_reply = CommunityPostCommentService.create(
            user=self.commenter,
            post=self.post,
            parent=first_reply,
            content="Nested reply.",
        )

        event = self.get_events(
            recipient=self.reply_author,
            event_type=self.COMMUNITY_COMMENT_REPLY,
        ).get()

        self.assertEqual(event.actor, self.commenter)
        self.assertEqual(event.target, nested_reply)

        self.assertEqual(
            event.metadata["comment_id"],
            str(nested_reply.pk),
        )
        self.assertEqual(
            event.metadata["parent_comment_id"],
            str(first_reply.pk),
        )
        self.assertEqual(
            event.metadata["root_comment_id"],
            str(root_comment.pk),
        )

    def test_reply_does_not_notify_when_replying_to_own_comment(self):
        parent = CommunityPostComment.objects.create(
            user=self.commenter,
            post=self.post,
            content="My own comment.",
        )

        CommunityPostCommentService.create(
            user=self.commenter,
            post=self.post,
            parent=parent,
            content="Replying to my own comment.",
        )

        self.assertFalse(
            self.get_events(
                recipient=self.commenter,
                event_type=self.COMMUNITY_COMMENT_REPLY,
            ).exists()
        )

    # ========================================================
    # Comment counter regression tests
    # ========================================================

    def test_comment_creation_still_updates_post_counter(self):
        initial_count = self.post.comments_count

        CommunityPostCommentService.create(
            user=self.commenter,
            post=self.post,
            content="A new comment.",
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.comments_count,
            initial_count + 1,
        )

    def test_reply_creation_still_updates_comment_counters(self):
        parent = CommunityPostComment.objects.create(
            user=self.reply_author,
            post=self.post,
            content="Parent comment.",
        )

        initial_post_count = self.post.comments_count
        initial_reply_count = parent.replies_count

        reply = CommunityPostCommentService.create(
            user=self.commenter,
            post=self.post,
            parent=parent,
            content="A reply.",
        )

        self.post.refresh_from_db()
        parent.refresh_from_db()

        self.assertEqual(
            self.post.comments_count,
            initial_post_count + 1,
        )
        self.assertEqual(
            parent.replies_count,
            initial_reply_count + 1,
        )
        self.assertEqual(reply.parent_id, parent.pk)
