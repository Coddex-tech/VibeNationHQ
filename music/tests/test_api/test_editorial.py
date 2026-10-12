from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from music.models import (
    Artist,
    EditorialArticle,
    EditorialArticleLike,
    EditorialArticleReport,
    EditorialComment,
    EditorialCommentLike,
    EditorialCommentReport,
    Song,
)


User = get_user_model()


class EditorialArticleListAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="editor",
            email="editor@example.com",
            password="testpassword",
        )

        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.song = Song.objects.create(
            title="Test Song",
            slug="test-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.song.artists.add(cls.artist)

        cls.published_article = EditorialArticle.objects.create(
            title="Published Article",
            slug="published-article",
            excerpt="A published editorial article.",
            content="This is the full editorial article content.",
            author=cls.user,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now(),
            is_featured=True,
        )

        cls.published_article.song = cls.song
        cls.published_article.save(update_fields=["song"])

        cls.draft_article = EditorialArticle.objects.create(
            title="Draft Article",
            slug="draft-article",
            excerpt="A draft editorial article.",
            content="This draft should not be publicly visible.",
            author=cls.user,
            status=EditorialArticle.Status.DRAFT,
        )

    def test_anonymous_user_can_list_published_articles(self):
        url = reverse("music_api:editorial-article-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_list_only_returns_published_articles(self):
        url = reverse("music_api:editorial-article-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        returned_ids = {
            article["id"]
            for article in results
        }

        self.assertIn(
            self.published_article.id,
            returned_ids,
        )

        self.assertNotIn(
            self.draft_article.id,
            returned_ids,
        )

    def test_article_card_contains_expected_fields(self):
        url = reverse("music_api:editorial-article-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        article = response.data["results"][0]

        self.assertIn("id", article)
        self.assertIn("title", article)
        self.assertIn("slug", article)
        self.assertIn("excerpt", article)
        self.assertIn("author", article)
        self.assertIn("song", article)
        self.assertIn("artist", article)
        self.assertIn("album", article)
        self.assertIn("status", article)
        self.assertIn("published_at", article)
        self.assertIn("is_featured", article)
        self.assertIn("views_count", article)
        self.assertIn("likes_count", article)
        self.assertIn("comments_count", article)
        self.assertIn("liked", article)

    def test_anonymous_user_sees_liked_as_false(self):
        url = reverse("music_api:editorial-article-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        article = response.data["results"][0]

        self.assertFalse(
            article["liked"],
        )

    def test_authenticated_user_sees_liked_as_false_when_not_liked(self):
        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse("music_api:editorial-article-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        article = response.data["results"][0]

        self.assertFalse(
            article["liked"],
        )

    def test_authenticated_user_sees_liked_as_true_when_liked(self):
        EditorialArticleLike.objects.create(
            user=self.user,
            article=self.published_article,
        )

        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse("music_api:editorial-article-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        article = response.data["results"][0]

        self.assertTrue(
            article["liked"],
        )


class EditorialArticleDetailAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="editor",
            email="editor-detail@example.com",
            password="testpassword",
        )

        cls.published_article = EditorialArticle.objects.create(
            title="Published Article",
            slug="published-article",
            excerpt="Article excerpt.",
            content="Full article content.",
            author=cls.user,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.draft_article = EditorialArticle.objects.create(
            title="Draft Article",
            slug="draft-article",
            excerpt="Draft excerpt.",
            content="Draft article content.",
            author=cls.user,
            status=EditorialArticle.Status.DRAFT,
        )

    def test_anonymous_user_can_retrieve_published_article(self):
        url = reverse(
            "music_api:editorial-article-detail",
            kwargs={
                "slug": self.published_article.slug,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.published_article.id,
        )

        self.assertEqual(
            response.data["title"],
            self.published_article.title,
        )

    def test_article_detail_returns_full_content(self):
        url = reverse(
            "music_api:editorial-article-detail",
            kwargs={
                "slug": self.published_article.slug,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["content"],
            self.published_article.content,
        )

    def test_article_detail_contains_liked_field(self):
        url = reverse(
            "music_api:editorial-article-detail",
            kwargs={
                "slug": self.published_article.slug,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "liked",
            response.data,
        )

    def test_anonymous_user_sees_liked_as_false(self):
        url = reverse(
            "music_api:editorial-article-detail",
            kwargs={
                "slug": self.published_article.slug,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            response.data["liked"],
        )

    def test_authenticated_user_sees_liked_as_false_when_not_liked(self):
        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-article-detail",
            kwargs={
                "slug": self.published_article.slug,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            response.data["liked"],
        )

    def test_authenticated_user_sees_liked_as_true_when_liked(self):
        EditorialArticleLike.objects.create(
            user=self.user,
            article=self.published_article,
        )

        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-article-detail",
            kwargs={
                "slug": self.published_article.slug,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            response.data["liked"],
        )

    def test_draft_article_is_not_publicly_accessible(self):
        url = reverse(
            "music_api:editorial-article-detail",
            kwargs={
                "slug": self.draft_article.slug,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )


class EditorialArticleLikeAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="article-liker",
            email="article-liker@example.com",
            password="testpassword",
        )

        cls.author = User.objects.create_user(
            username="editor",
            email="editor-like@example.com",
            password="testpassword",
        )

        cls.article = EditorialArticle.objects.create(
            title="Published Article",
            slug="published-article",
            content="Article content.",
            author=cls.author,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now(),
        )

    def test_authenticated_user_can_like_editorial_article(self):
        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-article-like",
            kwargs={
                "pk": self.article.id,
            },
        )

        self.assertEqual(
            url,
            f"/api/v1/music/editorial/{self.article.id}/like/",
        )

        response = self.client.post(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            response.data["liked"],
        )

        self.article.refresh_from_db()

        self.assertEqual(
            self.article.likes_count,
            1,
        )

        self.assertTrue(
            EditorialArticleLike.objects.filter(
                user=self.user,
                article=self.article,
            ).exists(),
        )

    def test_authenticated_user_can_unlike_editorial_article(self):
        EditorialArticleLike.objects.create(
            user=self.user,
            article=self.article,
        )

        self.article.likes_count = 1
        self.article.save(
            update_fields=["likes_count"],
        )

        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-article-like",
            kwargs={
                "pk": self.article.id,
            },
        )

        self.assertEqual(
            url,
            f"/api/v1/music/editorial/{self.article.id}/like/",
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            response.data["liked"],
        )

        self.article.refresh_from_db()

        self.assertEqual(
            self.article.likes_count,
            0,
        )

        self.assertFalse(
            EditorialArticleLike.objects.filter(
                user=self.user,
                article=self.article,
            ).exists(),
        )

    def test_anonymous_user_cannot_like_editorial_article(self):
        url = reverse(
            "music_api:editorial-article-like",
            kwargs={
                "pk": self.article.id,
            },
        )

        self.assertEqual(
            url,
            f"/api/v1/music/editorial/{self.article.id}/like/",
        )

        response = self.client.post(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


class EditorialCommentListCreateAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="commenter",
            email="commenter@example.com",
            password="testpassword",
        )

        cls.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="testpassword",
        )

        cls.author = User.objects.create_user(
            username="editor",
            email="editor-comments@example.com",
            password="testpassword",
        )

        cls.published_article = EditorialArticle.objects.create(
            title="Published Article",
            slug="published-article",
            excerpt="Article excerpt.",
            content="Full article content.",
            author=cls.author,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.draft_article = EditorialArticle.objects.create(
            title="Draft Article",
            slug="draft-article",
            excerpt="Draft excerpt.",
            content="Draft content.",
            author=cls.author,
            status=EditorialArticle.Status.DRAFT,
        )

        cls.comment = EditorialComment.objects.create(
            user=cls.other_user,
            article=cls.published_article,
            content="Existing comment.",
            status=EditorialComment.Status.PUBLISHED,
        )

    def test_anonymous_user_can_list_comments(self):
        url = reverse(
            "music_api:editorial-comment-list",
            kwargs={
                "article_id": self.published_article.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_anonymous_user_cannot_create_comment(self):
        url = reverse(
            "music_api:editorial-comment-list",
            kwargs={
                "article_id": self.published_article.id,
            },
        )

        response = self.client.post(
            url,
            {
                "content": "Anonymous comment.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_authenticated_user_can_create_comment(self):
        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-comment-list",
            kwargs={
                "article_id": self.published_article.id,
            },
        )

        response = self.client.post(
            url,
            {
                "content": "This is my comment.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["content"],
            "This is my comment.",
        )

        self.assertEqual(
            response.data["user"]["id"],
            self.user.id,
        )

        self.assertIn(
            "liked",
            response.data,
        )

        self.assertFalse(
            response.data["liked"],
        )

        self.assertEqual(
            EditorialComment.objects.filter(
                article=self.published_article,
                user=self.user,
            ).count(),
            1,
        )

        self.published_article.refresh_from_db()

        self.assertEqual(
            self.published_article.comments_count,
            1,
        )

    def test_article_is_taken_from_url_not_request_body(self):
        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-comment-list",
            kwargs={
                "article_id": self.published_article.id,
            },
        )

        response = self.client.post(
            url,
            {
                "article": 999999,
                "content": "The URL should determine the article.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        comment = EditorialComment.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(
            comment.article_id,
            self.published_article.id,
        )

    def test_empty_comment_is_rejected(self):
        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-comment-list",
            kwargs={
                "article_id": self.published_article.id,
            },
        )

        response = self.client.post(
            url,
            {
                "content": "   ",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_comment_on_draft_article_is_not_allowed(self):
        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-comment-list",
            kwargs={
                "article_id": self.draft_article.id,
            },
        )

        response = self.client.post(
            url,
            {
                "content": "Comment on draft.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_only_top_level_comments_are_returned_by_default(self):
        top_level_comment = EditorialComment.objects.create(
            user=self.user,
            article=self.published_article,
            content="Top-level comment.",
            status=EditorialComment.Status.PUBLISHED,
        )

        EditorialComment.objects.create(
            user=self.other_user,
            article=self.published_article,
            parent=top_level_comment,
            content="Reply to top-level comment.",
            status=EditorialComment.Status.PUBLISHED,
        )

        url = reverse(
            "music_api:editorial-comment-list",
            kwargs={
                "article_id": self.published_article.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            comment["id"]
            for comment in response.data["results"]
        }

        self.assertIn(
            self.comment.id,
            returned_ids,
        )

        self.assertIn(
            top_level_comment.id,
            returned_ids,
        )

    def test_comments_can_be_filtered_by_parent(self):
        parent = EditorialComment.objects.create(
            user=self.user,
            article=self.published_article,
            content="Parent comment.",
            status=EditorialComment.Status.PUBLISHED,
        )

        reply = EditorialComment.objects.create(
            user=self.other_user,
            article=self.published_article,
            parent=parent,
            content="Reply comment.",
            status=EditorialComment.Status.PUBLISHED,
        )

        url = reverse(
            "music_api:editorial-comment-list",
            kwargs={
                "article_id": self.published_article.id,
            },
        )

        response = self.client.get(
            url,
            {
                "parent": parent.id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            comment["id"]
            for comment in response.data["results"]
        }

        self.assertIn(
            reply.id,
            returned_ids,
        )

        self.assertNotIn(
            parent.id,
            returned_ids,
        )

    def test_anonymous_user_sees_comment_liked_as_false(self):
        url = reverse(
            "music_api:editorial-comment-list",
            kwargs={
                "article_id": self.published_article.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        comment = next(
            item
            for item in response.data["results"]
            if item["id"] == self.comment.id
        )

        self.assertIn(
            "liked",
            comment,
        )

        self.assertFalse(
            comment["liked"],
        )

    def test_authenticated_user_sees_comment_liked_as_false_when_not_liked(
        self,
    ):
        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-comment-list",
            kwargs={
                "article_id": self.published_article.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        comment = next(
            item
            for item in response.data["results"]
            if item["id"] == self.comment.id
        )

        self.assertFalse(
            comment["liked"],
        )

    def test_authenticated_user_sees_comment_liked_as_true_when_liked(
        self,
    ):
        EditorialCommentLike.objects.create(
            user=self.user,
            comment=self.comment,
        )

        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-comment-list",
            kwargs={
                "article_id": self.published_article.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        comment = next(
            item
            for item in response.data["results"]
            if item["id"] == self.comment.id
        )

        self.assertTrue(
            comment["liked"],
        )


class EditorialCommentReplyTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="commenter",
            email="commenter-reply@example.com",
            password="testpassword",
        )

        cls.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser-reply@example.com",
            password="testpassword",
        )

        cls.author = User.objects.create_user(
            username="editor",
            email="editor-reply@example.com",
            password="testpassword",
        )

        cls.article = EditorialArticle.objects.create(
            title="Published Article",
            slug="published-article",
            content="Article content.",
            author=cls.author,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.parent_comment = EditorialComment.objects.create(
            user=cls.other_user,
            article=cls.article,
            content="Parent comment.",
            status=EditorialComment.Status.PUBLISHED,
        )

    def test_authenticated_user_can_reply_to_comment(self):
        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-comment-list",
            kwargs={
                "article_id": self.article.id,
            },
        )

        response = self.client.post(
            url,
            {
                "parent": self.parent_comment.id,
                "content": "This is my reply.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        reply = EditorialComment.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(
            reply.parent_id,
            self.parent_comment.id,
        )

        self.assertIn(
            "liked",
            response.data,
        )

        self.assertFalse(
            response.data["liked"],
        )

        self.parent_comment.refresh_from_db()
        self.article.refresh_from_db()

        self.assertEqual(
            self.parent_comment.replies_count,
            1,
        )

        self.assertEqual(
            self.article.comments_count,
            1,
        )

    def test_reply_to_comment_from_another_article_is_rejected(self):
        other_article = EditorialArticle.objects.create(
            title="Another Article",
            slug="another-article",
            content="Another article.",
            author=self.author,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-comment-list",
            kwargs={
                "article_id": other_article.id,
            },
        )

        response = self.client.post(
            url,
            {
                "parent": self.parent_comment.id,
                "content": "Invalid cross-article reply.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_reply_to_removed_comment_is_rejected(self):
        self.parent_comment.status = (
            EditorialComment.Status.REMOVED
        )
        self.parent_comment.save(
            update_fields=["status"],
        )

        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-comment-list",
            kwargs={
                "article_id": self.article.id,
            },
        )

        response = self.client.post(
            url,
            {
                "parent": self.parent_comment.id,
                "content": "Reply to removed comment.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


class EditorialCommentDetailAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="commentowner",
            email="commentowner@example.com",
            password="testpassword",
        )

        cls.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser-detail@example.com",
            password="testpassword",
        )

        cls.author = User.objects.create_user(
            username="editor",
            email="editor-detail-comment@example.com",
            password="testpassword",
        )

        cls.article = EditorialArticle.objects.create(
            title="Published Article",
            slug="published-article",
            content="Article content.",
            author=cls.author,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.comment = EditorialComment.objects.create(
            user=cls.user,
            article=cls.article,
            content="Original comment.",
            status=EditorialComment.Status.PUBLISHED,
        )

    def test_anonymous_user_can_retrieve_comment(self):
        url = reverse(
            "music_api:editorial-comment-detail",
            kwargs={
                "pk": self.comment.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.comment.id,
        )

    def test_comment_detail_contains_liked_field(self):
        url = reverse(
            "music_api:editorial-comment-detail",
            kwargs={
                "pk": self.comment.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "liked",
            response.data,
        )

    def test_anonymous_user_sees_comment_liked_as_false(self):
        url = reverse(
            "music_api:editorial-comment-detail",
            kwargs={
                "pk": self.comment.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            response.data["liked"],
        )

    def test_authenticated_user_sees_comment_liked_as_false_when_not_liked(
        self,
    ):
        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-comment-detail",
            kwargs={
                "pk": self.comment.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            response.data["liked"],
        )

    def test_authenticated_user_sees_comment_liked_as_true_when_liked(
        self,
    ):
        EditorialCommentLike.objects.create(
            user=self.user,
            comment=self.comment,
        )

        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-comment-detail",
            kwargs={
                "pk": self.comment.id,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            response.data["liked"],
        )

    def test_comment_owner_can_update_comment(self):
        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-comment-detail",
            kwargs={
                "pk": self.comment.id,
            },
        )

        response = self.client.patch(
            url,
            {
                "content": "Updated comment.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            self.comment.content,
            "Updated comment.",
        )

        self.assertTrue(
            self.comment.is_edited,
        )

    def test_non_owner_cannot_update_comment(self):
        self.client.force_authenticate(
            user=self.other_user,
        )

        url = reverse(
            "music_api:editorial-comment-detail",
            kwargs={
                "pk": self.comment.id,
            },
        )

        response = self.client.patch(
            url,
            {
                "content": "Unauthorized edit.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_anonymous_user_cannot_update_comment(self):
        url = reverse(
            "music_api:editorial-comment-detail",
            kwargs={
                "pk": self.comment.id,
            },
        )

        response = self.client.patch(
            url,
            {
                "content": "Anonymous edit.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_comment_owner_can_delete_comment(self):
        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-comment-detail",
            kwargs={
                "pk": self.comment.id,
            },
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            EditorialComment.objects.filter(
                pk=self.comment.id,
            ).exists(),
        )

        self.article.refresh_from_db()

        self.assertEqual(
            self.article.comments_count,
            0,
        )

    def test_non_owner_cannot_delete_comment(self):
        self.client.force_authenticate(
            user=self.other_user,
        )

        url = reverse(
            "music_api:editorial-comment-detail",
            kwargs={
                "pk": self.comment.id,
            },
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


class EditorialArticleReportAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="reporter",
            email="reporter@example.com",
            password="testpassword",
        )

        cls.author = User.objects.create_user(
            username="editor",
            email="editor-report@example.com",
            password="testpassword",
        )

        cls.article = EditorialArticle.objects.create(
            title="Published Article",
            slug="published-article",
            content="Article content.",
            author=cls.author,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now(),
        )

    def test_anonymous_user_cannot_report_article(self):
        url = reverse(
            "music_api:editorial-article-report",
            kwargs={
                "pk": self.article.id,
            },
        )

        response = self.client.post(
            url,
            {
                "reason": EditorialArticleReport.Reason.SPAM,
                "details": "Spam content.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_authenticated_user_can_report_article(self):
        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-article-report",
            kwargs={
                "pk": self.article.id,
            },
        )

        self.assertEqual(
            url,
            f"/api/v1/music/editorial/{self.article.id}/report/",
        )

        response = self.client.post(
            url,
            {
                "reason": EditorialArticleReport.Reason.SPAM,
                "details": "This appears to be spam.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            EditorialArticleReport.objects.filter(
                user=self.user,
                article=self.article,
            ).count(),
            1,
        )

    def test_user_cannot_report_same_article_twice(self):
        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-article-report",
            kwargs={
                "pk": self.article.id,
            },
        )

        payload = {
            "reason": EditorialArticleReport.Reason.SPAM,
            "details": "Spam content.",
        }

        first_response = self.client.post(
            url,
            payload,
            format="json",
        )

        second_response = self.client.post(
            url,
            payload,
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            EditorialArticleReport.objects.filter(
                user=self.user,
                article=self.article,
            ).count(),
            1,
        )


class EditorialCommentReportAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="reporter",
            email="comment-reporter@example.com",
            password="testpassword",
        )

        cls.commenter = User.objects.create_user(
            username="commenter",
            email="commenter-report@example.com",
            password="testpassword",
        )

        cls.author = User.objects.create_user(
            username="editor",
            email="editor-comment-report@example.com",
            password="testpassword",
        )

        cls.article = EditorialArticle.objects.create(
            title="Published Article",
            slug="published-article",
            content="Article content.",
            author=cls.author,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.comment = EditorialComment.objects.create(
            user=cls.commenter,
            article=cls.article,
            content="Comment to report.",
            status=EditorialComment.Status.PUBLISHED,
        )

    def test_anonymous_user_cannot_report_comment(self):
        url = reverse(
            "music_api:editorial-comment-report",
            kwargs={
                "pk": self.comment.id,
            },
        )

        response = self.client.post(
            url,
            {
                "reason": EditorialCommentReport.Reason.SPAM,
                "details": "Spam comment.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_authenticated_user_can_report_comment(self):
        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-comment-report",
            kwargs={
                "pk": self.comment.id,
            },
        )

        response = self.client.post(
            url,
            {
                "reason": EditorialCommentReport.Reason.SPAM,
                "details": "This is spam.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            EditorialCommentReport.objects.filter(
                user=self.user,
                comment=self.comment,
            ).count(),
            1,
        )

    def test_user_cannot_report_same_comment_twice(self):
        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-comment-report",
            kwargs={
                "pk": self.comment.id,
            },
        )

        payload = {
            "reason": EditorialCommentReport.Reason.HARASSMENT,
            "details": "Harassing comment.",
        }

        first_response = self.client.post(
            url,
            payload,
            format="json",
        )

        second_response = self.client.post(
            url,
            payload,
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            EditorialCommentReport.objects.filter(
                user=self.user,
                comment=self.comment,
            ).count(),
            1,
        )

    def test_removed_comment_cannot_be_reported(self):
        self.comment.status = (
            EditorialComment.Status.REMOVED
        )
        self.comment.save(
            update_fields=["status"],
        )

        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:editorial-comment-report",
            kwargs={
                "pk": self.comment.id,
            },
        )

        response = self.client.post(
            url,
            {
                "reason": EditorialCommentReport.Reason.SPAM,
                "details": "Spam.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )