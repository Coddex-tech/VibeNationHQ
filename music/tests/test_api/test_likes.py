from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from music.models import (
    CommunityPost,
    CommunityPostComment,
    CommunityPostCommentLike,
    CommunityPostLike,
    EditorialArticle,
    EditorialArticleLike,
    EditorialComment,
    EditorialCommentLike,
    MusicFeedInteraction,
)

User = get_user_model()


# ============================================================
# EDITORIAL ARTICLE LIKE
# ============================================================

class EditorialArticleLikeAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="article_like_user",
            email="article_like_user@example.com",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="article_like_other",
            email="article_like_other@example.com",
            password="testpass123",
        )

        self.article = EditorialArticle.objects.create(
            title="Published Article",
            slug="published-article",
            content="This is a published article.",
            author=self.user,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.draft_article = EditorialArticle.objects.create(
            title="Draft Article",
            slug="draft-article",
            content="This is a draft article.",
            author=self.user,
            status=EditorialArticle.Status.DRAFT,
        )

    def get_url(self, article_id):
        return f"/api/v1/music/editorial/{article_id}/like/"

    def test_anonymous_user_cannot_like_article(self):
        response = self.client.post(
            self.get_url(self.article.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_anonymous_user_cannot_unlike_article(self):
        response = self.client.delete(
            self.get_url(self.article.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_like_article(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.article.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.article.refresh_from_db()

        self.assertEqual(
            response.data,
            {
                "liked": True,
                "likes_count": 1,
            },
        )

        self.assertEqual(
            self.article.likes_count,
            1,
        )

        self.assertTrue(
            EditorialArticleLike.objects.filter(
                user=self.user,
                article=self.article,
            ).exists()
        )

        interaction = MusicFeedInteraction.objects.get(
            user=self.user,
            interaction_type=(
                MusicFeedInteraction.InteractionType.LIKE_EDITORIAL
            ),
            editorial_article=self.article,
        )

        self.assertEqual(
            interaction.editorial_article,
            self.article,
        )

        self.assertIsNone(interaction.song)
        self.assertIsNone(interaction.album)
        self.assertIsNone(interaction.artist)
        self.assertIsNone(interaction.community_post)

    def test_duplicate_like_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        first_response = self.client.post(
            self.get_url(self.article.pk)
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        second_response = self.client.post(
            self.get_url(self.article.pk)
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.article.refresh_from_db()

        self.assertEqual(
            self.article.likes_count,
            1,
        )

        self.assertEqual(
            EditorialArticleLike.objects.filter(
                article=self.article,
            ).count(),
            1,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.LIKE_EDITORIAL
                ),
                editorial_article=self.article,
            ).count(),
            1,
        )

    def test_multiple_users_can_like_same_article(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.article.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            self.get_url(self.article.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.article.refresh_from_db()

        self.assertEqual(
            self.article.likes_count,
            2,
        )

        self.assertEqual(
            EditorialArticleLike.objects.filter(
                article=self.article,
            ).count(),
            2,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                interaction_type=(
                    MusicFeedInteraction.InteractionType.LIKE_EDITORIAL
                ),
                editorial_article=self.article,
            ).count(),
            2,
        )

        self.assertTrue(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.LIKE_EDITORIAL
                ),
                editorial_article=self.article,
            ).exists()
        )

        self.assertTrue(
            MusicFeedInteraction.objects.filter(
                user=self.other_user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.LIKE_EDITORIAL
                ),
                editorial_article=self.article,
            ).exists()
        )

    def test_authenticated_user_can_unlike_article(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.article.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        response = self.client.delete(
            self.get_url(self.article.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.article.refresh_from_db()

        self.assertEqual(
            response.data,
            {
                "liked": False,
                "likes_count": 0,
            },
        )

        self.assertEqual(
            self.article.likes_count,
            0,
        )

        self.assertFalse(
            EditorialArticleLike.objects.filter(
                user=self.user,
                article=self.article,
            ).exists()
        )

        # Unlike does not erase historical behavior.
        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.LIKE_EDITORIAL
                ),
                editorial_article=self.article,
            ).count(),
            1,
        )

    def test_unlike_when_not_liked_is_idempotent(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            self.get_url(self.article.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.article.refresh_from_db()

        self.assertEqual(
            response.data,
            {
                "liked": False,
                "likes_count": 0,
            },
        )

        self.assertEqual(
            self.article.likes_count,
            0,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.LIKE_EDITORIAL
                ),
                editorial_article=self.article,
            ).count(),
            0,
        )

    def test_draft_article_returns_404(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.draft_article.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.draft_article.refresh_from_db()

        self.assertEqual(
            self.draft_article.likes_count,
            0,
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.LIKE_EDITORIAL
                ),
                editorial_article=self.draft_article,
            ).exists()
        )


# ============================================================
# COMMUNITY POST LIKE
# ============================================================

class CommunityPostLikeAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="post_like_user",
            email="post_like_user@example.com",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="post_like_other",
            email="post_like_other@example.com",
            password="testpass123",
        )

        self.post = CommunityPost.objects.create(
            user=self.user,
            content="This is a published community post.",
            status=CommunityPost.Status.PUBLISHED,
        )

        self.hidden_post = CommunityPost.objects.create(
            user=self.user,
            content="This is a hidden community post.",
            status=CommunityPost.Status.HIDDEN,
        )

    def get_url(self, post_id):
        return f"/api/v1/music/community/posts/{post_id}/like/"

    def test_anonymous_user_cannot_like_post(self):
        response = self.client.post(
            self.get_url(self.post.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_anonymous_user_cannot_unlike_post(self):
        response = self.client.delete(
            self.get_url(self.post.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_like_post(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.post.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            response.data,
            {
                "liked": True,
                "likes_count": 1,
            },
        )

        self.assertEqual(
            self.post.likes_count,
            1,
        )

        self.assertTrue(
            CommunityPostLike.objects.filter(
                user=self.user,
                post=self.post,
            ).exists()
        )

        interaction = MusicFeedInteraction.objects.get(
            user=self.user,
            interaction_type=(
                MusicFeedInteraction.InteractionType.LIKE_COMMUNITY_POST
            ),
            community_post=self.post,
        )

        self.assertEqual(
            interaction.community_post,
            self.post,
        )

        self.assertIsNone(interaction.song)
        self.assertIsNone(interaction.album)
        self.assertIsNone(interaction.artist)
        self.assertIsNone(interaction.editorial_article)

    def test_duplicate_like_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.post.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        response = self.client.post(
            self.get_url(self.post.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.likes_count,
            1,
        )

        self.assertEqual(
            CommunityPostLike.objects.filter(
                post=self.post,
            ).count(),
            1,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.LIKE_COMMUNITY_POST
                ),
                community_post=self.post,
            ).count(),
            1,
        )

    def test_multiple_users_can_like_same_post(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.post.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            self.get_url(self.post.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.likes_count,
            2,
        )

        self.assertEqual(
            CommunityPostLike.objects.filter(
                post=self.post,
            ).count(),
            2,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                interaction_type=(
                    MusicFeedInteraction.InteractionType.LIKE_COMMUNITY_POST
                ),
                community_post=self.post,
            ).count(),
            2,
        )

        self.assertTrue(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.LIKE_COMMUNITY_POST
                ),
                community_post=self.post,
            ).exists()
        )

        self.assertTrue(
            MusicFeedInteraction.objects.filter(
                user=self.other_user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.LIKE_COMMUNITY_POST
                ),
                community_post=self.post,
            ).exists()
        )

    def test_authenticated_user_can_unlike_post(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.post.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        response = self.client.delete(
            self.get_url(self.post.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            response.data,
            {
                "liked": False,
                "likes_count": 0,
            },
        )

        self.assertEqual(
            self.post.likes_count,
            0,
        )

        self.assertFalse(
            CommunityPostLike.objects.filter(
                user=self.user,
                post=self.post,
            ).exists()
        )

        # Unlike does not erase historical behavior.
        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.LIKE_COMMUNITY_POST
                ),
                community_post=self.post,
            ).count(),
            1,
        )

    def test_unlike_when_not_liked_is_idempotent(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            self.get_url(self.post.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            response.data,
            {
                "liked": False,
                "likes_count": 0,
            },
        )

        self.assertEqual(
            self.post.likes_count,
            0,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.LIKE_COMMUNITY_POST
                ),
                community_post=self.post,
            ).count(),
            0,
        )

    def test_hidden_post_returns_404(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.hidden_post.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.hidden_post.refresh_from_db()

        self.assertEqual(
            self.hidden_post.likes_count,
            0,
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.LIKE_COMMUNITY_POST
                ),
                community_post=self.hidden_post,
            ).exists()
        )


