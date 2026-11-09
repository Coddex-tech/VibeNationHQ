from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.test import APIRequestFactory

from music.api.views.global_search import GlobalSearchAPIView
from music.services.global_search import GlobalSearchService

from music.models import (
    Album,
    Artist,
    CommunityPost,
    EditorialArticle,
    Song,
    UserFollow,
)


class GlobalSearchAPIViewTests(SimpleTestCase):
    """
    Tests the global search API view independently of database
    search behavior.

    GlobalSearchService is mocked because its search behavior
    is already covered by the service test suite.
    """

    URL = "/api/v1/music/global-search/"

    CATEGORIES = (
        "songs",
        "albums",
        "artists",
        "community_posts",
        "editorial_articles",
        "users",
    )

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = GlobalSearchAPIView.as_view()

    def make_page(
        self,
        *,
        count=0,
        page=1,
        page_size=20,
        has_next=False,
        has_previous=False,
        results=None,
    ):
        return SimpleNamespace(
            count=count,
            page=page,
            page_size=page_size,
            has_next=has_next,
            has_previous=has_previous,
            results=results or [],
        )

    def make_search_results(self, **overrides):
        results = {
            category: self.make_page()
            for category in self.CATEGORIES
        }

        results.update(overrides)
        return results

    def make_request(self, params=None):
        return self.factory.get(
            self.URL,
            data=params or {},
        )

    def perform_request(self, params=None):
        request = self.make_request(params)
        return self.view(request)

    @patch.object(GlobalSearchService, "search")
    def test_successful_anonymous_search_returns_all_categories(
        self,
        mock_search,
    ):
        mock_search.return_value = self.make_search_results()

        response = self.perform_request({
            "q": "Davido",
        })

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            set(response.data.keys()),
            {"query", "type", "results"},
        )

        self.assertEqual(response.data["query"], "Davido")
        self.assertEqual(response.data["type"], "all")

        self.assertEqual(
            set(response.data["results"].keys()),
            set(self.CATEGORIES),
        )

        for category in self.CATEGORIES:
            category_data = response.data["results"][category]

            self.assertEqual(category_data["count"], 0)
            self.assertEqual(category_data["page"], 1)
            self.assertEqual(category_data["page_size"], 20)
            self.assertFalse(category_data["has_next"])
            self.assertFalse(category_data["has_previous"])
            self.assertIsNone(category_data["next"])
            self.assertIsNone(category_data["previous"])
    
    @patch.object(GlobalSearchService, "search")
    def test_search_passes_default_page_size_and_page_numbers(
        self,
        mock_search,
    ):
        mock_search.return_value = self.make_search_results()

        self.perform_request({
            "q": "Davido",
        })

        mock_search.assert_called_once()

        _, kwargs = mock_search.call_args

        self.assertEqual(kwargs["query"], "Davido")
        self.assertIsNone(kwargs["category"])
        self.assertEqual(kwargs["page_size"], 20)

        self.assertEqual(
            kwargs["pages"],
            {
                "songs": 1,
                "albums": 1,
                "artists": 1,
                "community_posts": 1,
                "editorial_articles": 1,
                "users": 1,
            },
        )

        self.assertIn("user", kwargs)

    @patch.object(GlobalSearchService, "search")
    def test_category_filter_is_passed_to_service(
        self,
        mock_search,
    ):
        mock_search.return_value = self.make_search_results()

        response = self.perform_request({
            "q": "Davido",
            "type": "users",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["type"], "users")

        _, kwargs = mock_search.call_args

        self.assertEqual(kwargs["query"], "Davido")
        self.assertEqual(kwargs["category"], "users")

    @patch.object(GlobalSearchService, "search")
    def test_page_size_is_passed_to_service(
        self,
        mock_search,
    ):
        mock_search.return_value = self.make_search_results()

        response = self.perform_request({
            "q": "Davido",
            "page_size": 10,
        })

        self.assertEqual(response.status_code, 200)

        _, kwargs = mock_search.call_args

        self.assertEqual(kwargs["page_size"], 10)


    @patch.object(GlobalSearchService, "search")
    def test_category_specific_next_url_is_generated(
        self,
        mock_search,
    ):
        mock_search.return_value = self.make_search_results(
            songs=self.make_page(
                count=25,
                page=1,
                page_size=20,
                has_next=True,
            ),
        )

        response = self.perform_request({
            "q": "Davido",
            "page_size": 20,
        })

        self.assertEqual(response.status_code, 200)

        next_url = response.data["results"]["songs"]["next"]

        self.assertIsNotNone(next_url)

        parsed_url = urlparse(next_url)
        query_params = parse_qs(parsed_url.query)

        self.assertEqual(query_params["q"], ["Davido"])
        self.assertEqual(query_params["page_size"], ["20"])
        self.assertEqual(query_params["songs_page"], ["2"])

        # Pagination for songs must not modify other categories.
        self.assertNotIn("albums_page", query_params)
        self.assertNotIn("users_page", query_params)

    @patch.object(GlobalSearchService, "search")
    def test_category_specific_previous_url_is_generated(
        self,
        mock_search,
    ):
        mock_search.return_value = self.make_search_results(
            users=self.make_page(
                count=25,
                page=2,
                page_size=20,
                has_previous=True,
            ),
        )

        response = self.perform_request({
            "q": "Davido",
            "users_page": 2,
        })

        self.assertEqual(response.status_code, 200)

        previous_url = response.data["results"]["users"]["previous"]

        self.assertIsNotNone(previous_url)

        parsed_url = urlparse(previous_url)
        query_params = parse_qs(parsed_url.query)

        self.assertEqual(query_params["q"], ["Davido"])
        self.assertEqual(query_params["users_page"], ["1"])

    @patch.object(GlobalSearchService, "search")
    def test_pagination_preserves_existing_query_parameters(
        self,
        mock_search,
    ):
        mock_search.return_value = self.make_search_results(
            albums=self.make_page(
                count=30,
                page=1,
                page_size=10,
                has_next=True,
            ),
        )

        response = self.perform_request({
            "q": "Davido",
            "type": "albums",
            "page_size": 10,
            "songs_page": 3,
        })

        self.assertEqual(response.status_code, 200)

        next_url = response.data["results"]["albums"]["next"]

        query_params = parse_qs(urlparse(next_url).query)

        self.assertEqual(query_params["q"], ["Davido"])
        self.assertEqual(query_params["type"], ["albums"])
        self.assertEqual(query_params["page_size"], ["10"])
        self.assertEqual(query_params["songs_page"], ["3"])
        self.assertEqual(query_params["albums_page"], ["2"])

    def test_missing_query_returns_400(self):
        response = self.perform_request()

        self.assertEqual(response.status_code, 400)
        self.assertIn("q", response.data)

    def test_query_shorter_than_two_characters_returns_400(self):
        response = self.perform_request({
            "q": "a",
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("q", response.data)

    def test_query_longer_than_maximum_length_returns_400(self):
        response = self.perform_request({
            "q": "a" * 201,
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("q", response.data)

    def test_invalid_category_returns_400(self):
        response = self.perform_request({
            "q": "Davido",
            "type": "playlists",
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("type", response.data)

    def test_zero_page_number_returns_400(self):
        response = self.perform_request({
            "q": "Davido",
            "songs_page": 0,
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("songs_page", response.data)

    def test_invalid_page_number_returns_400(self):
        response = self.perform_request({
            "q": "Davido",
            "songs_page": "invalid",
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("songs_page", response.data)

    def test_page_size_above_maximum_returns_400(self):
        response = self.perform_request({
            "q": "Davido",
            "page_size": 21,
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("page_size", response.data)

    def test_zero_page_size_returns_400(self):
        response = self.perform_request({
            "q": "Davido",
            "page_size": 0,
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("page_size", response.data)


class GlobalSearchURLIntegrationTests(TestCase):
    """
    Tests the globally registered search URL through Django's
    URL resolver and DRF's API client.
    """

    CATEGORIES = (
        "songs",
        "albums",
        "artists",
        "community_posts",
        "editorial_articles",
        "users",
    )

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("music_api:global-search")

    def make_search_results(self):
        return {
            category: SimpleNamespace(
                count=0,
                page=1,
                page_size=20,
                has_next=False,
                has_previous=False,
                results=[],
            )
            for category in self.CATEGORIES
        }

    @patch.object(GlobalSearchService, "search")
    def test_registered_global_search_url_returns_200(
        self,
        mock_search,
    ):
        mock_search.return_value = self.make_search_results()

        response = self.client.get(
            self.url,
            {"q": "Davido"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["query"], "Davido")
        self.assertEqual(response.data["type"], "all")

        self.assertEqual(
            set(response.data["results"].keys()),
            set(self.CATEGORIES),
        )

        mock_search.assert_called_once()

        _, kwargs = mock_search.call_args

        self.assertEqual(kwargs["query"], "Davido")
        self.assertFalse(kwargs["user"].is_authenticated)

    @patch.object(GlobalSearchService, "search")
    def test_registered_url_validates_missing_query(
        self,
        mock_search,
    ):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 400)
        self.assertIn("q", response.data)

        mock_search.assert_not_called()

    def test_existing_search_routes_remain_registered(self):
        existing_search_url = reverse("music_api:music-search")
        catalog_search_url = reverse("music_api:catalog-search")

        self.assertNotEqual(self.url, existing_search_url)
        self.assertNotEqual(self.url, catalog_search_url)

        self.assertTrue(existing_search_url.endswith("/search/"))
        self.assertTrue(
            catalog_search_url.endswith("/catalog/search/")
        )
        self.assertTrue(self.url.endswith("/global-search/"))


User = get_user_model()


class GlobalSearchDatabaseIntegrationTests(TestCase):
    """
    Tests global search against actual database records through
    the registered API endpoint.
    """

    CATEGORIES = (
        "songs",
        "albums",
        "artists",
        "community_posts",
        "editorial_articles",
        "users",
    )

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("music_api:global-search")

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
    # Actual endpoint results
    # ========================================================

    def test_endpoint_returns_results_from_all_six_categories(self):
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

        response = self.client.get(
            self.url,
            {"q": "Davido"},
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        self.assertEqual(
            set(results.keys()),
            set(self.CATEGORIES),
        )

        self.assertIn(
            song.pk,
            [item["id"] for item in results["songs"]["results"]],
        )

        self.assertIn(
            album.pk,
            [item["id"] for item in results["albums"]["results"]],
        )

        self.assertIn(
            self.artist.pk,
            [item["id"] for item in results["artists"]["results"]],
        )

        self.assertIn(
            post.pk,
            [
                item["id"]
                for item in results["community_posts"]["results"]
            ],
        )

        self.assertIn(
            article.pk,
            [
                item["id"]
                for item in results["editorial_articles"]["results"]
            ],
        )

        self.assertIn(
            self.user.pk,
            [item["id"] for item in results["users"]["results"]],
        )

    # ========================================================
    # Category filtering
    # ========================================================

    def test_endpoint_category_filter_returns_only_selected_category(self):
        post = self.create_community_post()

        response = self.client.get(
            self.url,
            {
                "q": "Davido",
                "type": "community_posts",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["type"], "community_posts")

        results = response.data["results"]

        self.assertEqual(
            results["community_posts"]["count"],
            1,
        )

        self.assertEqual(
            results["community_posts"]["results"][0]["id"],
            post.pk,
        )

        for category in self.CATEGORIES:
            if category == "community_posts":
                continue

            self.assertEqual(
                results[category]["count"],
                0,
            )

            self.assertEqual(
                results[category]["results"],
                [],
            )

    # ========================================================
    # Public visibility
    # ========================================================

    def test_endpoint_excludes_unpublished_catalog_content(self):
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

        response = self.client.get(
            self.url,
            {"q": "Davido"},
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        self.assertEqual(
            results["songs"]["count"],
            1,
        )

        self.assertEqual(
            results["songs"]["results"][0]["id"],
            published_song.pk,
        )

        self.assertEqual(
            results["albums"]["count"],
            1,
        )

        self.assertEqual(
            results["albums"]["results"][0]["id"],
            published_album.pk,
        )

    def test_endpoint_excludes_hidden_and_removed_community_posts(self):
        published_post = self.create_community_post(
            content="Davido published discussion",
            slug="published-davido-discussion",
        )

        self.create_community_post(
            content="Davido hidden discussion",
            slug="hidden-davido-discussion",
            status=CommunityPost.Status.HIDDEN,
        )

        self.create_community_post(
            content="Davido removed discussion",
            slug="removed-davido-discussion",
            status=CommunityPost.Status.REMOVED,
        )

        response = self.client.get(
            self.url,
            {
                "q": "Davido",
                "type": "community_posts",
            },
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]["community_posts"]

        self.assertEqual(results["count"], 1)

        self.assertEqual(
            results["results"][0]["id"],
            published_post.pk,
        )

    def test_endpoint_excludes_unpublished_editorial_articles(self):
        published_article = self.create_editorial_article(
            title="Davido's Music Journey",
            slug="published-davido-article",
        )

        self.create_editorial_article(
            title="Davido's Music Journey",
            slug="draft-davido-article",
            status=EditorialArticle.Status.DRAFT,
        )

        response = self.client.get(
            self.url,
            {
                "q": "Davido",
                "type": "editorial_articles",
            },
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]["editorial_articles"]

        self.assertEqual(results["count"], 1)

        self.assertEqual(
            results["results"][0]["id"],
            published_article.pk,
        )

    def test_endpoint_excludes_inactive_artists(self):
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

        response = self.client.get(
            self.url,
            {
                "q": "Test Performer",
                "type": "artists",
            },
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]["artists"]

        self.assertEqual(results["count"], 1)

        self.assertEqual(
            results["results"][0]["id"],
            active_artist.pk,
        )

    # ========================================================
    # User privacy and visibility
    # ========================================================

    def test_endpoint_excludes_private_account_types(self):
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
            is_staff=True,
            is_superuser=True,
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

        response = self.client.get(
            self.url,
            {
                "q": "Davido",
                "type": "users",
            },
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]["users"]["results"]

        result_ids = {
            item["id"]
            for item in results
        }

        self.assertEqual(
            result_ids,
            {
                self.user.pk,
                public_user.pk,
            },
        )

    def test_endpoint_does_not_expose_user_email_addresses(self):
        response = self.client.get(
            self.url,
            {"q": "Davido"},
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        # Check user search results.
        for user_data in results["users"]["results"]:
            self.assertNotIn("email", user_data)
            self.assertNotIn(
                "davido@example.com",
                str(user_data),
            )

        # Check community post authors and nested user data.
        for post_data in results["community_posts"]["results"]:
            self.assertNotIn(
                "davido@example.com",
                str(post_data),
            )

        # Check editorial article authors.
        for article_data in results["editorial_articles"]["results"]:
            self.assertNotIn(
                "davido@example.com",
                str(article_data),
            )

    # ========================================================
    # Follow state
    # ========================================================

    def test_authenticated_user_receives_correct_follow_state(self):
        followed_user = self.create_user(
            username="followed_davido",
            display_name="Davido Followed",
        )

        unfollowed_user = self.create_user(
            username="unfollowed_davido",
            display_name="Davido Unfollowed",
        )

        UserFollow.objects.create(
            follower=self.user,
            following=followed_user,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            self.url,
            {
                "q": "Davido",
                "type": "users",
            },
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]["users"]["results"]

        users_by_id = {
            item["id"]: item
            for item in results
        }

        self.assertTrue(
            users_by_id[followed_user.pk]["is_following"],
        )

        self.assertFalse(
            users_by_id[unfollowed_user.pk]["is_following"],
        )

    # ========================================================
    # Independent pagination
    # ========================================================

    def test_endpoint_paginates_songs_independently(self):
        for title, slug in (
            ("Golden", "golden"),
            ("Golden Hour", "golden-hour"),
            ("Golden Nights", "golden-nights"),
        ):
            self.create_song(
                title=title,
                slug=slug,
                artist=self.artist,
            )

        response = self.client.get(
            self.url,
            {
                "q": "Golden",
                "page_size": 1,
            },
        )

        self.assertEqual(response.status_code, 200)

        songs = response.data["results"]["songs"]

        self.assertEqual(songs["count"], 3)
        self.assertEqual(songs["page"], 1)
        self.assertEqual(songs["page_size"], 1)
        self.assertEqual(len(songs["results"]), 1)
        self.assertTrue(songs["has_next"])
        self.assertIsNotNone(songs["next"])

        # Other categories must remain on their own first page.
        self.assertEqual(
            response.data["results"]["albums"]["page"],
            1,
        )

        second_response = self.client.get(songs["next"])

        self.assertEqual(second_response.status_code, 200)

        second_page = second_response.data["results"]["songs"]

        self.assertEqual(second_page["page"], 2)
        self.assertEqual(len(second_page["results"]), 1)
        self.assertTrue(second_page["has_previous"])
        self.assertIsNotNone(second_page["previous"])
