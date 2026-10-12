from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from music.models import (
    Artist,
    ArtistFollow,
    MusicFeedInteraction,
    UserFollow,
)


User = get_user_model()


# ============================================================
# ARTIST FOLLOWS
# ============================================================

class ArtistFollowAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="artist_follower",
            password="testpass123",
            email="artist_follower@example.com",
        )

        self.other_user = User.objects.create_user(
            username="another_artist_follower",
            password="testpass123",
            email="another_artist_follower@example.com",
        )

        self.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        self.inactive_artist = Artist.objects.create(
            name="Inactive Artist",
            slug="inactive-artist",
            is_active=False,
        )

        self.url = reverse(
            "music_api:artist-follow",
            kwargs={"pk": self.artist.id},
        )

        self.inactive_url = reverse(
            "music_api:artist-follow",
            kwargs={"pk": self.inactive_artist.id},
        )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    def test_anonymous_user_cannot_follow_artist(self):
        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_follow_artist(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            ArtistFollow.objects.filter(
                user=self.user,
                artist=self.artist,
            ).exists()
        )

    def test_follow_records_artist_interaction(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.FOLLOW_ARTIST
                ),
                artist=self.artist,
            ).count(),
            1,
        )

    def test_follow_response_contains_follow_data(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertIn(
            "following",
            response.data,
        )

        self.assertIn(
            "followers_count",
            response.data,
        )

        self.assertIn(
            "follow",
            response.data,
        )

        self.assertTrue(
            response.data["following"],
        )

    def test_follow_increments_followers_count(self):
        self.client.force_authenticate(
            user=self.user,
        )

        self.assertEqual(
            self.artist.followers_count,
            0,
        )

        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.artist.refresh_from_db()

        self.assertEqual(
            self.artist.followers_count,
            1,
        )

        self.assertEqual(
            response.data["followers_count"],
            1,
        )

    def test_duplicate_artist_follow_is_rejected(self):
        self.client.force_authenticate(
            user=self.user,
        )

        first_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        second_response = self.client.post(
            self.url,
            {},
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

    def test_duplicate_artist_follow_does_not_record_second_interaction(
        self,
    ):
        self.client.force_authenticate(
            user=self.user,
        )

        first_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        second_response = self.client.post(
            self.url,
            {},
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
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.FOLLOW_ARTIST
                ),
                artist=self.artist,
            ).count(),
            1,
        )

    def test_inactive_artist_cannot_be_followed(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.post(
            self.inactive_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_inactive_artist_does_not_record_interaction(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.post(
            self.inactive_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.FOLLOW_ARTIST
                ),
                artist=self.inactive_artist,
            ).exists()
        )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    def test_authenticated_user_can_unfollow_artist(self):
        self.client.force_authenticate(
            user=self.user,
        )

        self.client.post(
            self.url,
            {},
            format="json",
        )

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            ArtistFollow.objects.filter(
                user=self.user,
                artist=self.artist,
            ).exists()
        )

    def test_unfollow_does_not_record_interaction(self):
        self.client.force_authenticate(
            user=self.user,
        )

        self.client.post(
            self.url,
            {},
            format="json",
        )

        self.client.delete(
            self.url,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.FOLLOW_ARTIST
                ),
                artist=self.artist,
            ).count(),
            1,
        )

    def test_unfollow_decrements_followers_count(self):
        self.client.force_authenticate(
            user=self.user,
        )

        self.client.post(
            self.url,
            {},
            format="json",
        )

        self.artist.refresh_from_db()

        self.assertEqual(
            self.artist.followers_count,
            1,
        )

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.artist.refresh_from_db()

        self.assertEqual(
            self.artist.followers_count,
            0,
        )

    def test_unfollow_without_existing_follow_is_idempotent(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            response.data["following"],
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.FOLLOW_ARTIST
                ),
                artist=self.artist,
            ).count(),
            0,
        )

    def test_can_follow_artist_again_after_unfollowing(self):
        self.client.force_authenticate(
            user=self.user,
        )

        first_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.delete(
            self.url,
        )

        second_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.artist.refresh_from_db()

        self.assertEqual(
            self.artist.followers_count,
            1,
        )

    def test_refollowing_artist_records_new_interaction(self):
        self.client.force_authenticate(
            user=self.user,
        )

        first_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.delete(
            self.url,
        )

        second_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.FOLLOW_ARTIST
                ),
                artist=self.artist,
            ).count(),
            2,
        )

    def test_anonymous_user_cannot_unfollow_artist(self):
        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_different_users_can_follow_same_artist(self):
        self.client.force_authenticate(
            user=self.user,
        )

        first_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.client.force_authenticate(
            user=self.other_user,
        )

        second_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.artist.refresh_from_db()

        self.assertEqual(
            self.artist.followers_count,
            2,
        )

    def test_different_users_create_separate_artist_follow_interactions(
        self,
    ):
        self.client.force_authenticate(
            user=self.user,
        )

        first_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.client.force_authenticate(
            user=self.other_user,
        )

        second_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            MusicFeedInteraction.objects.filter(
                interaction_type=(
                    MusicFeedInteraction.InteractionType.FOLLOW_ARTIST
                ),
                artist=self.artist,
            ).count(),
            2,
        )

        self.assertTrue(
            MusicFeedInteraction.objects.filter(
                user=self.user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.FOLLOW_ARTIST
                ),
                artist=self.artist,
            ).exists()
        )

        self.assertTrue(
            MusicFeedInteraction.objects.filter(
                user=self.other_user,
                interaction_type=(
                    MusicFeedInteraction.InteractionType.FOLLOW_ARTIST
                ),
                artist=self.artist,
            ).exists()
        )

    def test_unfollowing_only_removes_current_users_follow(self):
        self.client.force_authenticate(
            user=self.user,
        )

        self.client.post(
            self.url,
            {},
            format="json",
        )

        self.client.force_authenticate(
            user=self.other_user,
        )

        self.client.post(
            self.url,
            {},
            format="json",
        )

        self.client.delete(
            self.url,
        )

        self.assertFalse(
            ArtistFollow.objects.filter(
                user=self.other_user,
                artist=self.artist,
            ).exists()
        )

        self.assertTrue(
            ArtistFollow.objects.filter(
                user=self.user,
                artist=self.artist,
            ).exists()
        )

        self.artist.refresh_from_db()

        self.assertEqual(
            self.artist.followers_count,
            1,
        )


