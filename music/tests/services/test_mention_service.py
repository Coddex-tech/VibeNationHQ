
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone

from music.models import (
    CommunityPost,
    CommunityPostComment,
    EditorialArticle,
    EditorialComment,
    UserMention,
)
from music.services.mentions import MentionService

from notifications.models import (
    Notification,
    NotificationEvent,
)


User = get_user_model()


class MentionServiceTests(TestCase):
    COMMUNITY_POST_MENTION = "community_post_mention"
    COMMUNITY_COMMENT_MENTION = "community_comment_mention"
    EDITORIAL_COMMENT_MENTION = "editorial_comment_mention"

    @classmethod
    def setUpTestData(cls):
        cls.mentioner = User.objects.create_user(
            username="mentioner",
            email="mentioner@example.com",
            password="test-password",
        )

        cls.mentioned_user = User.objects.create_user(
            username="mentioned_user",
            email="mentioned@example.com",
            password="test-password",
        )

        cls.second_mentioned_user = User.objects.create_user(
            username="second_user",
            email="second@example.com",
            password="test-password",
        )

        cls.inactive_user = User.objects.create_user(
            username="inactive_user",
            email="inactive@example.com",
            password="test-password",
            is_active=False,
        )

        cls.staff_user = User.objects.create_superuser(
            username="staff_user",
            email="staff@example.com",
            password="test-password",
        )

        cls.article_author = User.objects.create_user(
            username="article_author",
            email="articleauthor@example.com",
            password="test-password",
        )

        cls.article = EditorialArticle.objects.create(
            author=cls.article_author,
            title="Testing Mention Service",
            slug="testing-mention-service",
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now(),
        )

    # ========================================================
    # Helpers
    # ========================================================

    def create_community_post(self, *, content):
        return CommunityPost.objects.create(
            user=self.mentioner,
            content=content,
            slug=f"mention-test-{CommunityPost.objects.count()}",
        )

    def create_community_comment(self, *, content):
        post = self.create_community_post(
            content="Post for mention testing.",
        )

        return CommunityPostComment.objects.create(
            user=self.mentioner,
            post=post,
            content=content,
        )

    def create_editorial_comment(self, *, content):
        return EditorialComment.objects.create(
            user=self.mentioner,
            article=self.article,
            content=content,
        )

    def get_mentions(self, content_object):
        content_type = ContentType.objects.get_for_model(
            content_object,
            for_concrete_model=False,
        )

        return UserMention.objects.filter(
            content_type=content_type,
            object_id=str(content_object.pk),
        )

    def get_events(self, *, recipient, event_type):
        return NotificationEvent.objects.filter(
            recipient=recipient,
            event_type=event_type,
        )

    def assert_mention_notification(
        self,
        *,
        recipient,
        event_type,
        content_object,
    ):
        event = self.get_events(
            recipient=recipient,
            event_type=event_type,
        ).get()

        self.assertEqual(event.actor, self.mentioner)
        self.assertEqual(event.target, content_object)

        self.assertIsNotNone(event.notification)

        self.assertEqual(
            event.notification.recipient,
            recipient,
        )

        self.assertEqual(
            event.notification.category,
            Notification.Category.MENTIONS,
        )

        self.assertIsNone(
            event.notification.grouping_key,
        )

        self.assertEqual(
            event.notification.event_count,
            1,
        )

        return event

    # ========================================================
    # Username extraction and resolution
    # ========================================================

    def test_username_matching_is_case_insensitive(self):
        post = self.create_community_post(
            content="@MENTIONED_USER",
        )

        mentions = MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        self.assertEqual(len(mentions), 1)

        self.assertEqual(
            mentions[0].mentioned_user,
            self.mentioned_user,
        )

    def test_repeated_mentions_create_one_relationship(self):
        post = self.create_community_post(
            content=(
                "@mentioned_user "
                "@MENTIONED_USER "
                "@Mentioned_User"
            ),
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        self.assertEqual(
            self.get_mentions(post).count(),
            1,
        )

        self.assertEqual(
            self.get_events(
                recipient=self.mentioned_user,
                event_type=self.COMMUNITY_POST_MENTION,
            ).count(),
            1,
        )

    def test_nonexistent_username_is_ignored(self):
        post = self.create_community_post(
            content="@account_that_does_not_exist",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        self.assertFalse(
            self.get_mentions(post).exists(),
        )

        self.assertFalse(
            NotificationEvent.objects.exists(),
        )

    def test_inactive_account_is_ignored(self):
        post = self.create_community_post(
            content="@inactive_user",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        self.assertFalse(
            self.get_mentions(post).exists(),
        )

        self.assertFalse(
            self.get_events(
                recipient=self.inactive_user,
                event_type=self.COMMUNITY_POST_MENTION,
            ).exists(),
        )

    def test_staff_account_is_ignored(self):
        post = self.create_community_post(
            content="@staff_user",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        self.assertFalse(
            self.get_mentions(post).exists(),
        )

        self.assertFalse(
            self.get_events(
                recipient=self.staff_user,
                event_type=self.COMMUNITY_POST_MENTION,
            ).exists(),

        
        )

    def test_email_address_does_not_create_a_mention(self):
        post = self.create_community_post(
            content="Contact person@mentioned_user.example.com",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        self.assertFalse(
            self.get_mentions(post).exists(),
        )

    # ========================================================
    # Community post mentions
    # ========================================================

    def test_community_post_mention_creates_relationship(self):
        post = self.create_community_post(
            content="Hello @mentioned_user",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        mention = self.get_mentions(post).get()

        self.assertEqual(
            mention.mentioner,
            self.mentioner,
        )

        self.assertEqual(
            mention.mentioned_user,
            self.mentioned_user,
        )

        self.assertEqual(
            mention.content_object,
            post,
        )

    def test_community_post_mention_creates_notification(self):
        post = self.create_community_post(
            content="Hello @mentioned_user",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        self.assert_mention_notification(
            recipient=self.mentioned_user,
            event_type=self.COMMUNITY_POST_MENTION,
            content_object=post,
        )

    # ========================================================
    # Community comment mentions
    # ========================================================

    def test_community_comment_mention_creates_relationship(self):
        comment = self.create_community_comment(
            content="Hello @mentioned_user",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=comment,
            content=comment.content,
        )

        mention = self.get_mentions(comment).get()

        self.assertEqual(
            mention.mentioned_user,
            self.mentioned_user,
        )

        self.assertEqual(
            mention.content_object,
            comment,
        )

    def test_community_comment_mention_creates_notification(self):
        comment = self.create_community_comment(
            content="Hello @mentioned_user",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=comment,
            content=comment.content,
        )

        self.assert_mention_notification(
            recipient=self.mentioned_user,
            event_type=self.COMMUNITY_COMMENT_MENTION,
            content_object=comment,
        )

    # ========================================================
    # Editorial comment mentions
    # ========================================================

    def test_editorial_comment_mention_creates_relationship(self):
        comment = self.create_editorial_comment(
            content="Hello @mentioned_user",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=comment,
            content=comment.content,
        )

        mention = self.get_mentions(comment).get()

        self.assertEqual(
            mention.mentioned_user,
            self.mentioned_user,
        )

        self.assertEqual(
            mention.content_object,
            comment,
        )

    def test_editorial_comment_mention_creates_notification(self):
        comment = self.create_editorial_comment(
            content="Hello @mentioned_user",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=comment,
            content=comment.content,
        )

        self.assert_mention_notification(
            recipient=self.mentioned_user,
            event_type=self.EDITORIAL_COMMENT_MENTION,
            content_object=comment,
        )

    # ========================================================
    # Multiple mentions
    # ========================================================

    def test_multiple_users_receive_individual_notifications(self):
        post = self.create_community_post(
            content="@mentioned_user @second_user",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        self.assertEqual(
            self.get_mentions(post).count(),
            2,
        )

        first_event = self.get_events(
            recipient=self.mentioned_user,
            event_type=self.COMMUNITY_POST_MENTION,
        ).get()

        second_event = self.get_events(
            recipient=self.second_mentioned_user,
            event_type=self.COMMUNITY_POST_MENTION,
        ).get()

        self.assertNotEqual(
            first_event.notification_id,
            second_event.notification_id,
        )

        self.assertIsNone(
            first_event.notification.grouping_key,
        )

        self.assertIsNone(
            second_event.notification.grouping_key,
        )

    # ========================================================
    # Self-mentions
    # ========================================================

    def test_self_mention_is_stored_without_notification(self):
        post = self.create_community_post(
            content="I am mentioning myself @mentioner",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        mention = self.get_mentions(post).get()

        self.assertEqual(
            mention.mentioned_user,
            self.mentioner,
        )

        self.assertFalse(
            self.get_events(
                recipient=self.mentioner,
                event_type=self.COMMUNITY_POST_MENTION,
            ).exists(),
        )

    # ========================================================
    # Editing content
    # ========================================================

    def test_unchanged_mention_does_not_create_duplicate_notification(self):
        post = self.create_community_post(
            content="Hello @mentioned_user",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        post.content = "Updated content. Hello again @mentioned_user"

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        self.assertEqual(
            self.get_mentions(post).count(),
            1,
        )

        self.assertEqual(
            self.get_events(
                recipient=self.mentioned_user,
                event_type=self.COMMUNITY_POST_MENTION,
            ).count(),
            1,
        )

    def test_new_mention_added_during_edit_creates_notification(self):
        post = self.create_community_post(
            content="Hello @mentioned_user",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        post.content = (
            "Hello @mentioned_user and @second_user"
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        self.assertEqual(
            self.get_mentions(post).count(),
            2,
        )

        self.assertEqual(
            self.get_events(
                recipient=self.second_mentioned_user,
                event_type=self.COMMUNITY_POST_MENTION,
            ).count(),
            1,
        )

    def test_removed_mention_relationship_is_deleted(self):
        post = self.create_community_post(
            content="Hello @mentioned_user",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        post.content = "The mention has been removed."

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        self.assertFalse(
            self.get_mentions(post).exists(),
        )

        # Historical notification events are intentionally retained.
        self.assertEqual(
            self.get_events(
                recipient=self.mentioned_user,
                event_type=self.COMMUNITY_POST_MENTION,
            ).count(),
            1,
        )

    def test_readding_removed_mention_creates_new_notification(self):
        post = self.create_community_post(
            content="Hello @mentioned_user",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        post.content = "Mention removed."

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        post.content = "Hello again @mentioned_user"

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        self.assertEqual(
            self.get_mentions(post).count(),
            1,
        )

        self.assertEqual(
            self.get_events(
                recipient=self.mentioned_user,
                event_type=self.COMMUNITY_POST_MENTION,
            ).count(),
            2,
        )

    # ========================================================
    # Explicit relationship deletion
    # ========================================================

    def test_delete_mentions_removes_all_content_relationships(self):
        post = self.create_community_post(
            content="@mentioned_user @second_user",
        )

        MentionService.sync_mentions(
            mentioner=self.mentioner,
            content_object=post,
            content=post.content,
        )

        deleted_count = MentionService.delete_mentions(
            content_object=post,
        )

        self.assertEqual(deleted_count, 2)

        self.assertFalse(
            self.get_mentions(post).exists(),
        )

    # ========================================================
    # Unsupported targets
    # ========================================================

    def test_unsupported_target_raises_value_error(self):
        with self.assertRaises(ValueError):
            MentionService.sync_mentions(
                mentioner=self.mentioner,
                content_object=self.article,
                content="@mentioned_user",
            )

    def test_unsaved_target_raises_value_error(self):
        unsaved_post = CommunityPost(
            user=self.mentioner,
            content="@mentioned_user",
            slug="unsaved-mention-post",
        )

        with self.assertRaises(ValueError):
            MentionService.sync_mentions(
                mentioner=self.mentioner,
                content_object=unsaved_post,
                content=unsaved_post.content,
            )
