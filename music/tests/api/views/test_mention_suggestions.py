from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from music.models import UserFollow, UserMention


User = get_user_model()


class MentionSuggestionsAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="mention_user",
            email="mentionuser@example.com",
            password="testpass123",
            onboarding_completed=True,
        )

        self.following_user = User.objects.create_user(
            username="victor_music",
            email="victormusic@example.com",
            password="testpass123",
            display_name="Victor Music",
            onboarding_completed=True,
        )

        self.follower_user = User.objects.create_user(
            username="music_fan",
            email="musicfan@example.com",
            password="testpass123",
            display_name="Victor Fan",
            onboarding_completed=True,
        )

        self.unconnected_user = User.objects.create_user(
            username="victor_unconnected",
            email="victorunconnected@example.com",
            password="testpass123",
            display_name="Victor Unconnected",
            onboarding_completed=True,
        )

        UserFollow.objects.create(
            follower=self.user,
            following=self.following_user,
        )

        UserFollow.objects.create(
            follower=self.follower_user,
            following=self.user,
        )

        self.url = reverse(
            "music_api:mention-suggestions",
        )

    def authenticate(self, user=None):
        self.client.force_authenticate(
            user=user or self.user,
        )

    def create_mention(
        self,
        mentioned_user,
        object_id,
        created_at=None,
    ):
        content_type = ContentType.objects.get_for_model(User)

        mention = UserMention.objects.create(
            mentioner=self.user,
            mentioned_user=mentioned_user,
            content_type=content_type,
            object_id=str(object_id),
        )

        if created_at is not None:
            UserMention.objects.filter(
                pk=mention.pk,
            ).update(
                created_at=created_at,
            )

        return mention

    # ========================================================
    # AUTHENTICATION AND PERMISSIONS
    # ========================================================

    def test_anonymous_user_cannot_get_mention_suggestions(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_incomplete_user_cannot_get_mention_suggestions(self):
        incomplete_user = User.objects.create_user(
            username="incomplete_user",
            email="incomplete@example.com",
            password="testpass123",
            onboarding_completed=False,
        )

        self.authenticate(incomplete_user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_staff_user_cannot_get_mention_suggestions(self):
        staff_user = User.objects.create_superuser(
            username="mention_staff",
            email="mentionstaff@example.com",
            password="testpass123",
        )

        staff_user.is_superuser = False
        staff_user.save(update_fields=["is_superuser"])

        self.authenticate(staff_user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_superuser_cannot_get_mention_suggestions(self):
        superuser = User.objects.create_superuser(
            username="mention_superuser",
            email="mentionsuperuser@example.com",
            password="testpass123",
        )

        self.authenticate(superuser)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ========================================================
    # RECENT MENTIONS
    # ========================================================

    def test_empty_query_returns_recently_mentioned_users(self):
        self.create_mention(
            self.following_user,
            object_id=1,
        )

        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            response.data["results"][0]["id"],
            self.following_user.id,
        )

    def test_recent_mentions_are_ordered_by_latest_mention(self):
        now = timezone.now()

        self.create_mention(
            self.following_user,
            object_id=1,
            created_at=now - timedelta(hours=2),
        )

        self.create_mention(
            self.follower_user,
            object_id=2,
            created_at=now - timedelta(hours=1),
        )

        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        result_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertEqual(
            result_ids,
            [
                self.follower_user.id,
                self.following_user.id,
            ],
        )

    def test_recent_mentions_do_not_return_duplicate_users(self):
        self.create_mention(
            self.following_user,
            object_id=1,
        )

        self.create_mention(
            self.following_user,
            object_id=2,
        )

        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        result_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertEqual(
            result_ids,
            [self.following_user.id],
        )

    def test_recent_mentions_are_limited_to_five_users(self):
        mentioned_users = []

        for index in range(7):
            mentioned_user = User.objects.create_user(
                username=f"recent_user_{index}",
                email=f"recent{index}@example.com",
                password="testpass123",
                onboarding_completed=True,
            )

            mentioned_users.append(mentioned_user)

            self.create_mention(
                mentioned_user,
                object_id=index + 1,
                created_at=timezone.now() + timedelta(
                    seconds=index,
                ),
            )

        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["results"]),
            5,
        )

        result_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        expected_ids = [
            user.id
            for user in reversed(mentioned_users[-5:])
        ]

        self.assertEqual(
            result_ids,
            expected_ids,
        )

    def test_recent_mentions_exclude_inactive_and_staff_users(self):
        inactive_user = User.objects.create_user(
            username="inactive_mentioned",
            email="inactivementioned@example.com",
            password="testpass123",
            is_active=False,
            onboarding_completed=True,
        )

        staff_user = User.objects.create_superuser(
            username="staff_mentioned",
            email="staffmentioned@example.com",
            password="testpass123",
        )

        self.create_mention(
            inactive_user,
            object_id=1,
        )

        self.create_mention(
            staff_user,
            object_id=2,
        )

        self.create_mention(
            self.following_user,
            object_id=3,
        )

        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        result_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertEqual(
            result_ids,
            [self.following_user.id],
        )

    # ========================================================
    # NETWORK SEARCH
    # ========================================================

    def test_search_matches_username_prefix(self):
        self.authenticate()

        response = self.client.get(
            self.url,
            {"q": "victor"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        result_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertIn(
            self.following_user.id,
            result_ids,
        )

    def test_search_matches_display_name_prefix(self):
        self.authenticate()

        response = self.client.get(
            self.url,
            {"q": "victor"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        result_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertIn(
            self.follower_user.id,
            result_ids,
        )

    def test_search_is_case_insensitive(self):
        self.authenticate()

        response = self.client.get(
            self.url,
            {"q": "VICTOR"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        result_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertIn(
            self.following_user.id,
            result_ids,
        )

        self.assertIn(
            self.follower_user.id,
            result_ids,
        )

    def test_search_accepts_query_with_at_prefix(self):
        self.authenticate()

        response = self.client.get(
            self.url,
            {"q": "@victor"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        result_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertIn(
            self.following_user.id,
            result_ids,
        )

    def test_search_includes_followers_and_following(self):
        self.authenticate()

        response = self.client.get(
            self.url,
            {"q": "victor"},
        )

        result_ids = {
            item["id"]
            for item in response.data["results"]
        }

        self.assertIn(
            self.following_user.id,
            result_ids,
        )

        self.assertIn(
            self.follower_user.id,
            result_ids,
        )

    def test_search_excludes_users_outside_network(self):
        self.authenticate()

        response = self.client.get(
            self.url,
            {"q": "victor"},
        )

        result_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertNotIn(
            self.unconnected_user.id,
            result_ids,
        )

    def test_search_excludes_inactive_and_staff_users(self):
        inactive_user = User.objects.create_user(
            username="victor_inactive",
            email="victorinactive@example.com",
            password="testpass123",
            is_active=False,
            onboarding_completed=True,
        )

        staff_user = User.objects.create_superuser(
            username="victor_staff",
            email="victorstaff@example.com",
            password="testpass123",
        )

        UserFollow.objects.create(
            follower=self.user,
            following=inactive_user,
        )

        UserFollow.objects.create(
            follower=self.user,
            following=staff_user,
        )

        self.authenticate()

        response = self.client.get(
            self.url,
            {"q": "victor"},
        )

        result_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertNotIn(
            inactive_user.id,
            result_ids,
        )

        self.assertNotIn(
            staff_user.id,
            result_ids,
        )

    def test_search_excludes_current_user(self):
        self.user.username = "victor_self"
        self.user.save(update_fields=["username"])

        self.authenticate()

        response = self.client.get(
            self.url,
            {"q": "victor"},
        )

        result_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertNotIn(
            self.user.id,
            result_ids,
        )

    def test_search_returns_at_most_five_users(self):
        for index in range(8):
            suggested_user = User.objects.create_user(
                username=f"victor_{index}",
                email=f"victor{index}@example.com",
                password="testpass123",
                onboarding_completed=True,
            )

            UserFollow.objects.create(
                follower=self.user,
                following=suggested_user,
            )

        self.authenticate()

        response = self.client.get(
            self.url,
            {"q": "victor"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertLessEqual(
            len(response.data["results"]),
            5,
        )

    def test_search_response_contains_only_public_suggestion_fields(self):
        self.authenticate()

        response = self.client.get(
            self.url,
            {"q": "victor"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            response.data["results"],
        )

        expected_fields = {
            "id",
            "username",
            "display_name",
            "profile_image",
            "is_verified",
            "is_identity_verified",
        }

        self.assertEqual(
            set(response.data["results"][0].keys()),
            expected_fields,
        )
