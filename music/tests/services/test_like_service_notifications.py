from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from music.models import (
    CommunityPost,
    CommunityPostComment,
    EditorialArticle,
    EditorialComment,
)
from music.services.likes import (
    CommunityPostLikeService,
    CommunityPostCommentLikeService,
    EditorialArticleLikeService,
    EditorialCommentLikeService,
)
from notifications.models import NotificationEvent


User = get_user_model()


class LikeServiceNotificationTests(TestCase):
    """
    Tests notification integration for the like services.

    Expected behaviour:

    - Community post likes notify the post author.
    - Community comment likes notify the comment author.
    - Editorial comment likes notify the comment author.
    - Editorial article likes do not generate notifications.
    - Self-likes do not generate notifications.
    - Unlikes deactivate the corresponding notification event
      without deleting its history.
    """

    @classmethod
    def setUpTestData(cls):
        # Ordinary platform users.
        cls.owner = User.objects.create_user(
            email="owner@example.com",
            password="test-password",
        )

        cls.actor = User.objects.create_user(
            email="actor@example.com",
            password="test-password",
        )

        cls.other_actor = User.objects.create_user(
            email="other-actor@example.com",
            password="test-password",
        )

        # Staff account used as the editorial article author.
        cls.staff_author = User.objects.create_superuser(
            email="editor@example.com",
            password="test-password",
        )

        # Community post.
        cls.community_post = CommunityPost.objects.create(
            user=cls.owner,
            content="A community post for notification testing.",
            status=CommunityPost.Status.PUBLISHED,
        )

        # Community post comment.
        cls.community_comment = CommunityPostComment.objects.create(
            user=cls.owner,
            post=cls.community_post,
            content="A community comment for notification testing.",
            status=CommunityPostComment.Status.PUBLISHED,
        )

        # Published editorial article.
        cls.editorial_article = EditorialArticle.objects.create(
            title="Notification Testing Article",
            slug="notification-testing-article",
            content="Editorial article content for testing.",
            author=cls.staff_author,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        # Editorial comment.
        cls.editorial_comment = EditorialComment.objects.create(
            user=cls.owner,
            article=cls.editorial_article,
            content="An editorial comment for notification testing.",
            status=EditorialComment.Status.PUBLISHED,
        )

    # ========================================================
    # COMMUNITY POST LIKE TESTS
    # ========================================================

    def test_community_post_like_creates_notification_event(self):
        like = CommunityPostLikeService.create(
            user=self.actor,
            post=self.community_post,
        )

        self.assertIsNotNone(like.pk)

        event = NotificationEvent.objects.get(
            recipient=self.owner,
            actor=self.actor,
            event_type=(
                NotificationEvent.Type.COMMUNITY_POST_LIKE
            ),
        )

        self.assertTrue(event.is_active)
        self.assertEqual(event.target, self.community_post)

        self.community_post.refresh_from_db()

        self.assertEqual(
            self.community_post.likes_count,
            1,
        )

    def test_community_post_unlike_deactivates_notification_event(self):
        like = CommunityPostLikeService.create(
            user=self.actor,
            post=self.community_post,
        )

        CommunityPostLikeService.delete(
            like_instance=like,
        )

        event = NotificationEvent.objects.get(
            recipient=self.owner,
            actor=self.actor,
            event_type=(
                NotificationEvent.Type.COMMUNITY_POST_LIKE
            ),
        )

        # Event history is retained.
        self.assertFalse(event.is_active)

        self.community_post.refresh_from_db()

        self.assertEqual(
            self.community_post.likes_count,
            0,
        )

        self.assertTrue(
            NotificationEvent.objects.filter(
                pk=event.pk,
            ).exists()
        )

    def test_community_post_self_like_creates_no_notification(self):
        CommunityPostLikeService.create(
            user=self.owner,
            post=self.community_post,
        )

        self.assertFalse(
            NotificationEvent.objects.filter(
                recipient=self.owner,
                actor=self.owner,
                event_type=(
                    NotificationEvent.Type.COMMUNITY_POST_LIKE
                ),
            ).exists()
        )

        self.community_post.refresh_from_db()

        # The like itself is still valid.
        self.assertEqual(
            self.community_post.likes_count,
            1,
        )

    def test_unliking_one_post_does_not_deactivate_another_post_event(self):
        another_post = CommunityPost.objects.create(
            user=self.owner,
            content="Another post for target isolation testing.",
            slug="another-post-target-isolation",
            status=CommunityPost.Status.PUBLISHED,
        )

        first_like = CommunityPostLikeService.create(
            user=self.actor,
            post=self.community_post,
        )

        CommunityPostLikeService.create(
            user=self.actor,
            post=another_post,
        )

        CommunityPostLikeService.delete(
            like_instance=first_like,
        )

        first_event = NotificationEvent.objects.get(
            recipient=self.owner,
            actor=self.actor,
            event_type=(
                NotificationEvent.Type.COMMUNITY_POST_LIKE
            ),
            target_object_id=str(self.community_post.pk),
        )

        second_event = NotificationEvent.objects.get(
            recipient=self.owner,
            actor=self.actor,
            event_type=(
                NotificationEvent.Type.COMMUNITY_POST_LIKE
            ),
            target_object_id=str(another_post.pk),
        )

        self.assertFalse(first_event.is_active)
        self.assertTrue(second_event.is_active)

    # ========================================================
    # EDITORIAL COMMENT LIKE TESTS
    # ========================================================

    def test_editorial_comment_like_creates_notification_event(self):
        like = EditorialCommentLikeService.create(
            user=self.actor,
            comment=self.editorial_comment,
        )

        self.assertIsNotNone(like.pk)

        event = NotificationEvent.objects.get(
            recipient=self.owner,
            actor=self.actor,
            event_type=(
                NotificationEvent.Type.EDITORIAL_COMMENT_LIKE
            ),
        )

        self.assertTrue(event.is_active)
        self.assertEqual(event.target, self.editorial_comment)

        self.editorial_comment.refresh_from_db()

        self.assertEqual(
            self.editorial_comment.likes_count,
            1,
        )

    def test_editorial_comment_unlike_deactivates_notification_event(self):
        like = EditorialCommentLikeService.create(
            user=self.actor,
            comment=self.editorial_comment,
        )

        EditorialCommentLikeService.delete(
            like_instance=like,
        )

        event = NotificationEvent.objects.get(
            recipient=self.owner,
            actor=self.actor,
            event_type=(
                NotificationEvent.Type.EDITORIAL_COMMENT_LIKE
            ),
        )

        self.assertFalse(event.is_active)

        self.editorial_comment.refresh_from_db()

        self.assertEqual(
            self.editorial_comment.likes_count,
            0,
        )

    def test_editorial_comment_self_like_creates_no_notification(self):
        EditorialCommentLikeService.create(
            user=self.owner,
            comment=self.editorial_comment,
        )

        self.assertFalse(
            NotificationEvent.objects.filter(
                recipient=self.owner,
                actor=self.owner,
                event_type=(
                    NotificationEvent.Type.EDITORIAL_COMMENT_LIKE
                ),
            ).exists()
        )

        self.editorial_comment.refresh_from_db()

        self.assertEqual(
            self.editorial_comment.likes_count,
            1,
        )

    # ========================================================
    # COMMUNITY POST COMMENT LIKE TESTS
    # ========================================================

    def test_community_comment_like_creates_notification_event(self):
        like = CommunityPostCommentLikeService.create(
            user=self.actor,
            comment=self.community_comment,
        )

        self.assertIsNotNone(like.pk)

        event = NotificationEvent.objects.get(
            recipient=self.owner,
            actor=self.actor,
            event_type=(
                NotificationEvent.Type.COMMUNITY_COMMENT_LIKE
            ),
        )

        self.assertTrue(event.is_active)
        self.assertEqual(event.target, self.community_comment)

        self.community_comment.refresh_from_db()

        self.assertEqual(
            self.community_comment.likes_count,
            1,
        )

    def test_community_comment_unlike_deactivates_notification_event(self):
        like = CommunityPostCommentLikeService.create(
            user=self.actor,
            comment=self.community_comment,
        )

        CommunityPostCommentLikeService.delete(
            like_instance=like,
        )

        event = NotificationEvent.objects.get(
            recipient=self.owner,
            actor=self.actor,
            event_type=(
                NotificationEvent.Type.COMMUNITY_COMMENT_LIKE
            ),
        )

        self.assertFalse(event.is_active)

        self.community_comment.refresh_from_db()

        self.assertEqual(
            self.community_comment.likes_count,
            0,
        )

    def test_community_comment_self_like_creates_no_notification(self):
        CommunityPostCommentLikeService.create(
            user=self.owner,
            comment=self.community_comment,
        )

        self.assertFalse(
            NotificationEvent.objects.filter(
                recipient=self.owner,
                actor=self.owner,
                event_type=(
                    NotificationEvent.Type.COMMUNITY_COMMENT_LIKE
                ),
            ).exists()
        )

        self.community_comment.refresh_from_db()

        self.assertEqual(
            self.community_comment.likes_count,
            1,
        )

    # ========================================================
    # EDITORIAL ARTICLE LIKE TESTS
    # ========================================================

    def test_editorial_article_like_creates_no_notification(self):
        like = EditorialArticleLikeService.create(
            user=self.actor,
            article=self.editorial_article,
        )

        self.assertIsNotNone(like.pk)

        self.assertFalse(
            NotificationEvent.objects.filter(
                actor=self.actor,
                event_type=(
                    NotificationEvent.Type.EDITORIAL_ARTICLE_LIKE
                ),
            ).exists()
        )

        self.editorial_article.refresh_from_db()

        self.assertEqual(
            self.editorial_article.likes_count,
            1,
        )

    def test_editorial_article_unlike_does_not_create_notification(self):
        like = EditorialArticleLikeService.create(
            user=self.actor,
            article=self.editorial_article,
        )

        EditorialArticleLikeService.delete(
            like_instance=like,
        )

        self.assertFalse(
            NotificationEvent.objects.filter(
                actor=self.actor,
                event_type=(
                    NotificationEvent.Type.EDITORIAL_ARTICLE_LIKE
                ),
            ).exists()
        )

        self.editorial_article.refresh_from_db()

        self.assertEqual(
            self.editorial_article.likes_count,
            0,
        )
