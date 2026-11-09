
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from music.models import (
    Album,
    Artist,
    CommunityPost,
    EditorialArticle,
    UserFollow,
    Song,
)
from music.services.global_search import GlobalSearchService


User = get_user_model()


class GlobalSearchServiceTests(TestCase):
    def setUp(self):
        self.service = GlobalSearchService()

        self.artist = Artist.objects.create(
            name="Davido",
            slug="davido",
            is_active=True,
        )

        self.user = self.create_user(
            username="davido_fan",
            email="davido@example.com",
            display_name="Davido Fan",
        )

    # ========================================================
    # Test data helpers
    # ========================================================

    def create_user(
        self,
        *,
        username,
        email=None,
        display_name="",
        is_active=True,
        is_staff=False,
        is_superuser=False,
        onboarding_completed=True,
    ):
        user = User.objects.create(
            username=username,
            email=email or f"{username}@example.com",
            display_name=display_name,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
            onboarding_completed=onboarding_completed,
        )

        user.set_password("test-password")
        user.save(update_fields=["password"])

        return user

    def create_song(
        self,
        *,
        title,
        slug,
        artist=None,
        status=Song.Status.PUBLISHED,
    ):
        published_at = (
            timezone.now()
            if status == Song.Status.PUBLISHED
            else None
        )

        song = Song.objects.create(
            title=title,
            slug=slug,
            status=status,
            published_at=published_at,
        )

        if artist is not None:
            song.artists.add(artist)

        return song

    def create_album(
        self,
        *,
        title,
        slug,
        artist=None,
        status=Album.Status.PUBLISHED,
    ):
        published_at = (
            timezone.now()
            if status == Album.Status.PUBLISHED
            else None
        )

        album = Album.objects.create(
            title=title,
            slug=slug,
            status=status,
            published_at=published_at,
        )

        if artist is not None:
            album.artists.add(artist)

        return album

    def create_community_post(
        self,
        *,
        user=None,
        content="Davido is amazing",
        slug="davido-community-post",
        status=CommunityPost.Status.PUBLISHED,
    ):
        return CommunityPost.objects.create(
            user=user or self.user,
            content=content,
            slug=slug,
            status=status,
        )

    def create_editorial_article(
        self,
        *,
        title="Davido's Music Journey",
        slug="davido-music-journey",
        excerpt="An article about Davido",
        status=EditorialArticle.Status.PUBLISHED,
    ):
        published_at = (
            timezone.now()
            if status == EditorialArticle.Status.PUBLISHED
            else None
        )

        return EditorialArticle.objects.create(
            title=title,
            slug=slug,
            excerpt=excerpt,
            content="This is the full editorial article content.",
            author=self.user,
            status=status,
            published_at=published_at,
        )

    # ========================================================
    # General search behavior
    # ========================================================

    def test_search_returns_all_six_categories(self):
        results = self.service.search(
            query="Davido",
        )

        self.assertEqual(
            set(results.keys()),
            set(GlobalSearchService.CATEGORIES),
        )

    def test_search_returns_matching_results_in_all_categories(self):
        song = self.create_song(
            title="Unavailable",
            slug="davido-unavailable",
            artist=self.artist,
        )

        album = self.create_album(
            title="Timeless",
            slug="davido-timeless",
            artist=self.artist,
        )

        post = self.create_community_post()

        article = self.create_editorial_article()

        results = self.service.search(
            query="Davido",
        )

        self.assertIn(
            song,
            [result.object for result in results["songs"].results],
        )

        self.assertIn(
            album,
            [result.object for result in results["albums"].results],
        )

        self.assertIn(
            self.artist,
            [
                result.object
                for result in results["artists"].results
            ],
        )

        self.assertIn(
            post,
            results["community_posts"].results,
        )

        self.assertIn(
            article,
            results["editorial_articles"].results,
        )

        self.assertIn(
            self.user,
            results["users"].results,
        )

    # ========================================================
    # Category filtering
    # ========================================================

    def test_category_filter_searches_only_selected_category(self):
        self.create_community_post()

        results = self.service.search(
            query="Davido",
            category="community_posts",
        )

        self.assertGreater(
            results["community_posts"].count,
            0,
        )

        for category in GlobalSearchService.CATEGORIES:
            if category == "community_posts":
                continue

            self.assertEqual(
                results[category].count,
                0,
            )

            self.assertEqual(
                results[category].results,
                [],
            )

    def test_invalid_category_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.search(
                query="Davido",
                category="videos",
            )

    # ========================================================
    # Independent pagination
    # ========================================================

    def test_categories_have_independent_pagination(self):
        songs = [
            self.create_song(
                title=title,
                slug=slug,
                artist=self.artist,
            )
            for title, slug in (
                ("Golden", "golden"),
                ("Golden Hour", "golden-hour"),
                ("Golden Nights", "golden-nights"),
            )
        ]

        first_page = self.service.search(
            query="Golden",
            pages={
                "songs": 1,
            },
            page_size=1,
        )

        second_page = self.service.search(
            query="Golden",
            pages={
                "songs": 2,
            },
            page_size=1,
        )

        self.assertEqual(
            first_page["songs"].count,
            3,
        )

        self.assertEqual(
            second_page["songs"].count,
            3,
        )

        self.assertEqual(
            first_page["songs"].results[0].object.pk,
            songs[0].pk,
        )

        self.assertNotEqual(
            first_page["songs"].results[0].object.pk,
            second_page["songs"].results[0].object.pk,
        )

        self.assertTrue(
            first_page["songs"].has_next,
        )

        self.assertTrue(
            second_page["songs"].has_previous,
        )

        # Other categories retain their own default page.
        self.assertEqual(
            second_page["users"].page,
            1,
        )

    def test_page_size_is_capped(self):
        results = self.service.search(
            query="Davido",
            page_size=100,
        )

        for category in GlobalSearchService.CATEGORIES:
            self.assertEqual(
                results[category].page_size,
                GlobalSearchService.MAX_PAGE_SIZE,
            )

    def test_invalid_page_number_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.search(
                query="Davido",
                pages={
                    "songs": 0,
                },
            )

    def test_invalid_page_size_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.search(
                query="Davido",
                page_size=0,
            )

    # ========================================================
    # Public catalog visibility
    # ========================================================

    def test_catalog_search_excludes_unpublished_songs(self):
        published_song = self.create_song(
            title="Unavailable",
            slug="published-unavailable",
            artist=self.artist,
        )

        self.create_song(
            title="Unavailable",
            slug="draft-unavailable",
            artist=self.artist,
            status=Song.Status.DRAFT,
        )

        self.create_song(
            title="Unavailable",
            slug="archived-unavailable",
            artist=self.artist,
            status=Song.Status.ARCHIVED,
        )

        results = self.service.search(
            query="Unavailable",
            category="songs",
        )

        self.assertEqual(
            results["songs"].count,
            1,
        )

        self.assertEqual(
            results["songs"].results[0].object,
            published_song,
        )

    def test_catalog_search_excludes_unpublished_albums(self):
        published_album = self.create_album(
            title="Timeless",
            slug="published-timeless",
            artist=self.artist,
        )

        self.create_album(
            title="Timeless",
            slug="draft-timeless",
            artist=self.artist,
            status=Album.Status.DRAFT,
        )

        results = self.service.search(
            query="Timeless",
            category="albums",
        )

        self.assertEqual(
            results["albums"].count,
            1,
        )

        self.assertEqual(
            results["albums"].results[0].object,
            published_album,
        )

    def test_catalog_search_excludes_inactive_artists(self):
        active_artist = Artist.objects.create(
            name="Test Performer",
            slug="test-performer",
            is_active=True,
        )

        Artist.objects.create(
            name="Test Performer",
            slug="inactive-test-performer",
            is_active=False,
        )

        results = self.service.search(
            query="Test Performer",
            category="artists",
        )

        self.assertEqual(
            results["artists"].count,
            1,
        )

        self.assertEqual(
            results["artists"].results[0].object,
            active_artist,
        )

    # ========================================================
    # Community post visibility
    # ========================================================

    def test_community_search_excludes_hidden_and_removed_posts(self):
        published_post = self.create_community_post(
            content="Davido published community discussion",
            slug="published-davido-post",
        )

        self.create_community_post(
            content="Davido hidden discussion",
            slug="hidden-davido-post",
            status=CommunityPost.Status.HIDDEN,
        )

        self.create_community_post(
            content="Davido removed discussion",
            slug="removed-davido-post",
            status=CommunityPost.Status.REMOVED,
        )

        results = self.service.search(
            query="Davido",
            category="community_posts",
        )

        self.assertEqual(
            results["community_posts"].count,
            1,
        )

        self.assertEqual(
            results["community_posts"].results[0],
            published_post,
        )

    # ========================================================
    # Editorial article visibility
    # ========================================================

    def test_editorial_search_excludes_drafts_and_archived_articles(self):
        published_article = self.create_editorial_article(
            title="Davido's Musical Journey",
            slug="published-davido-article",
        )

        self.create_editorial_article(
            title="Davido's Musical Journey",
            slug="draft-davido-article",
            status=EditorialArticle.Status.DRAFT,
        )

        self.create_editorial_article(
            title="Davido's Musical Journey",
            slug="archived-davido-article",
            status=EditorialArticle.Status.ARCHIVED,
        )

        results = self.service.search(
            query="Davido",
            category="editorial_articles",
        )

        self.assertEqual(
            results["editorial_articles"].count,
            1,
        )

        self.assertEqual(
            results["editorial_articles"].results[0],
            published_article,
        )

    # ========================================================
    # Public user visibility and privacy
    # ========================================================

    def test_user_search_excludes_private_account_types(self):
        public_user = self.create_user(
            username="davido_public",
            display_name="Davido Public",
        )

        self.create_user(
            username="davido_staff",
            display_name="Davido Staff",
            is_staff=True,
        )

        self.create_user(
            username="davido_superuser",
            display_name="Davido Superuser",
            is_superuser=True,
            is_staff=True,
        )

        self.create_user(
            username="davido_inactive",
            display_name="Davido Inactive",
            is_active=False,
        )

        self.create_user(
            username="davido_incomplete",
            display_name="Davido Incomplete",
            onboarding_completed=False,
        )

        results = self.service.search(
            query="Davido",
            category="users",
        )

        result_ids = {
            result.pk
            for result in results["users"].results
        }

        self.assertIn(
            public_user.pk,
            result_ids,
        )

        # The requesting user is also a public account,
        # so their own profile can appear in search.
        self.assertIn(
            self.user.pk,
            result_ids,
        )

        self.assertEqual(
            result_ids,
            {
                self.user.pk,
                public_user.pk,
            },
        )
    
    def test_user_search_returns_only_public_user_records(self):
        results = self.service.search(
            query="Davido",
            category="users",
        )

        for result in results["users"].results:
            self.assertTrue(result.is_active)
            self.assertFalse(result.is_staff)
            self.assertFalse(result.is_superuser)
            self.assertTrue(result.onboarding_completed)

    # ========================================================
    # Follow-state annotation
    # ========================================================

    def test_authenticated_user_search_annotates_follow_status(self):
        followed_user = self.create_user(
            username="followed_davido",
            display_name="Davido Followed",
        )

        UserFollow.objects.create(
            follower=self.user,
            following=followed_user,
        )

        results = self.service.search(
            query="Davido",
            category="users",
            user=self.user,
        )

        followed_result = next(
            result
            for result in results["users"].results
            if result.pk == followed_user.pk
        )

        self.assertTrue(
            followed_result.is_following,
        )

    def test_authenticated_user_search_marks_unfollowed_users_false(self):
        unfollowed_user = self.create_user(
            username="unfollowed_davido",
            display_name="Davido Unfollowed",
        )

        results = self.service.search(
            query="Davido",
            category="users",
            user=self.user,
        )

        unfollowed_result = next(
            result
            for result in results["users"].results
            if result.pk == unfollowed_user.pk
        )

        self.assertFalse(
            unfollowed_result.is_following,
        )

    def test_anonymous_user_search_marks_follow_status_false(self):
        results = self.service.search(
            query="Davido",
            category="users",
        )

        for result in results["users"].results:
            self.assertFalse(
                result.is_following,
            )

    # ========================================================
    # Query validation
    # ========================================================

    def test_empty_query_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.search(
                query="   ",
            )

    def test_query_shorter_than_minimum_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.search(
                query="D",
            )

    def test_query_longer_than_maximum_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.search(
                query="a" * (
                    self.service.MAX_QUERY_LENGTH + 1
                ),
            )