# ============================================================
# USER FOLLOWS
# ============================================================

class UserFollowAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="follower",
            password="testpass123",
            email="follower@example.com",
        )

        self.other_user = User.objects.create_user(
            username="following_user",
            password="testpass123",
            email="following_user@example.com",
        )

        self.third_user = User.objects.create_user(
            username="third_user",
            password="testpass123",
            email="third_user@example.com",
        )

        self.url = reverse(
            "music_api:user-follow",
            kwargs={"pk": self.other_user.id},
        )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    def test_anonymous_user_cannot_follow_user(self):
        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_follow_user(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            UserFollow.objects.filter(
                follower=self.user,
                following=self.other_user,
            ).exists()
        )

    def test_follow_response_contains_follow_data(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertIn(
            "following",
            response.data,
        )

        self.assertIn(
            "follow",
            response.data,
        )

        self.assertTrue(
            response.data["following"],
        )

    def test_duplicate_user_follow_is_rejected(self):
        self.client.force_authenticate(
            user=self.user,
        )

        first_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        second_response = self.client.post(
            self.url,
            {},
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

    def test_user_cannot_follow_themselves(self):
        self.client.force_authenticate(
            user=self.user,
        )

        self_url = reverse(
            "music_api:user-follow",
            kwargs={"pk": self.user.id},
        )

        response = self.client.post(
            self_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    def test_authenticated_user_can_unfollow_user(self):
        self.client.force_authenticate(
            user=self.user,
        )

        self.client.post(
            self.url,
            {},
            format="json",
        )

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            UserFollow.objects.filter(
                follower=self.user,
                following=self.other_user,
            ).exists()
        )

    def test_unfollow_without_existing_follow_is_idempotent(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            response.data["following"],
        )

    def test_can_follow_user_again_after_unfollowing(self):
        self.client.force_authenticate(
            user=self.user,
        )

        first_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.delete(
            self.url,
        )

        second_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_anonymous_user_cannot_unfollow_user(self):
        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_different_users_can_follow_same_user(self):
        self.client.force_authenticate(
            user=self.user,
        )

        first_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.client.force_authenticate(
            user=self.third_user,
        )

        second_response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            UserFollow.objects.filter(
                following=self.other_user,
            ).count(),
            2,
        )

    def test_unfollowing_only_removes_current_users_follow(self):
        self.client.force_authenticate(
            user=self.user,
        )

        self.client.post(
            self.url,
            {},
            format="json",
        )

        self.client.force_authenticate(
            user=self.third_user,
        )

        self.client.post(
            self.url,
            {},
            format="json",
        )

        self.client.delete(
            self.url,
        )

        self.assertFalse(
            UserFollow.objects.filter(
                follower=self.third_user,
                following=self.other_user,
            ).exists()
        )

        self.assertTrue(
            UserFollow.objects.filter(
                follower=self.user,
                following=self.other_user,
            ).exists()
        )