# ============================================================
# EDITORIAL COMMENT LIKE
# ============================================================

class EditorialCommentLikeAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="editorial_comment_user",
            email="editorial_comment_user@example.com",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="editorial_comment_other",
            email="editorial_comment_other@example.com",
            password="testpass123",
        )

        self.article = EditorialArticle.objects.create(
            title="Comment Article",
            slug="comment-article",
            content="Article used for comment tests.",
            author=self.user,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.comment = EditorialComment.objects.create(
            user=self.user,
            article=self.article,
            content="This is a top-level comment.",
            status=EditorialComment.Status.PUBLISHED,
        )

        self.reply = EditorialComment.objects.create(
            user=self.other_user,
            article=self.article,
            parent=self.comment,
            content="This is a reply.",
            status=EditorialComment.Status.PUBLISHED,
        )

        self.hidden_comment = EditorialComment.objects.create(
            user=self.user,
            article=self.article,
            content="This comment is hidden.",
            status=EditorialComment.Status.HIDDEN,
        )

    def get_url(self, comment_id):
        return f"/api/v1/music/editorial/comments/{comment_id}/like/"

    def test_anonymous_user_cannot_like_comment(self):
        response = self.client.post(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_anonymous_user_cannot_unlike_comment(self):
        response = self.client.delete(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_like_comment(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            response.data,
            {
                "liked": True,
                "likes_count": 1,
            },
        )

        self.assertEqual(
            self.comment.likes_count,
            1,
        )

        self.assertTrue(
            EditorialCommentLike.objects.filter(
                user=self.user,
                comment=self.comment,
            ).exists()
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
            ).exists()
        )

    def test_duplicate_like_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        response = self.client.post(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            self.comment.likes_count,
            1,
        )

        self.assertEqual(
            EditorialCommentLike.objects.filter(
                comment=self.comment,
            ).count(),
            1,
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
            ).exists()
        )

    def test_multiple_users_can_like_same_comment(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            self.comment.likes_count,
            2,
        )

        self.assertEqual(
            EditorialCommentLike.objects.filter(
                comment=self.comment,
            ).count(),
            2,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            0,
        )

    def test_authenticated_user_can_unlike_comment(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        response = self.client.delete(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            response.data,
            {
                "liked": False,
                "likes_count": 0,
            },
        )

        self.assertEqual(
            self.comment.likes_count,
            0,
        )

        self.assertFalse(
            EditorialCommentLike.objects.filter(
                user=self.user,
                comment=self.comment,
            ).exists()
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            0,
        )

    def test_unlike_when_not_liked_is_idempotent(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            response.data,
            {
                "liked": False,
                "likes_count": 0,
            },
        )

        self.assertEqual(
            self.comment.likes_count,
            0,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            0,
        )

    def test_reply_can_be_liked(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.reply.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.reply.refresh_from_db()

        self.assertEqual(
            response.data,
            {
                "liked": True,
                "likes_count": 1,
            },
        )

        self.assertEqual(
            self.reply.likes_count,
            1,
        )

        self.assertTrue(
            EditorialCommentLike.objects.filter(
                user=self.user,
                comment=self.reply,
            ).exists()
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
            ).exists()
        )

    def test_hidden_comment_returns_404(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.hidden_comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.hidden_comment.refresh_from_db()

        self.assertEqual(
            self.hidden_comment.likes_count,
            0,
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
            ).exists()
        )


# ============================================================
# COMMUNITY POST COMMENT LIKE
# ============================================================

class CommunityPostCommentLikeAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="community_comment_user",
            email="community_comment_user@example.com",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="community_comment_other",
            email="community_comment_other@example.com",
            password="testpass123",
        )

        self.post = CommunityPost.objects.create(
            user=self.user,
            content="Community post used for comment tests.",
            status=CommunityPost.Status.PUBLISHED,
        )

        self.comment = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="This is a top-level community comment.",
            status=CommunityPostComment.Status.PUBLISHED,
        )

        self.reply = CommunityPostComment.objects.create(
            user=self.other_user,
            post=self.post,
            parent=self.comment,
            content="This is a community reply.",
            status=CommunityPostComment.Status.PUBLISHED,
        )

        self.hidden_comment = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="This community comment is hidden.",
            status=CommunityPostComment.Status.HIDDEN,
        )

    def get_url(self, comment_id):
        return f"/api/v1/music/community/comments/{comment_id}/like/"

    def test_anonymous_user_cannot_like_comment(self):
        response = self.client.post(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_anonymous_user_cannot_unlike_comment(self):
        response = self.client.delete(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_like_comment(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            response.data,
            {
                "liked": True,
                "likes_count": 1,
            },
        )

        self.assertEqual(
            self.comment.likes_count,
            1,
        )

        self.assertTrue(
            CommunityPostCommentLike.objects.filter(
                user=self.user,
                comment=self.comment,
            ).exists()
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
            ).exists()
        )

    def test_duplicate_like_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        response = self.client.post(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            self.comment.likes_count,
            1,
        )

        self.assertEqual(
            CommunityPostCommentLike.objects.filter(
                comment=self.comment,
            ).count(),
            1,
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
            ).exists()
        )

    def test_multiple_users_can_like_same_comment(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            self.comment.likes_count,
            2,
        )

        self.assertEqual(
            CommunityPostCommentLike.objects.filter(
                comment=self.comment,
            ).count(),
            2,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            0,
        )

    def test_authenticated_user_can_unlike_comment(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        response = self.client.delete(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            response.data,
            {
                "liked": False,
                "likes_count": 0,
            },
        )

        self.assertEqual(
            self.comment.likes_count,
            0,
        )

        self.assertFalse(
            CommunityPostCommentLike.objects.filter(
                user=self.user,
                comment=self.comment,
            ).exists()
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            0,
        )

    def test_unlike_when_not_liked_is_idempotent(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            self.get_url(self.comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            response.data,
            {
                "liked": False,
                "likes_count": 0,
            },
        )

        self.assertEqual(
            self.comment.likes_count,
            0,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.count(),
            0,
        )

    def test_reply_can_be_liked(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.reply.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.reply.refresh_from_db()

        self.assertEqual(
            response.data,
            {
                "liked": True,
                "likes_count": 1,
            },
        )

        self.assertEqual(
            self.reply.likes_count,
            1,
        )

        self.assertTrue(
            CommunityPostCommentLike.objects.filter(
                user=self.user,
                comment=self.reply,
            ).exists()
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
            ).exists()
        )

    def test_hidden_comment_returns_404(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.get_url(self.hidden_comment.pk)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.hidden_comment.refresh_from_db()

        self.assertEqual(
            self.hidden_comment.likes_count,
            0,
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
            ).exists()
        )