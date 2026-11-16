from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from music.models import EditorialArticle, EditorialComment
from music.services.editorial import EditorialCommentService

from notifications.models import (
    Notification,
    NotificationEvent,
)


User = get_user_model()


class EditorialCommentNotificationTests(TestCase):
    EDITORIAL_COMMENT_REPLY = "editorial_comment_reply"
    EDITORIAL_ARTICLE_COMMENT = "editorial_article_comment"

    @classmethod
    def setUpTestData(cls):
        cls.staff_author = User.objects.create_user(
            username="editorial_staff",
            email="staff@example.com",
            password="test-password",
        )

        cls.commenter = User.objects.create_user(
            username="editorial_commenter",
            email="commenter@example.com",
            password="test-password",
        )

        cls.second_commenter = User.objects.create_user(
            username="editorial_second_commenter",
            email="secondcommenter@example.com",
            password="test-password",
        )

        cls.reply_author = User.objects.create_user(
            username="editorial_reply_author",
            email="replyauthor@example.com",
            password="test-password",
        )

        cls.article = EditorialArticle.objects.create(
            author=cls.staff_author,
            title="Testing Editorial Comments",
            slug="testing-editorial-comments",
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now()
        )

    def get_events(self, *, recipient, event_type):
        return NotificationEvent.objects.filter(
            recipient=recipient,
            event_type=event_type,
        )

    # ========================================================
    # Top-level editorial comments
    # ========================================================

    def test_top_level_comment_does_not_notify_staff_author(self):
        EditorialCommentService.create(
            user=self.commenter,
            article=self.article,
            content="A comment on the article.",
        )

        self.assertFalse(
            self.get_events(
                recipient=self.staff_author,
                event_type=self.EDITORIAL_ARTICLE_COMMENT,
            ).exists()
        )

    def test_top_level_comment_does_not_notify_commenter(self):
        EditorialCommentService.create(
            user=self.commenter,
            article=self.article,
            content="A comment on the article.",
        )

        self.assertFalse(
            self.get_events(
                recipient=self.commenter,
                event_type=self.EDITORIAL_ARTICLE_COMMENT,
            ).exists()
        )

    # ========================================================
    # Editorial comment replies
    # ========================================================

    def test_reply_notifies_direct_parent_comment_author(self):
        parent = EditorialComment.objects.create(
            user=self.reply_author,
            article=self.article,
            content="This is the parent comment.",
        )

        reply = EditorialCommentService.create(
            user=self.commenter,
            article=self.article,
            parent=parent,
            content="This is a reply.",
        )

        event = self.get_events(
            recipient=self.reply_author,
            event_type=self.EDITORIAL_COMMENT_REPLY,
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

        self.assertEqual(
            event.notification.category,
            Notification.Category.ACTIVITY,
        )

    def test_multiple_replies_create_individual_notifications(self):
        parent = EditorialComment.objects.create(
            user=self.reply_author,
            article=self.article,
            content="Parent comment.",
        )

        first_reply = EditorialCommentService.create(
            user=self.commenter,
            article=self.article,
            parent=parent,
            content="First reply.",
        )

        second_reply = EditorialCommentService.create(
            user=self.second_commenter,
            article=self.article,
            parent=parent,
            content="Second reply.",
        )

        events = self.get_events(
            recipient=self.reply_author,
            event_type=self.EDITORIAL_COMMENT_REPLY,
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
        root_comment = EditorialComment.objects.create(
            user=self.staff_author,
            article=self.article,
            content="Root comment.",
        )

        first_reply = EditorialComment.objects.create(
            user=self.reply_author,
            article=self.article,
            parent=root_comment,
            root_comment=root_comment,
            content="First-level reply.",
        )

        nested_reply = EditorialCommentService.create(
            user=self.commenter,
            article=self.article,
            parent=first_reply,
            content="Nested reply.",
        )

        event = self.get_events(
            recipient=self.reply_author,
            event_type=self.EDITORIAL_COMMENT_REPLY,
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
        parent = EditorialComment.objects.create(
            user=self.commenter,
            article=self.article,
            content="My own comment.",
        )

        EditorialCommentService.create(
            user=self.commenter,
            article=self.article,
            parent=parent,
            content="Replying to my own comment.",
        )

        self.assertFalse(
            self.get_events(
                recipient=self.commenter,
                event_type=self.EDITORIAL_COMMENT_REPLY,
            ).exists()
        )

    # ========================================================
    # Comment counter regression tests
    # ========================================================

    def test_comment_creation_updates_article_counter(self):
        initial_count = self.article.comments_count

        EditorialCommentService.create(
            user=self.commenter,
            article=self.article,
            content="A new editorial comment.",
        )

        self.article.refresh_from_db()

        self.assertEqual(
            self.article.comments_count,
            initial_count + 1,
        )

    def test_reply_creation_updates_comment_counters(self):
        parent = EditorialComment.objects.create(
            user=self.reply_author,
            article=self.article,
            content="Parent comment.",
        )

        initial_article_count = self.article.comments_count
        initial_reply_count = parent.replies_count

        reply = EditorialCommentService.create(
            user=self.commenter,
            article=self.article,
            parent=parent,
            content="A reply.",
        )

        self.article.refresh_from_db()
        parent.refresh_from_db()

        self.assertEqual(
            self.article.comments_count,
            initial_article_count + 1,
        )

        self.assertEqual(
            parent.replies_count,
            initial_reply_count + 1,
        )

        self.assertEqual(reply.parent_id, parent.pk)
