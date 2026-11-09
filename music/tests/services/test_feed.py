
from __future__ import annotations

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from music.models import (
    Artist,
    ArtistFollow,
    CommunityPost,
    CommunityPostComment,
    CommunityPostFavorite,
    CommunityPostLike,
    CommunityPostTarget,
    MusicFeedInteraction,
    UserFollow,
)
from music.services.feed import (
    FeedCandidate,
    MusicFeedService,
)


User = get_user_model()


class MusicFeedServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.service = MusicFeedService()

        cls.user = User.objects.create_user(
            username="feed_user",
            email="feed_user@example.com",
            password="password",
        )

        cls.other_user = User.objects.create_user(
            username="other_user",
            email="other_user@example.com",
            password="password",
        )

        cls.third_user = User.objects.create_user(
            username="third_user",
            email="third_user@example.com",
            password="password",
        )

        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            is_active=True,
        )

        cls.other_artist = Artist.objects.create(
            name="Other Artist",
            slug="other-artist",
            is_active=True,
        )

    # ============================================================
    # HELPERS
    # ============================================================

    @classmethod
    def create_community_post(
        cls,
        user=None,
        content="Test community post",
        status=None,
        created_at=None,
        artist=None,
        **kwargs,
    ):
        """
        Create a community post with a unique slug.

        Optional artist attachment is created through
        CommunityPostTarget.

        created_at is applied after creating the post so tests
        can control feed ordering.
        """

        post_status = (
            status
            if status is not None
            else CommunityPost.Status.PUBLISHED
        )

        post = CommunityPost.objects.create(
            user=user or cls.other_user,
            content=content,
            status=post_status,
            slug=f"test-post-{uuid.uuid4().hex}",
        )

        if created_at is not None:
            CommunityPost.objects.filter(
                pk=post.pk,
            ).update(
                created_at=created_at,
            )

            post.refresh_from_db()

        if artist is not None:
            CommunityPostTarget.objects.create(
                post=post,
                target_type=CommunityPostTarget.TargetType.ARTIST,
                artist=artist,
            )

        return post

    @staticmethod
    def create_interaction(
        *,
        user,
        interaction_type,
        song=None,
        album=None,
        artist=None,
        community_post=None,
        created_at=None,
    ):
        interaction = MusicFeedInteraction.objects.create(
            user=user,
            interaction_type=interaction_type,
            song=song,
            album=album,
            artist=artist,
            community_post=community_post,
        )

        if created_at is not None:
            MusicFeedInteraction.objects.filter(
                pk=interaction.pk,
            ).update(
                created_at=created_at,
            )

            interaction.refresh_from_db()

        return interaction

    @staticmethod
    def get_post_ids(results):
        return [
            candidate.object_id
            for candidate in results
            if candidate.content_type == "community_post"
        ]

    @staticmethod
    def get_post_candidate(results, post_id):
        return next(
            (
                candidate
                for candidate in results
                if (
                    candidate.content_type == "community_post"
                    and candidate.object_id == post_id
                )
            ),
            None,
        )

    @staticmethod
    def get_unpublished_community_status():
        published_value = CommunityPost.Status.PUBLISHED

        for value, _label in CommunityPost.Status.choices:
            if value != published_value:
                return value

        raise AssertionError(
            "CommunityPost.Status must define at least one "
            "non-published status for this test."
        )

    # ============================================================
    # BASIC COMMUNITY FEED BEHAVIOR
    # ============================================================

    def test_anonymous_feed_returns_community_posts(self):
        post = self.create_community_post(
            content="Public community post",
        )

        result = self.service.get_feed(
            user=None,
            limit=20,
        )

        self.assertIn(
            post.id,
            self.get_post_ids(result["results"]),
        )

    def test_authenticated_feed_returns_community_posts(self):
        post = self.create_community_post(
            content="Authenticated community post",
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        self.assertIn(
            post.id,
            self.get_post_ids(result["results"]),
        )

    def test_feed_returns_only_community_posts(self):
        self.create_community_post(
            content="First community post",
        )

        self.create_community_post(
            content="Second community post",
            user=self.third_user,
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        self.assertTrue(result["results"])

        for candidate in result["results"]:
            self.assertEqual(
                candidate.content_type,
                "community_post",
            )

    def test_feed_does_not_return_standalone_music_entities(self):
        self.create_community_post(
            content="Community-only result",
            artist=self.artist,
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        content_types = {
            candidate.content_type
            for candidate in result["results"]
        }

        self.assertEqual(
            content_types,
            {"community_post"},
        )

    def test_limit_is_respected(self):
        for index in range(10):
            self.create_community_post(
                content=f"Community post {index}",
                user=(
                    self.other_user
                    if index % 2 == 0
                    else self.third_user
                ),
            )

        result = self.service.get_feed(
            user=None,
            limit=3,
        )

        self.assertLessEqual(
            len(result["results"]),
            3,
        )

    def test_limit_is_capped(self):
        for index in range(60):
            self.create_community_post(
                content=f"Community post {index}",
                user=(
                    self.other_user
                    if index % 2 == 0
                    else self.third_user
                ),
            )

        result = self.service.get_feed(
            user=None,
            limit=1000,
        )

        self.assertLessEqual(
            len(result["results"]),
            MusicFeedService.MAX_LIMIT,
        )

    # ============================================================
    # PUBLISHED CONTENT
    # ============================================================

    def test_unpublished_community_post_is_excluded(self):
        unpublished_status = (
            self.get_unpublished_community_status()
        )

        post = self.create_community_post(
            content="Unpublished post",
            status=unpublished_status,
        )

        result = self.service.get_feed(
            user=None,
            limit=20,
        )

        self.assertNotIn(
            post.id,
            self.get_post_ids(result["results"]),
        )

    def test_recent_published_post_is_included(self):
        post = self.create_community_post(
            content="Fresh community thought",
        )

        result = self.service.get_feed(
            user=None,
            limit=20,
        )

        self.assertIn(
            post.id,
            self.get_post_ids(result["results"]),
        )

    # ============================================================
    # USER FOLLOWING
    # ============================================================

    def test_followed_user_post_gets_personalization_boost(self):
        UserFollow.objects.create(
            follower=self.user,
            following=self.other_user,
        )

        followed_post = self.create_community_post(
            user=self.other_user,
            content="Post from followed user",
        )

        unrelated_post = self.create_community_post(
            user=self.third_user,
            content="Post from unrelated user",
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        followed_candidate = self.get_post_candidate(
            result["results"],
            followed_post.id,
        )

        unrelated_candidate = self.get_post_candidate(
            result["results"],
            unrelated_post.id,
        )

        self.assertIsNotNone(followed_candidate)
        self.assertIsNotNone(unrelated_candidate)

        self.assertGreater(
            followed_candidate.score,
            unrelated_candidate.score,
        )

    def test_mutual_user_post_gets_mutual_source(self):
        UserFollow.objects.create(
            follower=self.user,
            following=self.other_user,
        )

        UserFollow.objects.create(
            follower=self.other_user,
            following=self.user,
        )

        mutual_post = self.create_community_post(
            user=self.other_user,
            content="Mutual user's post",
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        candidate = self.get_post_candidate(
            result["results"],
            mutual_post.id,
        )

        self.assertIsNotNone(candidate)

        self.assertEqual(
            candidate.source,
            "mutual",
        )

    # ============================================================
    # FOLLOWED ARTIST CONTEXT
    # ============================================================

    def test_followed_artist_post_is_added_to_feed(self):
        ArtistFollow.objects.create(
            user=self.user,
            artist=self.artist,
        )

        post = self.create_community_post(
            content="Discussion about a followed artist",
            artist=self.artist,
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        candidate = self.get_post_candidate(
            result["results"],
            post.id,
        )

        self.assertIsNotNone(candidate)

        self.assertEqual(
            candidate.source,
            "followed_artist",
        )

    def test_followed_artist_attachment_gets_personalization_boost(self):
        ArtistFollow.objects.create(
            user=self.user,
            artist=self.artist,
        )

        followed_artist_post = self.create_community_post(
            content="Talking about my followed artist",
            artist=self.artist,
        )

        unrelated_artist_post = self.create_community_post(
            content="Talking about another artist",
            user=self.third_user,
            artist=self.other_artist,
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        followed_candidate = self.get_post_candidate(
            result["results"],
            followed_artist_post.id,
        )

        unrelated_candidate = self.get_post_candidate(
            result["results"],
            unrelated_artist_post.id,
        )

        self.assertIsNotNone(followed_candidate)
        self.assertIsNotNone(unrelated_candidate)

        self.assertGreater(
            followed_candidate.score,
            unrelated_candidate.score,
        )

    def test_artist_attachment_does_not_create_standalone_feed_item(self):
        ArtistFollow.objects.create(
            user=self.user,
            artist=self.artist,
        )

        post = self.create_community_post(
            content="Artist discussion",
            artist=self.artist,
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        self.assertIn(
            post.id,
            self.get_post_ids(result["results"]),
        )

        for candidate in result["results"]:
            self.assertEqual(
                candidate.content_type,
                "community_post",
            )

    # ============================================================
    # INTERACTION HISTORY
    # ============================================================

    def test_community_post_interaction_is_loaded_into_context(self):
        post = self.create_community_post(
            content="Previously viewed post",
        )

        self.create_interaction(
            user=self.user,
            interaction_type=(
                MusicFeedInteraction.InteractionType.VIEW_COMMUNITY_POST
            ),
            community_post=post,
            created_at=timezone.now(),
        )

        context = self.service._build_user_context(
            user=self.user,
            candidates=[
                FeedCandidate(
                    content_type="community_post",
                    source="recent",
                    object=post,
                )
            ],
        )

        self.assertIn(
            post.id,
            context.interacted_community_post_ids,
        )

    def test_old_community_interaction_is_ignored(self):
        post = self.create_community_post(
            content="Old interaction post",
        )

        self.create_interaction(
            user=self.user,
            interaction_type=(
                MusicFeedInteraction.InteractionType.VIEW_COMMUNITY_POST
            ),
            community_post=post,
            created_at=(
                timezone.now() - timedelta(days=120)
            ),
        )

        context = self.service._build_user_context(
            user=self.user,
            candidates=[
                FeedCandidate(
                    content_type="community_post",
                    source="recent",
                    object=post,
                )
            ],
        )

        self.assertNotIn(
            post.id,
            context.interacted_community_post_ids,
        )

    def test_generated_candidates_contain_only_community_posts(self):
        post = self.create_community_post(
            content="Normal community post",
        )

        candidates = self.service._generate_candidates(
            user=self.user,
            candidate_limit=20,
        )

        self.assertIn(
            post.id,
            self.get_post_ids(candidates),
        )

        for candidate in candidates:
            self.assertEqual(
                candidate.content_type,
                "community_post",
            )

    # ============================================================
    # ENGAGEMENT SIGNALS
    # ============================================================

    def test_liked_community_post_gets_penalty(self):
        liked_post = self.create_community_post(
            user=self.other_user,
            content="Already liked",
        )

        other_post = self.create_community_post(
            user=self.third_user,
            content="Not liked",
        )

        CommunityPostLike.objects.create(
            user=self.user,
            post=liked_post,
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        liked_candidate = self.get_post_candidate(
            result["results"],
            liked_post.id,
        )

        other_candidate = self.get_post_candidate(
            result["results"],
            other_post.id,
        )

        self.assertIsNotNone(liked_candidate)
        self.assertIsNotNone(other_candidate)

        self.assertLess(
            liked_candidate.score,
            other_candidate.score,
        )

    def test_favorited_community_post_gets_penalty(self):
        favorited_post = self.create_community_post(
            user=self.other_user,
            content="Already favorited",
        )

        other_post = self.create_community_post(
            user=self.third_user,
            content="Not favorited",
        )

        CommunityPostFavorite.objects.create(
            user=self.user,
            post=favorited_post,
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        favorited_candidate = self.get_post_candidate(
            result["results"],
            favorited_post.id,
        )

        other_candidate = self.get_post_candidate(
            result["results"],
            other_post.id,
        )

        self.assertIsNotNone(favorited_candidate)
        self.assertIsNotNone(other_candidate)

        self.assertLess(
            favorited_candidate.score,
            other_candidate.score,
        )

    def test_commented_community_post_gets_penalty(self):
        commented_post = self.create_community_post(
            user=self.other_user,
            content="Already commented",
        )

        other_post = self.create_community_post(
            user=self.third_user,
            content="Not commented",
        )

        CommunityPostComment.objects.create(
            user=self.user,
            post=commented_post,
            content="Interesting post",
            status=CommunityPostComment.Status.PUBLISHED,
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        commented_candidate = self.get_post_candidate(
            result["results"],
            commented_post.id,
        )

        other_candidate = self.get_post_candidate(
            result["results"],
            other_post.id,
        )

        self.assertIsNotNone(commented_candidate)
        self.assertIsNotNone(other_candidate)

        self.assertLess(
            commented_candidate.score,
            other_candidate.score,
        )

    # ============================================================
    # CREATOR AFFINITY
    # ============================================================

    def test_engaged_creator_gets_personalization_boost(self):
        engaged_creator_post = self.create_community_post(
            user=self.other_user,
            content="Previously engaged creator",
        )

        unrelated_creator_post = self.create_community_post(
            user=self.third_user,
            content="Unrelated creator",
        )

        # Establish creator affinity without liking either candidate post.
        previous_post = self.create_community_post(
            user=self.other_user,
            content="Previously engaged post",
        )

        CommunityPostLike.objects.create(
            user=self.user,
            post=previous_post,
        )

        candidates = [
            FeedCandidate(
                content_type="community_post",
                source="recent",
                object=engaged_creator_post,
            ),
            FeedCandidate(
                content_type="community_post",
                source="recent",
                object=unrelated_creator_post,
            ),
        ]

        context = self.service._build_user_context(
            user=self.user,
            candidates=candidates,
        )

        engaged_candidate = candidates[0]
        unrelated_candidate = candidates[1]

        engaged_personalization = (
            self.service._personalization_score(
                candidate=engaged_candidate,
                context=context,
            )
        )

        unrelated_personalization = (
            self.service._personalization_score(
                candidate=unrelated_candidate,
                context=context,
            )
        )

        self.assertIn(
            self.other_user.id,
            context.engaged_creator_ids,
        )

        self.assertGreater(
            engaged_personalization,
            unrelated_personalization,
        )

        self.assertEqual(
            engaged_personalization - unrelated_personalization,
            12.0,
        )

    # ============================================================
    # NEWLY PUBLISHED POST PRIORITY
    # ============================================================

    def test_own_newly_published_post_appears_first(self):
        older_post = self.create_community_post(
            user=self.other_user,
            content="Older community post",
            created_at=timezone.now() - timedelta(days=2),
        )

        new_post = self.create_community_post(
            user=self.user,
            content="My newly published post",
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
            new_post_id=new_post.id,
        )

        self.assertTrue(result["results"])

        first_candidate = result["results"][0]

        self.assertEqual(
            first_candidate.object_id,
            new_post.id,
        )

        self.assertEqual(
            first_candidate.source,
            "just_published",
        )

        self.assertIn(
            older_post.id,
            self.get_post_ids(result["results"]),
        )

    def test_another_users_post_does_not_receive_priority(self):
        another_users_post = self.create_community_post(
            user=self.other_user,
            content="Not my post",
            created_at=timezone.now() - timedelta(days=2),
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
            new_post_id=another_users_post.id,
        )

        candidate = self.get_post_candidate(
            result["results"],
            another_users_post.id,
        )

        self.assertIsNotNone(candidate)

        self.assertNotEqual(
            candidate.source,
            "just_published",
        )

    def test_unpublished_post_does_not_receive_priority(self):
        post = self.create_community_post(
            user=self.user,
            content="Not published",
            status=self.get_unpublished_community_status(),
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
            new_post_id=post.id,
        )

        self.assertNotIn(
            post.id,
            self.get_post_ids(result["results"]),
        )

    def test_anonymous_user_cannot_prioritize_a_post(self):
        post = self.create_community_post(
            user=self.other_user,
            content="Anonymous priority attempt",
        )

        result = self.service.get_feed(
            user=None,
            limit=20,
            new_post_id=post.id,
        )

        candidate = self.get_post_candidate(
            result["results"],
            post.id,
        )

        self.assertIsNotNone(candidate)

        self.assertNotEqual(
            candidate.source,
            "just_published",
        )

    def test_invalid_new_post_id_is_ignored_by_service(self):
        post = self.create_community_post(
            user=self.user,
            content="Normal post",
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
            new_post_id="invalid",
        )

        candidate = self.get_post_candidate(
            result["results"],
            post.id,
        )

        self.assertIsNotNone(candidate)

        self.assertNotEqual(
            candidate.source,
            "just_published",
        )

    def test_new_post_is_not_returned_twice(self):
        post = self.create_community_post(
            user=self.user,
            content="Prioritized post",
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
            new_post_id=post.id,
        )

        matching_ids = [
            candidate.object_id
            for candidate in result["results"]
            if candidate.object_id == post.id
        ]

        self.assertEqual(
            len(matching_ids),
            1,
        )

    def test_new_post_priority_is_not_permanent(self):
        new_post = self.create_community_post(
            user=self.user,
            content="New post",
            created_at=timezone.now() - timedelta(days=2),
        )

        other_post = self.create_community_post(
            user=self.other_user,
            content="Recent post",
        )

        prioritized_result = self.service.get_feed(
            user=self.user,
            limit=20,
            new_post_id=new_post.id,
        )

        normal_result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        prioritized_candidate = self.get_post_candidate(
            prioritized_result["results"],
            new_post.id,
        )

        normal_candidate = self.get_post_candidate(
            normal_result["results"],
            new_post.id,
        )

        self.assertIsNotNone(prioritized_candidate)
        self.assertIsNotNone(normal_candidate)

        self.assertEqual(
            prioritized_candidate.source,
            "just_published",
        )

        self.assertNotEqual(
            normal_candidate.source,
            "just_published",
        )

        self.assertNotEqual(
            normal_result["results"][0].object_id,
            new_post.id,
        )

        self.assertIn(
            other_post.id,
            self.get_post_ids(normal_result["results"]),
        )

    # ============================================================
    # CURSOR SNAPSHOTS
    # ============================================================

    def test_feed_returns_cursor_when_more_results_exist(self):
        for index in range(3):
            self.create_community_post(
                content=f"Cursor post {index}",
                user=(
                    self.other_user
                    if index % 2 == 0
                    else self.third_user
                ),
            )

        result = self.service.get_feed(
            user=None,
            limit=1,
        )

        self.assertTrue(result["has_more"])
        self.assertIsNotNone(result["next_cursor"])

    def test_cursor_continues_original_snapshot_order(self):
        older_post = self.create_community_post(
            user=self.other_user,
            content="Older post",
            created_at=timezone.now() - timedelta(days=3),
        )

        middle_post = self.create_community_post(
            user=self.third_user,
            content="Middle post",
            created_at=timezone.now() - timedelta(days=2),
        )

        new_post = self.create_community_post(
            user=self.user,
            content="Newly published post",
        )

        first_page = self.service.get_feed(
            user=self.user,
            limit=1,
            new_post_id=new_post.id,
        )

        self.assertEqual(
            first_page["results"][0].object_id,
            new_post.id,
        )

        self.assertTrue(first_page["has_more"])

        second_page = self.service.get_feed(
            user=self.user,
            limit=1,
            cursor=first_page["next_cursor"],
        )

        self.assertEqual(
            len(second_page["results"]),
            1,
        )

        second_post_id = second_page["results"][0].object_id

        self.assertNotEqual(
            second_post_id,
            new_post.id,
        )

        self.assertIn(
            second_post_id,
            {older_post.id, middle_post.id},
        )

    def test_cursor_pages_do_not_repeat_posts(self):
        for index in range(5):
            self.create_community_post(
                content=f"Pagination post {index}",
                user=(
                    self.other_user
                    if index % 2 == 0
                    else self.third_user
                ),
            )

        first_page = self.service.get_feed(
            user=None,
            limit=2,
        )

        self.assertTrue(first_page["has_more"])

        second_page = self.service.get_feed(
            user=None,
            limit=2,
            cursor=first_page["next_cursor"],
        )

        first_ids = set(
            self.get_post_ids(first_page["results"])
        )

        second_ids = set(
            self.get_post_ids(second_page["results"])
        )

        self.assertFalse(
            first_ids.intersection(second_ids)
        )

    def test_cursor_page_does_not_reapply_new_post_priority(self):
        new_post = self.create_community_post(
            user=self.user,
            content="New post",
        )

        for index in range(3):
            self.create_community_post(
                content=f"Other post {index}",
                user=(
                    self.other_user
                    if index % 2 == 0
                    else self.third_user
                ),
            )

        first_page = self.service.get_feed(
            user=self.user,
            limit=1,
            new_post_id=new_post.id,
        )

        self.assertEqual(
            first_page["results"][0].object_id,
            new_post.id,
        )

        self.assertTrue(first_page["has_more"])

        second_page = self.service.get_feed(
            user=self.user,
            limit=1,
            cursor=first_page["next_cursor"],
            new_post_id=new_post.id,
        )

        if second_page["results"]:
            self.assertNotEqual(
                second_page["results"][0].object_id,
                new_post.id,
            )

            self.assertNotEqual(
                second_page["results"][0].source,
                "just_published",
            )

    # ============================================================
    # DEDUPLICATION
    # ============================================================

    def test_same_community_post_is_not_returned_twice(self):
        post = self.create_community_post(
            user=self.other_user,
            content="Duplicate candidate",
            artist=self.artist,
        )

        ArtistFollow.objects.create(
            user=self.user,
            artist=self.artist,
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        matching = [
            candidate
            for candidate in result["results"]
            if candidate.object_id == post.id
        ]

        self.assertEqual(
            len(matching),
            1,
        )

    # ============================================================
    # DIVERSITY
    # ============================================================

    def test_feed_limits_repeated_authors_when_alternatives_exist(self):
        author_a = self.other_user
        author_b = self.third_user

        for index in range(4):
            self.create_community_post(
                user=author_a,
                content=f"Author A post {index}",
                created_at=(
                    timezone.now() - timedelta(minutes=index)
                ),
            )

        for index in range(2):
            self.create_community_post(
                user=author_b,
                content=f"Author B post {index}",
                created_at=(
                    timezone.now() - timedelta(minutes=10 + index)
                ),
            )

        result = self.service.get_feed(
            user=None,
            limit=6,
        )

        returned_posts = result["results"]

        self.assertEqual(
            len(returned_posts),
            6,
        )

        author_ids = [
            candidate.object.user_id
            for candidate in returned_posts
        ]

        self.assertLessEqual(
            author_ids[:3].count(author_a.id),
            2,
        )

    def test_diversity_does_not_duplicate_posts(self):
        for index in range(5):
            self.create_community_post(
                content=f"Diversity post {index}",
                user=(
                    self.other_user
                    if index % 2 == 0
                    else self.third_user
                ),
            )

        result = self.service.get_feed(
            user=None,
            limit=20,
        )

        post_ids = self.get_post_ids(
            result["results"],
        )

        self.assertEqual(
            len(post_ids),
            len(set(post_ids)),
        )
