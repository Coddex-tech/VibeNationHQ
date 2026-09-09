from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
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
)



User = get_user_model()


class CommunityPostListCreateAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )

        cls.other_user = User.objects.create_user(
            username="otheruser",
            password="testpassword",
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
            status.HTTP_403_FORBIDDEN,
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


class CommunityPostListAPIViewVisibilityTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
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

        cls.published_post = CommunityPost.objects.create(
            user=cls.user,
            content="Published post",
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

        self.assertEqual(
            response.data["count"],
            1,
        )

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


class CommunityPostDetailAPIViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )

        cls.other_user = User.objects.create_user(
            username="otheruser",
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

    def test_owner_can_delete_post(self):
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

        self.assertFalse(
            CommunityPost.objects.filter(
                id=self.post.id
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
            status.HTTP_403_FORBIDDEN,
        )

    def test_anonymous_user_cannot_delete_post(self):
        url = reverse(
            "music_api:community-post-detail",
            kwargs={"pk": self.post.id},
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
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


class CommunityPostCommentListCreateAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="commentuser",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="testpass123",
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
            status.HTTP_403_FORBIDDEN,
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
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="testpass123",
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
            status.HTTP_403_FORBIDDEN,
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
            status.HTTP_403_FORBIDDEN,
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


class CommunityPostLikeAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="likeuser",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="otherlikeuser",
            password="testpass123",
        )

        self.post = CommunityPost.objects.create(
            user=self.user,
            content="Test community post",
            status=CommunityPost.Status.PUBLISHED,
        )

        self.url = reverse(
            "music_api:community-post-like",
            kwargs={"pk": self.post.id},
        )

    def test_anonymous_user_cannot_like_post(self):
        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            CommunityPostLike.objects.filter(
                post=self.post,
            ).exists()
        )

    def test_authenticated_user_can_like_post(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(response.data["liked"])
        self.assertEqual(response.data["likes_count"], 1)

        self.assertTrue(
            CommunityPostLike.objects.filter(
                user=self.user,
                post=self.post,
            ).exists()
        )

    def test_like_increments_post_likes_count(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.likes_count,
            1,
        )

    def test_user_cannot_like_same_post_twice(self):
        self.client.force_authenticate(user=self.user)

        first_response = self.client.post(self.url)

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        second_response = self.client.post(self.url)

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.likes_count,
            1,
        )

    def test_user_can_unlike_post(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(self.url)

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(response.data["liked"])
        self.assertEqual(response.data["likes_count"], 0)

        self.assertFalse(
            CommunityPostLike.objects.filter(
                user=self.user,
                post=self.post,
            ).exists()
        )

    def test_unlike_decrements_post_likes_count(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(self.url)

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.likes_count,
            1,
        )

        self.client.delete(self.url)

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.likes_count,
            0,
        )

    def test_unlike_without_existing_like_is_idempotent(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(response.data["liked"])
        self.assertEqual(response.data["likes_count"], 0)

    def test_different_users_can_like_same_post(self):
        self.client.force_authenticate(user=self.user)

        first_response = self.client.post(self.url)

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.force_authenticate(user=self.other_user)

        second_response = self.client.post(self.url)

        self.assertEqual(
            second_response.status_code,
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

    def test_cannot_like_hidden_post(self):
        self.post.status = CommunityPost.Status.HIDDEN
        self.post.save(update_fields=["status"])

        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_cannot_like_removed_post(self):
        self.post.status = CommunityPost.Status.REMOVED
        self.post.save(update_fields=["status"])

        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )


class CommunityPostCommentLikeAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="comment_liker",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="another_liker",
            password="testpass123",
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
            "music_api:community-comment-like",
            kwargs={"pk": self.comment.id},
        )

    def test_anonymous_user_cannot_like_comment(self):
        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            CommunityPostCommentLike.objects.filter(
                comment=self.comment,
            ).exists()
        )

    def test_authenticated_user_can_like_comment(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(response.data["liked"])
        self.assertEqual(response.data["likes_count"], 1)

        self.assertTrue(
            CommunityPostCommentLike.objects.filter(
                user=self.user,
                comment=self.comment,
            ).exists()
        )

    def test_liking_comment_increments_likes_count(self):
        self.client.force_authenticate(user=self.user)

        self.assertEqual(self.comment.likes_count, 0)

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.comment.refresh_from_db()

        self.assertEqual(self.comment.likes_count, 1)
        self.assertEqual(response.data["likes_count"], 1)

    def test_duplicate_like_is_rejected(self):
        self.client.force_authenticate(user=self.user)

        first_response = self.client.post(self.url)

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        second_response = self.client.post(self.url)

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.comment.refresh_from_db()

        self.assertEqual(self.comment.likes_count, 1)

        self.assertEqual(
            CommunityPostCommentLike.objects.filter(
                user=self.user,
                comment=self.comment,
            ).count(),
            1,
        )

    def test_authenticated_user_can_unlike_comment(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(self.url)

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(response.data["liked"])

        self.assertFalse(
            CommunityPostCommentLike.objects.filter(
                user=self.user,
                comment=self.comment,
            ).exists()
        )

    def test_unliking_comment_decrements_likes_count(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(self.url)

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.likes_count, 1)

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.comment.refresh_from_db()

        self.assertEqual(self.comment.likes_count, 0)
        self.assertEqual(response.data["likes_count"], 0)

    def test_unliking_without_existing_like_is_idempotent(self):
        self.client.force_authenticate(user=self.user)

        self.assertEqual(self.comment.likes_count, 0)

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(response.data["liked"])
        self.assertEqual(response.data["likes_count"], 0)

        self.assertEqual(
            CommunityPostCommentLike.objects.filter(
                comment=self.comment,
            ).count(),
            0,
        )

    def test_multiple_users_can_like_same_comment(self):
        self.client.force_authenticate(user=self.user)

        first_response = self.client.post(self.url)

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.force_authenticate(user=self.other_user)

        second_response = self.client.post(self.url)

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.comment.refresh_from_db()

        self.assertEqual(self.comment.likes_count, 2)

        self.assertEqual(
            CommunityPostCommentLike.objects.filter(
                comment=self.comment,
            ).count(),
            2,
        )

    def test_hidden_comment_cannot_be_liked(self):
        self.comment.status = CommunityPostComment.Status.HIDDEN
        self.comment.save(update_fields=["status"])

        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            CommunityPostCommentLike.objects.filter(
                comment=self.comment,
            ).exists()
        )

    def test_comment_on_hidden_post_cannot_be_liked(self):
        self.post.status = CommunityPost.Status.HIDDEN
        self.post.save(update_fields=["status"])

        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            CommunityPostCommentLike.objects.filter(
                comment=self.comment,
            ).exists()
        )


class CommunityPostReportAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="reporter",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="another_reporter",
            password="testpass123",
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
            status.HTTP_403_FORBIDDEN,
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
        )

        self.other_user = User.objects.create_user(
            username="another_comment_reporter",
            password="testpass123",
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
            status.HTTP_403_FORBIDDEN,
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