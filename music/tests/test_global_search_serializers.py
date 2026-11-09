
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from music.models import (
    Artist,
    CommunityPost,
    EditorialArticle,
    Song,
)
from music.serializers.global_search import (
    GlobalSearchResponseSerializer,
)
from music.services.global_search import GlobalSearchService


User = get_user_model()


class GlobalSearchResponseSerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.user = self.create_user(
            username="davido_fan",
            email="private-email@example.com",
            display_name="Davido Fan",
        )

        self.artist = Artist.objects.create(
            name="Davido",
            slug="davido",
            is_active=True,
        )

        self.song = Song.objects.create(
            title="Unavailable",
            slug="unavailable",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        self.song.artists.add(self.artist)

        self.community_post = CommunityPost.objects.create(
            user=self.user,
            content="Davido has released another great song.",
            slug="davido-community-discussion",
            status=CommunityPost.Status.PUBLISHED,
        )

        self.editorial_article = EditorialArticle.objects.create(
            title="Davido's Musical Journey",
            slug="davidos-musical-journey",
            excerpt="A look at Davido's music career.",
            content="Full editorial article content.",
            author=self.user,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.search_service = GlobalSearchService()

    # ========================================================
    # Helpers
    # ========================================================

    def create_user(
        self,
        *,
        username,
        email,
        display_name="",
    ):
        user = User.objects.create(
            username=username,
            email=email,
            display_name=display_name,
            is_active=True,
            is_staff=False,
            is_superuser=False,
            onboarding_completed=True,
        )

        user.set_password("test-password")
        user.save(update_fields=["password"])

        return user

    def get_search_results(self, *, query="Davido"):
        return self.search_service.search(
            query=query,
            user=self.user,
        )

    def serialize_results(self, *, query="Davido"):
        results = self.get_search_results(
            query=query,
        )

        request = self.factory.get(
            "/api/v1/music/global-search/",
            {"q": query},
        )

        request.user = self.user

        serializer = GlobalSearchResponseSerializer(
            results,
            context={
                "request": request,
            },
        )

        return serializer.data

    def assert_no_email_key(self, value):
        """
        Recursively ensure no serialized object exposes
        a field named email.
        """

        if isinstance(value, dict):
            self.assertNotIn(
                "email",
                value,
            )

            for nested_value in value.values():
                self.assert_no_email_key(nested_value)

        elif isinstance(value, (list, tuple)):
            for nested_value in value:
                self.assert_no_email_key(nested_value)

    # ========================================================
    # Response structure
    # ========================================================

    def test_response_contains_all_six_categories(self):
        data = self.serialize_results()

        expected_categories = {
            "songs",
            "albums",
            "artists",
            "community_posts",
            "editorial_articles",
            "users",
        }

        self.assertEqual(
            set(data.keys()),
            expected_categories,
        )

    def test_each_category_contains_pagination_metadata(self):
        data = self.serialize_results()

        for category in (
            "songs",
            "albums",
            "artists",
            "community_posts",
            "editorial_articles",
            "users",
        ):
            with self.subTest(category=category):
                category_data = data[category]

                self.assertIn("count", category_data)
                self.assertIn("page", category_data)
                self.assertIn("page_size", category_data)
                self.assertIn("has_next", category_data)
                self.assertIn("has_previous", category_data)
                self.assertIn("results", category_data)

    def test_category_metadata_matches_service_results(self):
        service_results = self.get_search_results()
        serialized_data = self.serialize_results()

        for category in GlobalSearchService.CATEGORIES:
            with self.subTest(category=category):
                page = service_results[category]
                serialized_page = serialized_data[category]

                self.assertEqual(
                    serialized_page["count"],
                    page.count,
                )

                self.assertEqual(
                    serialized_page["page"],
                    page.page,
                )

                self.assertEqual(
                    serialized_page["page_size"],
                    page.page_size,
                )

                self.assertEqual(
                    serialized_page["has_next"],
                    page.has_next,
                )

                self.assertEqual(
                    serialized_page["has_previous"],
                    page.has_previous,
                )

    # ========================================================
    # Catalog serializers
    # ========================================================

    def test_song_catalog_result_is_unwrapped_and_serialized(self):
        data = self.serialize_results()

        songs = data["songs"]["results"]

        self.assertEqual(
            len(songs),
            1,
        )

        song_data = songs[0]

        self.assertEqual(
            song_data["id"],
            self.song.pk,
        )

        self.assertEqual(
            song_data["title"],
            self.song.title,
        )

        self.assertIn(
            "artists",
            song_data,
        )

        self.assertIn(
            "featured_artists",
            song_data,
        )

    def test_artist_catalog_result_is_unwrapped_and_serialized(self):
        data = self.serialize_results()

        artists = data["artists"]["results"]

        self.assertEqual(
            len(artists),
            1,
        )

        artist_data = artists[0]

        self.assertEqual(
            artist_data["id"],
            self.artist.pk,
        )

        self.assertEqual(
            artist_data["name"],
            self.artist.name,
        )

        self.assertIn(
            "profile_image",
            artist_data,
        )

    # ========================================================
    # Community post serialization
    # ========================================================

    def test_community_post_is_serialized(self):
        data = self.serialize_results()

        posts = data["community_posts"]["results"]

        self.assertEqual(
            len(posts),
            1,
        )

        post_data = posts[0]

        self.assertEqual(
            post_data["id"],
            self.community_post.pk,
        )

        self.assertEqual(
            post_data["content"],
            self.community_post.content,
        )

        self.assertIn(
            "user",
            post_data,
        )

        self.assertIn(
            "target",
            post_data,
        )

        self.assertIn(
            "likes_count",
            post_data,
        )

        self.assertIn(
            "comments_count",
            post_data,
        )

    def test_community_post_author_email_is_not_exposed(self):
        data = self.serialize_results()

        self.assert_no_email_key(
            data["community_posts"],
        )

        self.assertNotIn(
            "private-email@example.com",
            str(data["community_posts"]),
        )

    # ========================================================
    # Editorial article serialization
    # ========================================================

    def test_editorial_article_is_serialized(self):
        data = self.serialize_results()

        articles = data["editorial_articles"]["results"]

        self.assertEqual(
            len(articles),
            1,
        )

        article_data = articles[0]

        self.assertEqual(
            article_data["id"],
            self.editorial_article.pk,
        )

        self.assertEqual(
            article_data["title"],
            self.editorial_article.title,
        )

        self.assertEqual(
            article_data["author"]["id"],
            self.user.pk,
        )

        self.assertEqual(
            article_data["author"]["name"],
            self.user.display_name,
        )

    def test_editorial_author_email_is_not_exposed(self):
        data = self.serialize_results()

        self.assert_no_email_key(
            data["editorial_articles"],
        )

        self.assertNotIn(
            "private-email@example.com",
            str(data["editorial_articles"]),
        )

    # ========================================================
    # User serialization and privacy
    # ========================================================

    def test_user_result_contains_only_search_profile_fields(self):
        data = self.serialize_results()

        users = data["users"]["results"]

        self.assertEqual(
            len(users),
            1,
        )

        user_data = users[0]

        expected_fields = {
            "id",
            "username",
            "display_name",
            "profile_image",
            "is_verified",
            "is_identity_verified",
            "is_following",
        }

        self.assertEqual(
            set(user_data.keys()),
            expected_fields,
        )

        self.assertEqual(
            user_data["id"],
            self.user.pk,
        )

        self.assertEqual(
            user_data["username"],
            self.user.username,
        )

        self.assertEqual(
            user_data["display_name"],
            self.user.display_name,
        )

    def test_user_result_never_exposes_email(self):
        data = self.serialize_results()

        self.assert_no_email_key(
            data["users"],
        )

        self.assertNotIn(
            "private-email@example.com",
            str(data["users"]),
        )

    def test_user_result_does_not_expose_private_profile_fields(self):
        data = self.serialize_results()

        user_data = data["users"]["results"][0]

        self.assertNotIn(
            "bio",
            user_data,
        )

        self.assertNotIn(
            "date_joined",
            user_data,
        )

        self.assertNotIn(
            "followers_count",
            user_data,
        )

        self.assertNotIn(
            "following_count",
            user_data,
        )

        self.assertNotIn(
            "artists_count",
            user_data,
        )

        self.assertNotIn(
            "is_own_profile",
            user_data,
        )

    def test_user_follow_state_is_preserved(self):
        data = self.serialize_results()

        user_data = data["users"]["results"][0]

        self.assertFalse(
            user_data["is_following"],
        )

    # ========================================================
    # Empty categories
    # ========================================================

    def test_empty_category_serializes_with_empty_results(self):
        results = self.search_service.search(
            query="Davido",
            category="users",
            user=self.user,
        )

        request = self.factory.get(
            "/api/v1/music/global-search/",
            {"q": "Davido", "type": "users"},
        )

        request.user = self.user

        data = GlobalSearchResponseSerializer(
            results,
            context={
                "request": request,
            },
        ).data

        for category in (
            "songs",
            "albums",
            "artists",
            "community_posts",
            "editorial_articles",
        ):
            with self.subTest(category=category):
                self.assertEqual(
                    data[category]["count"],
                    0,
                )

                self.assertEqual(
                    data[category]["results"],
                    [],
                )

    # ========================================================
    # Context propagation
    # ========================================================

    def test_request_context_is_passed_to_nested_serializers(self):
        data = self.serialize_results()

        self.assertIn(
            "is_liked",
            data["community_posts"]["results"][0],
        )

        self.assertIn(
            "is_favorited",
            data["community_posts"]["results"][0],
        )
