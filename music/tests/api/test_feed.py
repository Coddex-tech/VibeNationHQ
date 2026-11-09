from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from music.models import CommunityPost, EditorialArticle
from music.services.feed import MusicFeedService


User = get_user_model()


class MusicFeedAPIViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="feed_api_user",
            email="feed_api_user@example.com",
            password="password",
        )

    @classmethod
    def create_community_post(
        cls,
        *,
        user=None,
        content="Feed test community post",
        slug=None,
    ):
        if slug is None:
            slug = f"feed-post-{CommunityPost.objects.count() + 1}"

        return CommunityPost.objects.create(
            user=user or cls.user,
            content=content,
            slug=slug,
        )

    @classmethod
    def create_editorial_article(
        cls,
        *,
        title="Feed test editorial article",
        slug=None,
        published_at=None,
    ):
        if slug is None:
            slug = (
                f"feed-editorial-"
                f"{EditorialArticle.objects.count() + 1}"
            )

        return EditorialArticle.objects.create(
            title=title,
            slug=slug,
            excerpt="Editorial feed test excerpt.",
            content="Editorial feed test content.",
            author=cls.user,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=(
                published_at
                if published_at is not None
                else timezone.now()
            ),
        )

    @staticmethod
    def get_url():
        return reverse("music_api:music-feed")

    def setUp(self):
        self.client = APIClient()

    # ========================================================
    # BASIC RESPONSE
    # ========================================================

    def test_anonymous_request_returns_feed(self):
        post = self.create_community_post(
            content="Anonymous feed post",
        )

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 200)

        self.assertIn("results", response.data)
        self.assertIn("has_more", response.data)
        self.assertIn("next_cursor", response.data)

        returned_ids = [
            item["content"]["id"]
            for item in response.data["results"]
            if item["content_type"] == "community_post"
        ]

        self.assertIn(post.id, returned_ids)

    def test_authenticated_request_returns_feed(self):
        post = self.create_community_post(
            content="Authenticated feed post",
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 200)

        returned_ids = [
            item["content"]["id"]
            for item in response.data["results"]
            if item["content_type"] == "community_post"
        ]

        self.assertIn(post.id, returned_ids)

    # ========================================================
    # FEED CONTENT TYPES
    # ========================================================

    def test_feed_contains_only_supported_content_types(self):
        self.create_community_post()

        self.create_editorial_article()

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 200)

        content_types = {
            item["content_type"]
            for item in response.data["results"]
        }

        self.assertTrue(content_types)

        self.assertTrue(
            content_types.issubset(
                {
                    "community_post",
                    "editorial",
                }
            )
        )

    def test_community_post_has_expected_response_shape(self):
        self.create_community_post(
            content="Community post response shape",
        )

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 200)

        post_items = [
            item
            for item in response.data["results"]
            if item["content_type"] == "community_post"
        ]

        self.assertTrue(post_items)

        item = post_items[0]

        self.assertIn("content_type", item)
        self.assertIn("source", item)
        self.assertIn("content", item)

        self.assertEqual(
            item["content_type"],
            "community_post",
        )

        self.assertIsInstance(item["source"], str)
        self.assertIsInstance(item["content"], dict)

        self.assertIn("id", item["content"])
        self.assertIn("content", item["content"])

    def test_editorial_article_has_expected_response_shape(self):
        article = self.create_editorial_article(
            title="Editorial response shape",
        )

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 200)

        editorial_items = [
            item
            for item in response.data["results"]
            if item["content_type"] == "editorial"
        ]

        self.assertTrue(editorial_items)

        item = next(
            (
                item
                for item in editorial_items
                if item["content"]["id"] == article.id
            ),
            None,
        )

        self.assertIsNotNone(item)

        self.assertIn("content_type", item)
        self.assertIn("source", item)
        self.assertIn("content", item)

        self.assertEqual(
            item["content_type"],
            "editorial",
        )

        self.assertIsInstance(item["source"], str)
        self.assertIsInstance(item["content"], dict)

        self.assertEqual(
            item["content"]["id"],
            article.id,
        )

        self.assertEqual(
            item["content"]["title"],
            article.title,
        )

    # ========================================================
    # EDITORIAL ELIGIBILITY
    # ========================================================

    def test_editorial_without_music_relationships_appears_in_feed(self):
        article = self.create_editorial_article(
            title="Editorial without music relationships",
        )

        self.assertIsNone(article.song)
        self.assertIsNone(article.artist)
        self.assertIsNone(article.album)

        self.assertEqual(article.genres.count(), 0)

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 200)

        returned_editorial_ids = [
            item["content"]["id"]
            for item in response.data["results"]
            if item["content_type"] == "editorial"
        ]

        self.assertIn(
            article.id,
            returned_editorial_ids,
        )

    def test_unpublished_editorial_does_not_appear_in_feed(self):
        article = self.create_editorial_article(
            title="Draft editorial article",
            slug="draft-editorial-article",
        )

        article.status = EditorialArticle.Status.DRAFT
        article.published_at = None
        article.save(
            update_fields=[
                "status",
                "published_at",
            ]
        )

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 200)

        returned_editorial_ids = [
            item["content"]["id"]
            for item in response.data["results"]
            if item["content_type"] == "editorial"
        ]

        self.assertNotIn(
            article.id,
            returned_editorial_ids,
        )

    # ========================================================
    # LIMIT
    # ========================================================

    def test_limit_parameter_is_respected(self):
        for index in range(10):
            self.create_community_post(
                content=f"Limit post {index}",
                slug=f"limit-post-{index}",
            )

        for index in range(3):
            self.create_editorial_article(
                title=f"Limit editorial {index}",
                slug=f"limit-editorial-{index}",
            )

        response = self.client.get(
            self.get_url(),
            {
                "limit": 3,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertLessEqual(
            len(response.data["results"]),
            3,
        )

    def test_invalid_limit_returns_bad_request(self):
        response = self.client.get(
            self.get_url(),
            {
                "limit": "abc",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.data)

    def test_limit_above_maximum_is_capped(self):
        for index in range(
            MusicFeedService.MAX_LIMIT + 10
        ):
            self.create_community_post(
                content=f"Maximum limit post {index}",
                slug=f"maximum-limit-post-{index}",
            )

        response = self.client.get(
            self.get_url(),
            {
                "limit": 1000,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertLessEqual(
            len(response.data["results"]),
            MusicFeedService.MAX_LIMIT,
        )

    # ========================================================
    # MIXING
    # ========================================================

    def test_feed_uses_ten_to_one_mixing_ratio(self):
        for index in range(12):
            self.create_community_post(
                content=f"Mixing post {index}",
                slug=f"mixing-post-{index}",
            )

        for index in range(2):
            self.create_editorial_article(
                title=f"Mixing editorial {index}",
                slug=f"mixing-editorial-{index}",
            )

        response = self.client.get(
            self.get_url(),
            {
                "limit": 12,
            },
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        self.assertEqual(len(results), 12)

        content_types = [
            item["content_type"]
            for item in results
        ]

        self.assertEqual(
            content_types.count("community_post"),
            11,
        )

        self.assertEqual(
            content_types.count("editorial"),
            1,
        )

        self.assertEqual(
            content_types[10],
            "editorial",
        )

    def test_editorials_do_not_appear_consecutively_while_community_posts_remain(self):
        for index in range(25):
            self.create_community_post(
                content=f"Diversity post {index}",
                slug=f"diversity-post-{index}",
            )

        for index in range(5):
            self.create_editorial_article(
                title=f"Diversity editorial {index}",
                slug=f"diversity-editorial-{index}",
            )

        response = self.client.get(
            self.get_url(),
            {
                "limit": 20,
            },
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        for index in range(len(results) - 1):
            current_type = results[index]["content_type"]
            next_type = results[index + 1]["content_type"]

            if current_type == "editorial":
                self.assertNotEqual(
                    next_type,
                    "editorial",
                )

    def test_remaining_editorials_fill_feed_when_community_pool_is_exhausted(self):
        self.create_community_post(
            content="Only community post",
            slug="only-community-post",
        )

        for index in range(4):
            self.create_editorial_article(
                title=f"Remaining editorial {index}",
                slug=f"remaining-editorial-{index}",
            )

        response = self.client.get(
            self.get_url(),
            {
                "limit": 5,
            },
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        self.assertEqual(len(results), 5)

        self.assertEqual(
            sum(
                item["content_type"] == "community_post"
                for item in results
            ),
            1,
        )

        self.assertEqual(
            sum(
                item["content_type"] == "editorial"
                for item in results
            ),
            4,
        )

    # ========================================================
    # PINNED COMMUNITY POST
    # ========================================================

    def test_new_post_id_is_pinned_first(self):
        for index in range(5):
            self.create_community_post(
                content=f"Existing post {index}",
                slug=f"existing-post-{index}",
            )

        new_post = self.create_community_post(
            content="Newly published post",
            slug="newly-published-post",
        )

        response = self.client.get(
            self.get_url(),
            {
                "new_post_id": new_post.id,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(response.data["results"])

        first_item = response.data["results"][0]

        self.assertEqual(
            first_item["content_type"],
            "community_post",
        )

        self.assertEqual(
            first_item["content"]["id"],
            new_post.id,
        )

    def test_new_post_id_is_not_reapplied_on_cursor_request(self):
        for index in range(5):
            self.create_community_post(
                content=f"Cursor pin post {index}",
                slug=f"cursor-pin-post-{index}",
            )

        new_post = self.create_community_post(
            content="Pinned cursor post",
            slug="pinned-cursor-post",
        )

        first_response = self.client.get(
            self.get_url(),
            {
                "limit": 1,
                "new_post_id": new_post.id,
            },
        )

        self.assertEqual(first_response.status_code, 200)

        self.assertEqual(
            first_response.data["results"][0]["content"]["id"],
            new_post.id,
        )

        cursor = first_response.data["next_cursor"]

        self.assertIsNotNone(cursor)

        second_response = self.client.get(
            self.get_url(),
            {
                "limit": 1,
                "cursor": cursor,
                "new_post_id": new_post.id,
            },
        )

        self.assertEqual(second_response.status_code, 200)

        second_item = second_response.data["results"][0]

        self.assertNotEqual(
            (
                second_item["content_type"],
                second_item["content"]["id"],
            ),
            (
                "community_post",
                new_post.id,
            ),
        )

    def test_invalid_new_post_id_returns_bad_request(self):
        response = self.client.get(
            self.get_url(),
            {
                "new_post_id": "invalid",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.data)

    def test_non_positive_new_post_id_returns_bad_request(self):
        for invalid_id in ("0", "-1"):
            response = self.client.get(
                self.get_url(),
                {
                    "new_post_id": invalid_id,
                },
            )

            self.assertEqual(response.status_code, 400)

    # ========================================================
    # CURSOR PAGINATION
    # ========================================================

    def test_first_page_returns_cursor_when_more_items_exist(self):
        for index in range(5):
            self.create_community_post(
                content=f"Cursor post {index}",
                slug=f"cursor-post-{index}",
            )

        response = self.client.get(
            self.get_url(),
            {
                "limit": 1,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertTrue(response.data["has_more"])

        self.assertIsNotNone(
            response.data["next_cursor"],
        )

    def test_next_cursor_returns_next_page(self):
        for index in range(5):
            self.create_community_post(
                content=f"Next page post {index}",
                slug=f"next-page-post-{index}",
            )

        first_response = self.client.get(
            self.get_url(),
            {
                "limit": 1,
            },
        )

        self.assertEqual(first_response.status_code, 200)

        first_cursor = first_response.data["next_cursor"]

        self.assertIsNotNone(first_cursor)

        first_item = first_response.data["results"][0]

        second_response = self.client.get(
            self.get_url(),
            {
                "limit": 1,
                "cursor": first_cursor,
            },
        )

        self.assertEqual(second_response.status_code, 200)

        self.assertEqual(
            len(second_response.data["results"]),
            1,
        )

        second_item = second_response.data["results"][0]

        self.assertNotEqual(
            (
                first_item["content_type"],
                first_item["content"]["id"],
            ),
            (
                second_item["content_type"],
                second_item["content"]["id"],
            ),
        )

    def test_cursor_keeps_snapshot_ordering(self):
        for index in range(15):
            self.create_community_post(
                content=f"Stable cursor post {index}",
                slug=f"stable-cursor-post-{index}",
            )

        for index in range(3):
            self.create_editorial_article(
                title=f"Stable cursor editorial {index}",
                slug=f"stable-cursor-editorial-{index}",
            )

        first_response = self.client.get(
            self.get_url(),
            {
                "limit": 5,
            },
        )

        self.assertEqual(first_response.status_code, 200)

        first_cursor = first_response.data["next_cursor"]

        self.assertIsNotNone(first_cursor)

        second_response = self.client.get(
            self.get_url(),
            {
                "limit": 5,
                "cursor": first_cursor,
            },
        )

        self.assertEqual(second_response.status_code, 200)

        first_page_ids = {
            (
                item["content_type"],
                item["content"]["id"],
            )
            for item in first_response.data["results"]
        }

        second_page_ids = {
            (
                item["content_type"],
                item["content"]["id"],
            )
            for item in second_response.data["results"]
        }

        self.assertTrue(
            first_page_ids.isdisjoint(second_page_ids)
        )

    def test_invalid_cursor_returns_bad_request(self):
        response = self.client.get(
            self.get_url(),
            {
                "cursor": "not-a-valid-feed-cursor",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.data)

    # ========================================================
    # EMPTY FEED
    # ========================================================

    def test_empty_feed_returns_valid_response(self):
        CommunityPost.objects.all().delete()
        EditorialArticle.objects.all().delete()

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["results"],
            [],
        )

        self.assertFalse(
            response.data["has_more"],
        )

        self.assertIsNone(
            response.data["next_cursor"],
        )