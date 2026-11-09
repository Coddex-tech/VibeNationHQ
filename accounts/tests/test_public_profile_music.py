from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from rest_framework import status
from rest_framework.test import APITestCase

from music.models import (
    Album,
    Artist,
    CommunityPost,
    CommunityPostTarget,
    Song,
)


User = get_user_model()


class PublicProfileMusicAPITests(APITestCase):
    """
    Tests for the public user's Music timeline.

    Endpoint:
        GET /accounts/users/<username>/music/
    """

    @classmethod
    def setUpTestData(cls):
        cls.profile = User.objects.create_user(
            username="musicuser",
            email="musicuser@example.com",
            password="TestPassword123!",
            onboarding_completed=True,
        )

        cls.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="TestPassword123!",
            onboarding_completed=True,
        )

        cls.hidden_profile = User.objects.create_user(
            username="hiddenuser",
            email="hiddenuser@example.com",
            password="TestPassword123!",
            onboarding_completed=False,
        )

        cls.song = Song.objects.create(
            title="Test Song",
            slug="test-song",
        )

        cls.second_song = Song.objects.create(
            title="Second Test Song",
            slug="second-test-song",
        )

        cls.album = Album.objects.create(
            title="Test Album",
            slug="test-album",
        )

        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
        )

    def setUp(self):
        self.url = reverse(
            "public-user-profile-music",
            kwargs={
                "username": self.profile.username,
            },
        )

    # ========================================================
    # HELPERS
    # ========================================================

    def create_post(
        self,
        *,
        user=None,
        target_type,
        target,
        status_value=CommunityPost.Status.PUBLISHED,
        content="Test community post",
        slug=None,
    ):
        user = user or self.profile

        post = CommunityPost.objects.create(
            user=user,
            content=content,
            slug=slug or (
                f"test-post-{CommunityPost.objects.count() + 1}"
            ),
            status=status_value,
        )

        target_fields = {
            "song": {"song": target},
            "album": {"album": target},
            "artist": {"artist": target},
        }

        CommunityPostTarget.objects.create(
            post=post,
            target_type=target_type,
            **target_fields[target_type],
        )

        return post

    def set_post_time(self, post, created_at):
        CommunityPost.objects.filter(pk=post.pk).update(
            created_at=created_at,
        )

    def get_results(self, response):
        return response.data["results"]

    # ========================================================
    # ACCESS
    # ========================================================

    def test_music_timeline_is_publicly_accessible(self):
        self.create_post(
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("results", response.data)

    def test_anonymous_user_can_view_music_timeline(self):
        self.create_post(
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(self.get_results(response)),
            1,
        )

    def test_authenticated_user_can_view_another_users_music(self):
        self.client.force_authenticate(
            user=self.other_user,
        )

        self.create_post(
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_nonexistent_profile_returns_404(self):
        response = self.client.get(
            reverse(
                "public-user-profile-music",
                kwargs={"username": "does-not-exist"},
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_incomplete_profile_is_not_publicly_accessible(self):
        response = self.client.get(
            reverse(
                "public-user-profile-music",
                kwargs={"username": self.hidden_profile.username},
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ========================================================
    # TARGET AGGREGATION
    # ========================================================

    def test_song_album_and_artist_are_returned(self):
        self.create_post(
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
        )

        self.create_post(
            target_type=CommunityPostTarget.TargetType.ALBUM,
            target=self.album,
        )

        self.create_post(
            target_type=CommunityPostTarget.TargetType.ARTIST,
            target=self.artist,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = self.get_results(response)

        self.assertEqual(len(results), 3)

        returned_types = {
            item["target_type"]
            for item in results
        }

        self.assertEqual(
            returned_types,
            {"song", "album", "artist"},
        )

    def test_multiple_posts_about_same_song_produce_one_entry(self):
        self.create_post(
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
            slug="song-post-one",
        )

        self.create_post(
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
            slug="song-post-two",
        )

        self.create_post(
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
            slug="song-post-three",
        )

        response = self.client.get(self.url)

        results = self.get_results(response)

        self.assertEqual(len(results), 1)

        self.assertEqual(
            results[0]["target_type"],
            "song",
        )

        self.assertEqual(
            results[0]["post_count"],
            3,
        )

        self.assertEqual(
            results[0]["entity"]["id"],
            self.song.pk,
        )

    def test_different_entity_types_are_aggregated_separately(self):
        self.create_post(
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
            slug="song-post-one",
        )

        self.create_post(
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
            slug="song-post-two",
        )

        self.create_post(
            target_type=CommunityPostTarget.TargetType.ALBUM,
            target=self.album,
        )

        response = self.client.get(self.url)

        results = self.get_results(response)

        self.assertEqual(len(results), 2)

        song_result = next(
            item for item in results
            if item["target_type"] == "song"
        )

        album_result = next(
            item for item in results
            if item["target_type"] == "album"
        )

        self.assertEqual(song_result["post_count"], 2)
        self.assertEqual(album_result["post_count"], 1)

    # ========================================================
    # POST VISIBILITY
    # ========================================================

    def test_hidden_posts_are_excluded(self):
        self.create_post(
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
            status_value=CommunityPost.Status.HIDDEN,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            len(self.get_results(response)),
            0,
        )

    def test_removed_posts_are_excluded(self):
        self.create_post(
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
            status_value=CommunityPost.Status.REMOVED,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            len(self.get_results(response)),
            0,
        )

    def test_posts_from_other_users_are_excluded(self):
        self.create_post(
            user=self.other_user,
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            len(self.get_results(response)),
            0,
        )

    # ========================================================
    # ORDERING
    # ========================================================

    def test_entities_are_ordered_by_latest_published_post(self):
        now = timezone.now()

        song_post = self.create_post(
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
        )

        album_post = self.create_post(
            target_type=CommunityPostTarget.TargetType.ALBUM,
            target=self.album,
        )

        artist_post = self.create_post(
            target_type=CommunityPostTarget.TargetType.ARTIST,
            target=self.artist,
        )

        self.set_post_time(
            song_post,
            now - timedelta(days=3),
        )

        self.set_post_time(
            album_post,
            now - timedelta(days=2),
        )

        self.set_post_time(
            artist_post,
            now - timedelta(days=1),
        )

        response = self.client.get(self.url)

        results = self.get_results(response)

        self.assertEqual(
            [item["target_type"] for item in results],
            ["artist", "album", "song"],
        )

    def test_new_post_moves_existing_entity_to_top(self):
        now = timezone.now()

        song_post = self.create_post(
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
        )

        album_post = self.create_post(
            target_type=CommunityPostTarget.TargetType.ALBUM,
            target=self.album,
        )

        self.set_post_time(
            song_post,
            now - timedelta(days=2),
        )

        self.set_post_time(
            album_post,
            now - timedelta(days=1),
        )

        # A newer post about the existing song.
        new_song_post = self.create_post(
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
            slug="new-song-post",
        )

        self.set_post_time(
            new_song_post,
            now,
        )

        response = self.client.get(self.url)

        results = self.get_results(response)

        self.assertEqual(
            results[0]["target_type"],
            "song",
        )

        self.assertEqual(
            results[0]["post_count"],
            2,
        )

    def test_latest_post_at_represents_most_recent_post(self):
        now = timezone.now()

        first_post = self.create_post(
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
            slug="first-song-post",
        )

        second_post = self.create_post(
            target_type=CommunityPostTarget.TargetType.SONG,
            target=self.song,
            slug="second-song-post",
        )

        latest_time = now - timedelta(hours=2)

        self.set_post_time(
            first_post,
            now - timedelta(days=2),
        )

        self.set_post_time(
            second_post,
            latest_time,
        )

        response = self.client.get(self.url)

        result = self.get_results(response)[0]

        self.assertEqual(
            result["post_count"],
            2,
        )

        returned_datetime = parse_datetime(
            result["latest_post_at"],
        )

        self.assertIsNotNone(returned_datetime)

        expected_datetime = CommunityPost.objects.get(
            pk=second_post.pk,
        ).created_at

        self.assertEqual(
            returned_datetime.timestamp(),
            expected_datetime.timestamp(),
        )

    # ========================================================
    # PAGINATION
    # ========================================================

    def test_music_timeline_uses_pagination(self):
        for index in range(25):
            song = Song.objects.create(
                title=f"Pagination Song {index}",
                slug=f"pagination-song-{index}",
            )

            self.create_post(
                target_type=CommunityPostTarget.TargetType.SONG,
                target=song,
                slug=f"pagination-post-{index}",
            )

        response = self.client.get(
            self.url,
            {"page_size": 10},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(response.data["count"], 25)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])

    def test_second_page_returns_remaining_entities(self):
        for index in range(25):
            song = Song.objects.create(
                title=f"Page Song {index}",
                slug=f"page-song-{index}",
            )

            self.create_post(
                target_type=CommunityPostTarget.TargetType.SONG,
                target=song,
                slug=f"page-post-{index}",
            )

        first_response = self.client.get(
            self.url,
            {"page_size": 10},
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(first_response.data["results"]), 10)

        second_response = self.client.get(
            self.url,
            {"page_size": 10, "page": 2},
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(second_response.data["results"]), 10)

        first_ids = {
            item["entity"]["id"]
            for item in first_response.data["results"]
        }

        second_ids = {
            item["entity"]["id"]
            for item in second_response.data["results"]
        }

        self.assertTrue(first_ids.isdisjoint(second_ids))