from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from music.models import Artist, Song
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

        cls.artist = Artist.objects.create(
            name="Feed API Artist",
            slug="feed-api-artist",
            is_active=True,
        )

    @classmethod
    def create_song(
        cls,
        *,
        title,
        slug,
        published_at=None,
    ):
        song = Song.objects.create(
            title=title,
            slug=slug,
            status=Song.Status.PUBLISHED,
            published_at=(
                published_at
                if published_at is not None
                else timezone.now()
            ),
        )

        song.artists.add(
            cls.artist,
        )

        return song

    @staticmethod
    def get_url():
        return reverse(
            "music_api:music-feed",
        )

    def setUp(self):
        self.client = APIClient()

    # ========================================================
    # BASIC RESPONSE
    # ========================================================

    def test_anonymous_request_returns_feed(self):
        song = self.create_song(
            title="Anonymous Feed Song",
            slug="anonymous-feed-song",
        )

        response = self.client.get(
            self.get_url(),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "results",
            response.data,
        )

        self.assertIn(
            "has_more",
            response.data,
        )

        self.assertIn(
            "next_cursor",
            response.data,
        )

        returned_ids = [
            item["content"]["id"]
            for item in response.data["results"]
            if item["content_type"] == "song"
        ]

        self.assertIn(
            song.id,
            returned_ids,
        )

    def test_authenticated_request_returns_feed(self):
        song = self.create_song(
            title="Authenticated Feed Song",
            slug="authenticated-feed-song",
        )

        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            self.get_url(),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        returned_ids = [
            item["content"]["id"]
            for item in response.data["results"]
            if item["content_type"] == "song"
        ]

        self.assertIn(
            song.id,
            returned_ids,
        )

    # ========================================================
    # LIMIT
    # ========================================================

    def test_limit_parameter_is_respected(self):
        for index in range(10):
            self.create_song(
                title=f"Limit Song {index}",
                slug=f"limit-song-{index}",
            )

        response = self.client.get(
            self.get_url(),
            {
                "limit": 3,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

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

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "detail",
            response.data,
        )

    def test_limit_above_maximum_is_capped(self):
        for index in range(
            MusicFeedService.MAX_LIMIT + 10,
        ):
            self.create_song(
                title=f"Maximum Song {index}",
                slug=f"maximum-song-{index}",
            )

        response = self.client.get(
            self.get_url(),
            {
                "limit": 1000,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertLessEqual(
            len(response.data["results"]),
            MusicFeedService.MAX_LIMIT,
        )

    # ========================================================
    # RESPONSE SHAPE
    # ========================================================

    def test_feed_item_has_expected_shape(self):
        self.create_song(
            title="Response Shape Song",
            slug="response-shape-song",
        )

        response = self.client.get(
            self.get_url(),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        song_items = [
            item
            for item in response.data["results"]
            if item["content_type"] == "song"
        ]

        self.assertTrue(
            song_items,
        )

        item = song_items[0]

        self.assertIn(
            "content_type",
            item,
        )

        self.assertIn(
            "source",
            item,
        )

        self.assertIn(
            "content",
            item,
        )

        self.assertEqual(
            item["content_type"],
            "song",
        )

        self.assertIsInstance(
            item["source"],
            str,
        )

        self.assertIsInstance(
            item["content"],
            dict,
        )

        self.assertIn(
            "id",
            item["content"],
        )

        self.assertIn(
            "title",
            item["content"],
        )

    # ========================================================
    # CURSOR PAGINATION
    # ========================================================

    def test_first_page_returns_cursor_when_more_items_exist(self):
        for index in range(5):
            self.create_song(
                title=f"Cursor Song {index}",
                slug=f"cursor-song-{index}",
            )

        response = self.client.get(
            self.get_url(),
            {
                "limit": 1,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertTrue(
            response.data["has_more"],
        )

        self.assertIsNotNone(
            response.data["next_cursor"],
        )

    def test_next_cursor_returns_next_page(self):
        for index in range(5):
            self.create_song(
                title=f"Next Page Song {index}",
                slug=f"next-page-song-{index}",
            )

        first_response = self.client.get(
            self.get_url(),
            {
                "limit": 1,
            },
        )

        self.assertEqual(
            first_response.status_code,
            200,
        )

        first_cursor = (
            first_response.data["next_cursor"]
        )

        self.assertIsNotNone(
            first_cursor,
        )

        first_item = (
            first_response.data["results"][0]
        )

        second_response = self.client.get(
            self.get_url(),
            {
                "limit": 1,
                "cursor": first_cursor,
            },
        )

        self.assertEqual(
            second_response.status_code,
            200,
        )

        self.assertEqual(
            len(second_response.data["results"]),
            1,
        )

        second_item = (
            second_response.data["results"][0]
        )

        self.assertNotEqual(
            first_item["content_type"],
            "",
        )

        self.assertNotEqual(
            second_item["content_type"],
            "",
        )

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
        for index in range(5):
            self.create_song(
                title=f"Stable Cursor Song {index}",
                slug=f"stable-cursor-song-{index}",
            )

        first_response = self.client.get(
            self.get_url(),
            {
                "limit": 2,
            },
        )

        self.assertEqual(
            first_response.status_code,
            200,
        )

        first_cursor = (
            first_response.data["next_cursor"]
        )

        self.assertIsNotNone(
            first_cursor,
        )

        second_response = self.client.get(
            self.get_url(),
            {
                "limit": 2,
                "cursor": first_cursor,
            },
        )

        self.assertEqual(
            second_response.status_code,
            200,
        )

        second_cursor = (
            second_response.data["next_cursor"]
        )

        if second_response.data["has_more"]:
            self.assertIsNotNone(
                second_cursor,
            )

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
            first_page_ids.isdisjoint(
                second_page_ids,
            ),
        )

    def test_invalid_cursor_returns_bad_request(self):
        response = self.client.get(
            self.get_url(),
            {
                "cursor": "not-a-valid-feed-cursor",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "detail",
            response.data,
        )

    # ========================================================
    # EMPTY FEED
    # ========================================================

    def test_empty_feed_returns_valid_response(self):
        Artist.objects.all().delete()

        response = self.client.get(
            self.get_url(),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

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