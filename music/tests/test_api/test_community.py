from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase

from music.models import (
    Album,
    Artist,
    CommunityPost,
    CommunityPostComment,
    CommunityPostTarget,
    Song,
    CommunityPostLike,
    CommunityPostCommentLike,
    CommunityPostReport,
    CommunityPostCommentReport,
    MusicFeedInteraction,
)

from music.services.community import (
    CommunityPostService,
    CommunityPostCommentService,
)


User = get_user_model()


class CommunityPostListCreateAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="commentuser@example.com",
        )

        cls.other_user = User.objects.create_user(
            username="otheruser",
            password="testpassword",
            email="otheruser@example.com",
        )

        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.album = Album.objects.create(
            title="Test Album",
            slug="test-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.album.artists.add(cls.artist)

        cls.song = Song.objects.create(
            title="Test Song",
            slug="test-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.song.artists.add(cls.artist)

        cls.draft_song = Song.objects.create(
            title="Draft Song",
            slug="draft-song",
            status=Song.Status.DRAFT,
        )

        cls.draft_album = Album.objects.create(
            title="Draft Album",
            slug="draft-album",
            status=Album.Status.DRAFT,
        )

        cls.inactive_artist = Artist.objects.create(
            name="Inactive Artist",
            slug="inactive-artist",
            is_active=False,
        )

    def test_anonymous_user_can_list_posts(self):
        url = reverse("music_api:community-post-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_anonymous_user_cannot_create_post(self):
        url = reverse("music_api:community-post-list")

        response = self.client.post(
            url,
            {
                "content": "Test community post",
                "target": {
                    "target_type": "song",
                    "song": self.song.id,
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_create_song_post(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("music_api:community-post-list")

        response = self.client.post(
            url,
            {
                "content": "This song is amazing!",
                "rating": "4.5",
                "target": {
                    "target_type": "song",
                    "song": self.song.id,
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["content"],
            "This song is amazing!",
        )

        self.assertEqual(
            response.data["rating"],
            "4.5",
        )

        self.assertEqual(
            response.data["target"]["target_type"],
            "song",
        )

        self.assertEqual(
            CommunityPost.objects.count(),
            1,
        )

    def test_authenticated_user_can_create_album_post(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("music_api:community-post-list")

        response = self.client.post(
            url,
            {
                "content": "Great album!",
                "target": {
                    "target_type": "album",
                    "album": self.album.id,
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["target"]["target_type"],
            "album",
        )

    def test_authenticated_user_can_create_artist_post(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("music_api:community-post-list")

        response = self.client.post(
            url,
            {
                "content": "Test artist post",
                "target": {
                    "target_type": "artist",
                    "artist": self.artist.id,
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["target"]["target_type"],
            "artist",
        )

    def test_cannot_create_post_for_draft_song(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("music_api:community-post-list")

        response = self.client.post(
            url,
            {
                "content": "Draft song post",
                "target": {
                    "target_type": "song",
                    "song": self.draft_song.id,
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            CommunityPost.objects.count(),
            0,
        )

    def test_cannot_create_post_for_draft_album(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("music_api:community-post-list")

        response = self.client.post(
            url,
            {
                "content": "Draft album post",
                "target": {
                    "target_type": "album",
                    "album": self.draft_album.id,
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_cannot_create_post_for_inactive_artist(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("music_api:community-post-list")

        response = self.client.post(
            url,
            {
                "content": "Inactive artist post",
                "target": {
                    "target_type": "artist",
                    "artist": self.inactive_artist.id,
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_target_type_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("music_api:community-post-list")

        response = self.client.post(
            url,
            {
                "content": "Invalid target",
                "target": {
                    "target_type": "invalid",
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_mixed_internal_targets_are_rejected(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("music_api:community-post-list")

        response = self.client.post(
            url,
            {
                "content": "Mixed target",
                "target": {
                    "target_type": "song",
                    "song": self.song.id,
                    "album": self.album.id,
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_authenticated_user_can_create_text_only_post(self):
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "music_api:community-post-list",
        )

        response = self.client.post(
            url,
            {
                "content": "This is just a normal community post.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["content"],
            "This is just a normal community post.",
        )

        self.assertIsNone(
            response.data["rating"],
        )

        self.assertIsNone(
            response.data["target"],
        )

        post = CommunityPost.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(
            post.content,
            "This is just a normal community post.",
        )

        self.assertFalse(
            CommunityPostTarget.objects.filter(
                post=post,
            ).exists()
        )

    def test_cannot_create_text_only_post_with_rating(self):
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "music_api:community-post-list",
        )

        response = self.client.post(
            url,
            {
                "content": "This should not have a rating.",
                "rating": "4.5",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            CommunityPost.objects.filter(
                content="This should not have a rating.",
            ).exists()
        )

    def test_cannot_create_artist_post_with_rating(self):
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "music_api:community-post-list",
        )

        response = self.client.post(
            url,
            {
                "content": "Artist post with invalid rating.",
                "rating": "4.5",
                "target": {
                    "target_type": "artist",
                    "artist": self.artist.id,
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            CommunityPost.objects.filter(
                content="Artist post with invalid rating.",
            ).exists()
        )

class CommunityPostServiceTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="serviceuser",
            password="testpassword",
            email="serviceuser@example.com",
        )

        cls.artist = Artist.objects.create(
            name="Service Artist",
            slug="service-artist",
            is_active=True,
        )

        cls.song = Song.objects.create(
            title="Service Song",
            slug="service-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.song.artists.add(cls.artist)

        cls.album = Album.objects.create(
            title="Service Album",
            slug="service-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        cls.album.artists.add(cls.artist)

    def test_service_allows_text_only_post_without_rating(self):
        post = CommunityPostService.create(
            user=self.user,
            content="Text-only service post.",
        )

        self.assertEqual(
            post.content,
            "Text-only service post.",
        )

        self.assertIsNone(
            post.rating,
        )

        self.assertFalse(
            CommunityPostTarget.objects.filter(
                post=post,
            ).exists()
        )

    def test_service_rejects_rating_without_target(self):
        with self.assertRaises(ValidationError):
            CommunityPostService.create(
                user=self.user,
                content="Invalid rated post.",
                rating=4.5,
            )

        self.assertFalse(
            CommunityPost.objects.filter(
                content="Invalid rated post.",
            ).exists()
        )

    def test_service_rejects_rating_for_artist_target(self):
        with self.assertRaises(ValidationError):
            CommunityPostService.create(
                user=self.user,
                content="Invalid artist rating.",
                rating=4.5,
                target_data={
                    "target_type": (
                        CommunityPostTarget.TargetType.ARTIST
                    ),
                    "artist": self.artist,
                },
            )

        self.assertFalse(
            CommunityPost.objects.filter(
                content="Invalid artist rating.",
            ).exists()
        )

    def test_service_allows_rating_for_song_target(self):
        post = CommunityPostService.create(
            user=self.user,
            content="Rated song post.",
            rating=4.5,
            target_data={
                "target_type": (
                    CommunityPostTarget.TargetType.SONG
                ),
                "song": self.song,
            },
        )

        self.assertEqual(
            post.rating,
            4.5,
        )

        target = CommunityPostTarget.objects.get(
            post=post,
        )

        self.assertEqual(
            target.target_type,
            CommunityPostTarget.TargetType.SONG,
        )

        self.assertEqual(
            target.song_id,
            self.song.id,
        )

    def test_service_allows_rating_for_album_target(self):
        post = CommunityPostService.create(
            user=self.user,
            content="Rated album post.",
            rating=5.0,
            target_data={
                "target_type": (
                    CommunityPostTarget.TargetType.ALBUM
                ),
                "album": self.album,
            },
        )

        self.assertEqual(
            post.rating,
            5.0,
        )

        target = CommunityPostTarget.objects.get(
            post=post,
        )

        self.assertEqual(
            target.target_type,
            CommunityPostTarget.TargetType.ALBUM,
        )

        self.assertEqual(
            target.album_id,
            self.album.id,
        )

    def test_service_update_rejects_rating_without_target(self):
        post = CommunityPost.objects.create(
            user=self.user,
            content="Text-only post.",
            status=CommunityPost.Status.PUBLISHED,
        )

        with self.assertRaises(ValidationError):
            CommunityPostService.update(
                post=post,
                content="Updated text.",
                rating=4.5,
            )

        post.refresh_from_db()

        self.assertEqual(
            post.content,
            "Text-only post.",
        )

        self.assertIsNone(
            post.rating,
        )

    def test_service_update_allows_rating_for_song_target(self):
        post = CommunityPost.objects.create(
            user=self.user,
            content="Song post.",
            status=CommunityPost.Status.PUBLISHED,
            rating=3.0,
        )

        CommunityPostTarget.objects.create(
            post=post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=self.song,
        )

        updated_post = CommunityPostService.update(
            post=post,
            content="Updated song post.",
            rating=4.5,
        )

        self.assertEqual(
            updated_post.content,
            "Updated song post.",
        )

        self.assertEqual(
            updated_post.rating,
            4.5,
        )

        self.assertTrue(
            updated_post.is_edited,
        )

    def test_service_update_can_clear_rating(self):
        post = CommunityPost.objects.create(
            user=self.user,
            content="Rated song post.",
            status=CommunityPost.Status.PUBLISHED,
            rating=4.5,
        )

        CommunityPostTarget.objects.create(
            post=post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=self.song,
        )

        updated_post = CommunityPostService.update(
            post=post,
            content="Updated post.",
            rating=None,
        )

        self.assertIsNone(
            updated_post.rating,
        )



class CommunityPostListAPIViewVisibilityTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="commentuser@example.com",
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

        cls.published_post = CommunityPost.objects.create(
            user=cls.user,
            content="Published post",
            slug="visibility-test-published",
            status=CommunityPost.Status.PUBLISHED,
        )

        CommunityPostTarget.objects.create(
            post=cls.published_post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=cls.song,
        )

        cls.hidden_post = CommunityPost.objects.create(
            user=cls.user,
            content="Hidden post",
            slug="visibility-test-hidden",
            status=CommunityPost.Status.HIDDEN,
        )

        CommunityPostTarget.objects.create(
            post=cls.hidden_post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=cls.song,
        )

        cls.removed_post = CommunityPost.objects.create(
            user=cls.user,
            content="Removed post",
            slug="visibility-test-removed",
            status=CommunityPost.Status.REMOVED,
        )

        CommunityPostTarget.objects.create(
            post=cls.removed_post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=cls.song,
        )

    def test_only_published_posts_are_returned(self):
        url = reverse("music_api:community-post-list")

        response = self.client.get(url)

        self.assertEqual(response.data["count"], 1)

        returned_ids = [
            post["id"]
            for post in response.data["results"]
        ]

        self.assertIn(
            self.published_post.id,
            returned_ids,
        )

        self.assertNotIn(
            self.hidden_post.id,
            returned_ids,
        )

        self.assertNotIn(
            self.removed_post.id,
            returned_ids,
        )

    def test_list_response_is_paginated(self):
        url = reverse("music_api:community-post-list")

        response = self.client.get(url)

        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)



class CommunityPostViewAPIViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="viewtest@example.com",
            password="TestPassword123!",
        )

        self.other_user = User.objects.create_user(
            email="otherviewtest@example.com",
            password="TestPassword123!",
        )

        self.post = CommunityPost.objects.create(
            user=self.user,
            content="A post for view-count testing.",
            slug="view-count-test-published",
            status=CommunityPost.Status.PUBLISHED,
        )

        self.hidden_post = CommunityPost.objects.create(
            user=self.user,
            content="A hidden post.",
            slug="view-count-test-hidden",
            status=CommunityPost.Status.HIDDEN,
        )

        self.url = reverse(
            "music_api:community-post-view",
            kwargs={"pk": self.post.pk},
        )

    def test_authenticated_user_can_record_view(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            self.url,
            {"navigation_type": "navigate"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.post.refresh_from_db()
        self.assertEqual(self.post.views_count, 1)
        self.assertEqual(response.data["views_count"], 1)
        self.assertTrue(response.data["counted"])

    def test_unauthenticated_user_cannot_record_view(self):
        response = self.client.post(
            self.url,
            {"navigation_type": "navigate"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.post.refresh_from_db()
        self.assertEqual(self.post.views_count, 0)

    def test_authenticated_non_owner_refresh_counts_view(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            self.url,
            {"navigation_type": "reload"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.post.refresh_from_db()
        self.assertEqual(self.post.views_count, 1)
        self.assertTrue(response.data["counted"])

    def test_owner_refresh_does_not_count_view(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {"navigation_type": "reload"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.post.refresh_from_db()
        self.assertEqual(self.post.views_count, 0)
        self.assertEqual(response.data["views_count"], 0)
        self.assertFalse(response.data["counted"])

    def test_owner_navigation_counts_view(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {"navigation_type": "navigate"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.post.refresh_from_db()
        self.assertEqual(self.post.views_count, 1)
        self.assertTrue(response.data["counted"])

    def test_hidden_post_does_not_receive_view(self):
        self.client.force_authenticate(user=self.other_user)

        url = reverse(
            "music_api:community-post-view",
            kwargs={"pk": self.hidden_post.pk},
        )

        response = self.client.post(
            url,
            {"navigation_type": "navigate"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.hidden_post.refresh_from_db()
        self.assertEqual(self.hidden_post.views_count, 0)

    def test_nonexistent_post_returns_404(self):
        self.client.force_authenticate(user=self.other_user)

        url = reverse(
            "music_api:community-post-view",
            kwargs={"pk": 999999},
        )

        response = self.client.post(
            url,
            {"navigation_type": "navigate"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_request_is_not_allowed(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class CommunityPostDetailAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="commentuser@example.com",
        )

        cls.other_user = User.objects.create_user(
            username="otheruser",
            password="testpassword",
            email="otheruser@example.com",
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

        cls.post = CommunityPost.objects.create(
            user=cls.user,
            content="Original post",
            rating="4.0",
            status=CommunityPost.Status.PUBLISHED,
        )

        CommunityPostTarget.objects.create(
            post=cls.post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=cls.song,
        )

        cls.other_post = CommunityPost.objects.create(
            user=cls.other_user,
            content="Other user's post",
            status=CommunityPost.Status.PUBLISHED,
        )

        CommunityPostTarget.objects.create(
            post=cls.other_post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=cls.song,
        )

        cls.hidden_post = CommunityPost.objects.create(
            user=cls.user,
            content="Hidden post",
            status=CommunityPost.Status.HIDDEN,
        )

        CommunityPostTarget.objects.create(
            post=cls.hidden_post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=cls.song,
        )

    def test_anonymous_user_can_retrieve_post(self):
        url = reverse(
            "music_api:community-post-detail",
            kwargs={"pk": self.post.id},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["content"],
            "Original post",
        )

    def test_owner_can_update_content_without_changing_rating(self):
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "music_api:community-post-detail",
            kwargs={"pk": self.post.id},
        )

        response = self.client.patch(
            url,
            {
                "content": "Updated content only",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.content,
            "Updated content only",
        )

        self.assertEqual(
            self.post.rating,
            4.0,
        )

    def test_owner_can_update_rating_without_changing_content(self):
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "music_api:community-post-detail",
            kwargs={"pk": self.post.id},
        )

        response = self.client.patch(
            url,
            {
                "rating": "4.5",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.content,
            "Original post",
        )

        self.assertEqual(
            self.post.rating,
            4.5,
        )

    def test_owner_can_clear_rating(self):
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "music_api:community-post-detail",
            kwargs={"pk": self.post.id},
        )

        response = self.client.patch(
            url,
            {
                "rating": None,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.content,
            "Original post",
        )

        self.assertIsNone(
            self.post.rating,
        )

    def test_authenticated_user_can_retrieve_post(self):
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "music_api:community-post-detail",
            kwargs={"pk": self.post.id},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_owner_can_update_post(self):
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "music_api:community-post-detail",
            kwargs={"pk": self.post.id},
        )

        response = self.client.patch(
            url,
            {
                "content": "Updated post",
                "rating": "4.5",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.content,
            "Updated post",
        )

        self.assertEqual(
            self.post.rating,
            4.5,
        )

        self.assertTrue(
            self.post.is_edited,
        )

    def test_non_owner_cannot_update_post(self):
        self.client.force_authenticate(user=self.other_user)

        url = reverse(
            "music_api:community-post-detail",
            kwargs={"pk": self.post.id},
        )

        response = self.client.patch(
            url,
            {
                "content": "Hacked post",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.content,
            "Original post",
        )


    def test_owner_can_soft_delete_post(self):
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "music_api:community-post-detail",
            kwargs={"pk": self.post.id},
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        # The post remains in the database.
        self.assertTrue(
            CommunityPost.objects.filter(
                id=self.post.id,
            ).exists()
        )

        # Its status is changed to REMOVED.
        self.post.refresh_from_db()

        self.assertEqual(
            self.post.status,
            CommunityPost.Status.REMOVED,
        )

        # The associated target is retained for investigation.
        self.assertTrue(
            CommunityPostTarget.objects.filter(
                post=self.post,
            ).exists()
        )

    def test_non_owner_cannot_delete_post(self):
        self.client.force_authenticate(user=self.other_user)

        url = reverse(
            "music_api:community-post-detail",
            kwargs={"pk": self.post.id},
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            CommunityPost.objects.filter(
                id=self.post.id
            ).exists()
        )

    def test_anonymous_user_cannot_update_post(self):
        url = reverse(
            "music_api:community-post-detail",
            kwargs={"pk": self.post.id},
        )

        response = self.client.patch(
            url,
            {
                "content": "Anonymous update",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_anonymous_user_cannot_delete_post(self):
        url = reverse(
            "music_api:community-post-detail",
            kwargs={"pk": self.post.id},
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_target_cannot_be_changed(self):
        self.client.force_authenticate(user=self.user)

        album = Album.objects.create(
            title="Another Album",
            slug="another-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        album.artists.add(self.artist)

        url = reverse(
            "music_api:community-post-detail",
            kwargs={"pk": self.post.id},
        )

        response = self.client.patch(
            url,
            {
                "content": "Updated content",
                "target": {
                    "target_type": "album",
                    "album": album.id,
                },
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        target = CommunityPostTarget.objects.get(
            post=self.post
        )

        self.assertEqual(
            target.target_type,
            CommunityPostTarget.TargetType.SONG,
        )

        self.assertEqual(
            target.song_id,
            self.song.id,
        )

        self.assertIsNone(
            target.album_id,
        )

    def test_hidden_post_returns_404(self):
        url = reverse(
            "music_api:community-post-detail",
            kwargs={"pk": self.hidden_post.id},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    
    def test_removed_post_returns_404(self):
        removed_post = CommunityPost.objects.create(
            user=self.user,
            content="Removed post",
            status=CommunityPost.Status.REMOVED,
        )

        url = reverse(
            "music_api:community-post-detail",
            kwargs={"pk": removed_post.id},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_unknown_post_returns_404(self):
        url = reverse(
            "music_api:community-post-detail",
            kwargs={"pk": 999999},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )



class CommunityPostCommentDetailSoftDeleteTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="comment_owner",
            password="testpassword",
            email="commentowner@example.com",
        )

        cls.post = CommunityPost.objects.create(
            user=cls.user,
            content="Post to be removed",
            status=CommunityPost.Status.PUBLISHED,
        )

        cls.comment = CommunityPostComment.objects.create(
            user=cls.user,
            post=cls.post,
            content="Comment retained for moderation",
            status=CommunityPostComment.Status.PUBLISHED,
        )

    def test_comment_detail_returns_404_after_parent_post_is_removed(self):
        self.post.status = CommunityPost.Status.REMOVED
        self.post.save(update_fields=["status", "updated_at"])

        url = reverse(
            "music_api:community-comment-detail",
            kwargs={"pk": self.comment.pk},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            CommunityPostComment.objects.filter(
                pk=self.comment.pk,
            ).exists(),
        )

    def test_comment_cannot_be_updated_after_parent_post_is_removed(self):
        self.post.status = CommunityPost.Status.REMOVED
        self.post.save(update_fields=["status", "updated_at"])

        self.client.force_authenticate(user=self.user)

        url = reverse(
            "music_api:community-comment-detail",
            kwargs={"pk": self.comment.pk},
        )

        response = self.client.patch(
            url,
            {"content": "Attempted edit"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            self.comment.content,
            "Comment retained for moderation",
        )

    def test_comment_cannot_be_deleted_after_parent_post_is_removed(self):
        self.post.status = CommunityPost.Status.REMOVED
        self.post.save(update_fields=["status", "updated_at"])

        self.client.force_authenticate(user=self.user)

        url = reverse(
            "music_api:community-comment-detail",
            kwargs={"pk": self.comment.pk},
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            CommunityPostComment.objects.filter(
                pk=self.comment.pk,
            ).exists(),
        )
 
    def test_deleting_comment_soft_deletes_it(self):
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "music_api:community-comment-detail",
            kwargs={"pk": self.comment.pk},
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            self.comment.status,
            CommunityPostComment.Status.REMOVED,
        )

        self.assertTrue(
            CommunityPostComment.objects.filter(
                pk=self.comment.pk,
            ).exists()
        )

    def test_deleting_comment_decrements_post_counter(self):
        CommunityPost.objects.filter(
            pk=self.post.pk,
        ).update(comments_count=1)

        self.client.force_authenticate(user=self.user)

        url = reverse(
            "music_api:community-comment-detail",
            kwargs={"pk": self.comment.pk},
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.comments_count,
            0,
        )

    def test_deleting_reply_soft_deletes_it(self):
        reply = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            parent=self.comment,
            content="Reply to preserve",
            status=CommunityPostComment.Status.PUBLISHED,
        )

        CommunityPost.objects.filter(
            pk=self.post.pk,
        ).update(comments_count=2)

        CommunityPostComment.objects.filter(
            pk=self.comment.pk,
        ).update(replies_count=1)

        self.client.force_authenticate(user=self.user)

        url = reverse(
            "music_api:community-comment-detail",
            kwargs={"pk": reply.pk},
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        reply.refresh_from_db()

        self.assertEqual(
            reply.status,
            CommunityPostComment.Status.REMOVED,
        )

        self.assertTrue(
            CommunityPostComment.objects.filter(
                pk=reply.pk,
            ).exists()
        )

        self.post.refresh_from_db()
        self.comment.refresh_from_db()

        self.assertEqual(self.post.comments_count, 1)
        self.assertEqual(self.comment.replies_count, 0)


class CommunityPostCommentListCreateAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="commentuser",
            password="testpass123",
            email="commentuser@example.com",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="testpass123",
            email="otheruser@example.com",
        )

        self.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        self.song = Song.objects.create(
            title="Test Song",
            slug="test-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.song.artists.add(self.artist)

        self.post = CommunityPost.objects.create(
            user=self.user,
            content="Test community post",
            status=CommunityPost.Status.PUBLISHED,
        )

        CommunityPostTarget.objects.create(
            post=self.post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=self.song,
        )

    def test_anonymous_user_can_list_comments(self):
        response = self.client.get(
            reverse(
                "music_api:community-post-comment-list",
                kwargs={"post_id": self.post.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_list_comments(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                "music_api:community-post-comment-list",
                kwargs={"post_id": self.post.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_only_top_level_comments_are_returned_by_default(self):
        top_level = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Top level comment",
            status=CommunityPostComment.Status.PUBLISHED,
        )

        CommunityPostComment.objects.create(
            user=self.other_user,
            post=self.post,
            parent=top_level,
            content="Reply",
            status=CommunityPostComment.Status.PUBLISHED,
        )

        response = self.client.get(
            reverse(
                "music_api:community-post-comment-list",
                kwargs={"post_id": self.post.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], top_level.id)

    def test_parent_query_parameter_returns_replies(self):
        top_level = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Top level comment",
            status=CommunityPostComment.Status.PUBLISHED,
        )

        reply = CommunityPostComment.objects.create(
            user=self.other_user,
            post=self.post,
            parent=top_level,
            content="Reply",
            status=CommunityPostComment.Status.PUBLISHED,
        )

        response = self.client.get(
            reverse(
                "music_api:community-post-comment-list",
                kwargs={"post_id": self.post.id},
            ),
            {"parent": top_level.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], reply.id)

    def test_hidden_comments_are_not_returned(self):
        CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Visible comment",
            status=CommunityPostComment.Status.PUBLISHED,
        )

        CommunityPostComment.objects.create(
            user=self.other_user,
            post=self.post,
            content="Hidden comment",
            status=CommunityPostComment.Status.HIDDEN,
        )

        response = self.client.get(
            reverse(
                "music_api:community-post-comment-list",
                kwargs={"post_id": self.post.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"], "Visible comment")

    def test_anonymous_user_cannot_create_comment(self):
        response = self.client.post(
            reverse(
                "music_api:community-post-comment-list",
                kwargs={"post_id": self.post.id},
            ),
            {
                "post": self.post.id,
                "content": "Anonymous comment",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_create_comment(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse(
                "music_api:community-post-comment-list",
                kwargs={"post_id": self.post.id},
            ),
            {
                "post": self.post.id,
                "content": "My comment",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        comment = CommunityPostComment.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.content, "My comment")

        interaction = MusicFeedInteraction.objects.get(
            user=self.user,
            interaction_type=(
                MusicFeedInteraction.InteractionType.COMMENT_COMMUNITY_POST
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

    def test_authenticated_user_can_create_reply(self):
        parent = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Parent comment",
            status=CommunityPostComment.Status.PUBLISHED,
        )

        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            reverse(
                "music_api:community-post-comment-list",
                kwargs={"post_id": self.post.id},
            ),
            {
                "post": self.post.id,
                "parent": parent.id,
                "content": "My reply",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        reply = CommunityPostComment.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(reply.parent, parent)
        self.assertEqual(reply.post, self.post)
        self.assertEqual(reply.user, self.other_user)

        interaction = MusicFeedInteraction.objects.get(
            user=self.other_user,
            interaction_type=(
                MusicFeedInteraction.InteractionType.COMMENT_COMMUNITY_POST
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

    def test_comment_increments_post_comments_count(self):
        self.client.force_authenticate(user=self.user)

        self.assertEqual(self.post.comments_count, 0)

        response = self.client.post(
            reverse(
                "music_api:community-post-comment-list",
                kwargs={"post_id": self.post.id},
            ),
            {
                "post": self.post.id,
                "content": "New comment",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.post.refresh_from_db()

        self.assertEqual(self.post.comments_count, 1)

    def test_reply_increments_parent_replies_count(self):
        parent = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Parent comment",
            status=CommunityPostComment.Status.PUBLISHED,
        )

        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            reverse(
                "music_api:community-post-comment-list",
                kwargs={"post_id": self.post.id},
            ),
            {
                "post": self.post.id,
                "parent": parent.id,
                "content": "Reply",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        parent.refresh_from_db()

        self.assertEqual(parent.replies_count, 1)


class CommunityPostCommentDetailAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="commentowner",
            password="testpass123",
            email="commentowner@example.com",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="testpass123",
            email="otheruser@example.com",
        )

        self.post = CommunityPost.objects.create(
            user=self.user,
            content="Test community post",
            status=CommunityPost.Status.PUBLISHED,
        )

        self.comment = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Original comment",
        )

    def detail_url(self):
        return reverse(
            "music_api:community-comment-detail",
            kwargs={"pk": self.comment.id},
        )

    def test_anonymous_user_can_retrieve_comment(self):
        response = self.client.get(self.detail_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.comment.id)

    def test_authenticated_user_can_retrieve_comment(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.detail_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.comment.id)

    def test_owner_can_update_comment(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            self.detail_url(),
            {
                "content": "Updated comment",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "Updated comment")

        self.comment.refresh_from_db()

        self.assertEqual(
            self.comment.content,
            "Updated comment",
        )
        self.assertTrue(self.comment.is_edited)

    def test_non_owner_cannot_update_comment(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            self.detail_url(),
            {
                "content": "Hacked comment",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.comment.refresh_from_db()

        self.assertEqual(
            self.comment.content,
            "Original comment",
        )

    def test_anonymous_user_cannot_update_comment(self):
        response = self.client.patch(
            self.detail_url(),
            {
                "content": "Anonymous edit",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_owner_can_delete_comment(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.detail_url())

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            CommunityPostComment.objects.filter(
                id=self.comment.id
            ).exists()
        )

    def test_non_owner_cannot_delete_comment(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(self.detail_url())

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            CommunityPostComment.objects.filter(
                id=self.comment.id
            ).exists()
        )

    def test_anonymous_user_cannot_delete_comment(self):
        response = self.client.delete(self.detail_url())

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertTrue(
            CommunityPostComment.objects.filter(
                id=self.comment.id
            ).exists()
        )

    def test_update_does_not_change_comment_owner(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            self.detail_url(),
            {
                "content": "Updated content",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.comment.refresh_from_db()

        self.assertEqual(
            self.comment.user,
            self.user,
        )

    def test_update_does_not_change_comment_post(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            self.detail_url(),
            {
                "content": "Updated content",
                "post": 999999,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.comment.refresh_from_db()

        self.assertEqual(
            self.comment.post,
            self.post,
        )

    def test_deleting_comment_decrements_post_comments_count(self):
        self.post.comments_count = 1
        self.post.save(update_fields=["comments_count"])

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.detail_url())

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.comments_count,
            0,
        )

    def test_deleting_reply_decrements_parent_replies_count(self):
        parent = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Parent comment",
        )

        reply = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            parent=parent,
            content="Reply",
        )

        parent.replies_count = 1
        parent.save(update_fields=["replies_count"])

        self.client.force_authenticate(user=self.user)

        url = reverse(
            "music_api:community-comment-detail",
            kwargs={"pk": reply.id},
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        parent.refresh_from_db()

        self.assertEqual(
            parent.replies_count,
            0,
        )

    def test_deleting_comment_deletes_entire_reply_subtree_and_updates_counters(self):
        root = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Root comment",
        )

        reply = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            parent=root,
            content="Reply",
        )

        nested_reply = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            parent=reply,
            content="Nested reply",
        )

        deeply_nested_reply = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            parent=nested_reply,
            content="Deeply nested reply",
        )

        self.post.comments_count = 4
        self.post.save(
            update_fields=["comments_count"],
        )

        root.replies_count = 1
        root.save(
            update_fields=["replies_count"],
        )

        reply.replies_count = 1
        reply.save(
            update_fields=["replies_count"],
        )

        nested_reply.replies_count = 1
        nested_reply.save(
            update_fields=["replies_count"],
        )

        self.client.force_authenticate(
            user=self.user,
        )

        url = reverse(
            "music_api:community-comment-detail",
            kwargs={"pk": reply.id},
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        # The deleted reply and every descendant must be gone.
        self.assertFalse(
            CommunityPostComment.objects.filter(
                id=reply.id,
            ).exists()
        )

        self.assertFalse(
            CommunityPostComment.objects.filter(
                id=nested_reply.id,
            ).exists()
        )

        self.assertFalse(
            CommunityPostComment.objects.filter(
                id=deeply_nested_reply.id,
            ).exists()
        )

        # The root comment survives.
        self.assertTrue(
            CommunityPostComment.objects.filter(
                id=root.id,
            ).exists()
        )

        # Four total comments existed.
        # Three were deleted.
        self.post.refresh_from_db()

        self.assertEqual(
            self.post.comments_count,
            1,
        )

        # Root had one direct reply, which was deleted.
        root.refresh_from_db()

        self.assertEqual(
            root.replies_count,
            0,
        )

    def test_deleting_comment_decrements_post_comments_count(self):
        CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Comment",
        )

        self.post.comments_count = 1
        self.post.save(
            update_fields=["comments_count"],
        )

        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.delete(
            self.detail_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.comments_count,
            0,
        )


class CommunityPostReportAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="reporter",
            password="testpass123",
            email="reporter@example.com",
        )

        self.other_user = User.objects.create_user(
            username="another_reporter",
            password="testpass123",
            email="anotherreporter@example.com",
        )

        self.post = CommunityPost.objects.create(
            user=self.user,
            content="This is a community post.",
            status=CommunityPost.Status.PUBLISHED,
        )

        self.url = reverse(
            "music_api:community-post-report",
            kwargs={"pk": self.post.id},
        )

    def test_anonymous_user_cannot_report_post(self):
        response = self.client.post(
            self.url,
            {
                "reason": CommunityPostReport.Reason.SPAM,
                "details": "This post looks like spam.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertFalse(
            CommunityPostReport.objects.filter(
                post=self.post,
            ).exists()
        )

    def test_authenticated_user_can_report_post(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                "reason": CommunityPostReport.Reason.SPAM,
                "details": "This post is spam.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["reason"],
            CommunityPostReport.Reason.SPAM,
        )

        self.assertEqual(
            response.data["details"],
            "This post is spam.",
        )

        self.assertTrue(
            CommunityPostReport.objects.filter(
                user=self.user,
                post=self.post,
            ).exists()
        )

    def test_report_belongs_to_authenticated_user(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                "reason": CommunityPostReport.Reason.HARASSMENT,
                "details": "This is harassment.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = CommunityPostReport.objects.get(
            post=self.post,
        )

        self.assertEqual(report.user, self.user)

    def test_valid_report_reason_is_accepted(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                "reason": CommunityPostReport.Reason.COPYRIGHT,
                "details": "This content appears to violate copyright.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["reason"],
            CommunityPostReport.Reason.COPYRIGHT,
        )

    def test_invalid_report_reason_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                "reason": "invalid_reason",
                "details": "Something is wrong.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            CommunityPostReport.objects.filter(
                post=self.post,
            ).exists()
        )

    def test_duplicate_report_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        first_response = self.client.post(
            self.url,
            {
                "reason": CommunityPostReport.Reason.SPAM,
                "details": "First report.",
            },
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        second_response = self.client.post(
            self.url,
            {
                "reason": CommunityPostReport.Reason.HARASSMENT,
                "details": "Second report.",
            },
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            CommunityPostReport.objects.filter(
                user=self.user,
                post=self.post,
            ).count(),
            1,
        )

    def test_different_users_can_report_same_post(self):
        self.client.force_authenticate(user=self.user)

        first_response = self.client.post(
            self.url,
            {
                "reason": CommunityPostReport.Reason.SPAM,
            },
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.force_authenticate(user=self.other_user)

        second_response = self.client.post(
            self.url,
            {
                "reason": CommunityPostReport.Reason.HARASSMENT,
            },
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            CommunityPostReport.objects.filter(
                post=self.post,
            ).count(),
            2,
        )

    def test_hidden_post_cannot_be_reported(self):
        self.post.status = CommunityPost.Status.HIDDEN
        self.post.save(update_fields=["status"])

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                "reason": CommunityPostReport.Reason.SPAM,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            CommunityPostReport.objects.filter(
                post=self.post,
            ).exists()
        )

    def test_report_details_are_optional(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                "reason": CommunityPostReport.Reason.SPAM,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = CommunityPostReport.objects.get(
            user=self.user,
            post=self.post,
        )

        self.assertEqual(report.details, "")

    def test_report_response_contains_expected_fields(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                "reason": CommunityPostReport.Reason.MISINFORMATION,
                "details": "This information appears to be false.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertIn("id", response.data)
        self.assertIn("user", response.data)
        self.assertIn("post", response.data)
        self.assertIn("reason", response.data)
        self.assertIn("details", response.data)
        self.assertIn("created_at", response.data)


class CommunityPostCommentReportAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="comment_reporter",
            password="testpass123",
            email="commentreporter@example.com",
        )

        self.other_user = User.objects.create_user(
            username="another_comment_reporter",
            password="testpass123",
            email="anothercommentreporter@example.com",
        )

        self.post = CommunityPost.objects.create(
            user=self.user,
            content="This is a community post.",
            status=CommunityPost.Status.PUBLISHED,
        )

        self.comment = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="This is a comment.",
            status=CommunityPostComment.Status.PUBLISHED,
        )

        self.url = reverse(
            "music_api:community-comment-report",
            kwargs={"pk": self.comment.id},
        )

    def test_anonymous_user_cannot_report_comment(self):
        response = self.client.post(
            self.url,
            {
                "reason": CommunityPostCommentReport.Reason.SPAM,
                "details": "This comment is spam.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertFalse(
            CommunityPostCommentReport.objects.filter(
                comment=self.comment,
            ).exists()
        )

    def test_authenticated_user_can_report_comment(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                "reason": CommunityPostCommentReport.Reason.SPAM,
                "details": "This comment is spam.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["reason"],
            CommunityPostCommentReport.Reason.SPAM,
        )

        self.assertEqual(
            response.data["details"],
            "This comment is spam.",
        )

        self.assertTrue(
            CommunityPostCommentReport.objects.filter(
                user=self.user,
                comment=self.comment,
            ).exists()
        )

    def test_report_belongs_to_authenticated_user(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                "reason": CommunityPostCommentReport.Reason.HARASSMENT,
                "details": "This comment is harassment.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = CommunityPostCommentReport.objects.get(
            comment=self.comment,
        )

        self.assertEqual(report.user, self.user)

    def test_valid_report_reason_is_accepted(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                "reason": CommunityPostCommentReport.Reason.MISINFORMATION,
                "details": "This comment contains false information.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["reason"],
            CommunityPostCommentReport.Reason.MISINFORMATION,
        )

    def test_invalid_report_reason_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                "reason": "invalid_reason",
                "details": "Something is wrong.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            CommunityPostCommentReport.objects.filter(
                comment=self.comment,
            ).exists()
        )

    def test_duplicate_report_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        first_response = self.client.post(
            self.url,
            {
                "reason": CommunityPostCommentReport.Reason.SPAM,
                "details": "First report.",
            },
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        second_response = self.client.post(
            self.url,
            {
                "reason": CommunityPostCommentReport.Reason.HARASSMENT,
                "details": "Second report.",
            },
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            CommunityPostCommentReport.objects.filter(
                user=self.user,
                comment=self.comment,
            ).count(),
            1,
        )

    def test_different_users_can_report_same_comment(self):
        self.client.force_authenticate(user=self.user)

        first_response = self.client.post(
            self.url,
            {
                "reason": CommunityPostCommentReport.Reason.SPAM,
            },
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.force_authenticate(user=self.other_user)

        second_response = self.client.post(
            self.url,
            {
                "reason": CommunityPostCommentReport.Reason.HARASSMENT,
            },
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            CommunityPostCommentReport.objects.filter(
                comment=self.comment,
            ).count(),
            2,
        )

    def test_hidden_comment_cannot_be_reported(self):
        self.comment.status = CommunityPostComment.Status.HIDDEN
        self.comment.save(update_fields=["status"])

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                "reason": CommunityPostCommentReport.Reason.SPAM,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            CommunityPostCommentReport.objects.filter(
                comment=self.comment,
            ).exists()
        )

    def test_comment_on_hidden_post_cannot_be_reported(self):
        self.post.status = CommunityPost.Status.HIDDEN
        self.post.save(update_fields=["status"])

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                "reason": CommunityPostCommentReport.Reason.SPAM,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            CommunityPostCommentReport.objects.filter(
                comment=self.comment,
            ).exists()
        )

    def test_report_details_are_optional(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                "reason": CommunityPostCommentReport.Reason.SPAM,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = CommunityPostCommentReport.objects.get(
            user=self.user,
            comment=self.comment,
        )

        self.assertEqual(report.details, "")

    def test_report_response_contains_expected_fields(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {
                "reason": CommunityPostCommentReport.Reason.HATE,
                "details": "This comment contains hateful content.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertIn("id", response.data)
        self.assertIn("user", response.data)
        self.assertIn("comment", response.data)
        self.assertIn("reason", response.data)
        self.assertIn("details", response.data)
        self.assertIn("created_at", response.data)