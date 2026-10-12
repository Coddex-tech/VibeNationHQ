from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from music.models import (
    Album,
    Artist,
    ArtistFollow,
    CommunityPost,
    CommunityPostLike,
    CommunityPostTarget,
    Genre,
    MusicFeedInteraction,
    Song,
    UserFollow,
    UserGenrePreference,
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

        cls.genre = Genre.objects.create(
            name="Afrobeats",
            slug="afrobeats",
            is_active=True,
        )

        cls.other_genre = Genre.objects.create(
            name="Rock",
            slug="rock",
            is_active=True,
        )

    # ============================================================
    # HELPERS
    # ============================================================

    @classmethod
    def create_song(
        cls,
        *,
        title,
        slug,
        artist=None,
        genre=None,
        published_at=None,
        is_featured=False,
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
            is_featured=is_featured,
        )

        song.artists.add(
            artist or cls.artist,
        )

        if genre is not None:
            song.genres.add(genre)

        return song

    @classmethod
    def create_album(
        cls,
        *,
        title,
        slug,
        artist=None,
        published_at=None,
        is_featured=False,
    ):
        album = Album.objects.create(
            title=title,
            slug=slug,
            status=Album.Status.PUBLISHED,
            published_at=(
                published_at
                if published_at is not None
                else timezone.now()
            ),
            is_featured=is_featured,
        )

        album.artists.add(
            artist or cls.artist,
        )

        return album

    @classmethod
    def create_community_post(
        cls,
        *,
        user=None,
        content="Community post",
        song=None,
        created_at=None,
        status=None,
    ):
        if status is None:
            status = CommunityPost.Status.PUBLISHED

        post = CommunityPost.objects.create(
            user=user or cls.other_user,
            content=content,
            status=status,
        )

        if created_at is not None:
            CommunityPost.objects.filter(
                pk=post.pk,
            ).update(
                created_at=created_at,
            )
            post.refresh_from_db()

        if song is not None:
            CommunityPostTarget.objects.create(
                post=post,
                target_type=(
                    CommunityPostTarget.TargetType.SONG
                ),
                song=song,
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
        created_at=None,
    ):
        interaction = MusicFeedInteraction.objects.create(
            user=user,
            interaction_type=interaction_type,
            song=song,
            album=album,
            artist=artist,
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
    def get_content_ids(
        results,
        content_type,
    ):
        return [
            candidate.object_id
            for candidate in results
            if candidate.content_type == content_type
        ]

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
    # BASIC FEED BEHAVIOR
    # ============================================================

    def test_anonymous_feed_returns_candidates(self):
        song = self.create_song(
            title="Public Song",
            slug="public-song",
        )

        result = self.service.get_feed(
            user=None,
            limit=20,
        )

        self.assertIn(
            song.id,
            self.get_content_ids(
                result["results"],
                "song",
            ),
        )

    def test_authenticated_feed_returns_candidates(self):
        song = self.create_song(
            title="Authenticated Song",
            slug="authenticated-song",
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        self.assertIn(
            song.id,
            self.get_content_ids(
                result["results"],
                "song",
            ),
        )

    def test_limit_is_respected(self):
        for index in range(10):
            self.create_song(
                title=f"Song {index}",
                slug=f"song-{index}",
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
            self.create_song(
                title=f"Song {index}",
                slug=f"song-{index}",
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
    # PUBLISHED / ACTIVE CONTENT
    # ============================================================

    def test_unpublished_song_is_excluded(self):
        song = Song.objects.create(
            title="Draft Song",
            slug="draft-song",
            status=Song.Status.DRAFT,
        )

        song.artists.add(
            self.artist,
        )

        result = self.service.get_feed(
            user=None,
            limit=20,
        )

        returned_ids = self.get_content_ids(
            result["results"],
            "song",
        )

        self.assertNotIn(
            song.id,
            returned_ids,
        )

    def test_inactive_artist_is_excluded(self):
        artist = Artist.objects.create(
            name="Inactive Artist",
            slug="inactive-artist",
            is_active=False,
        )

        result = self.service.get_feed(
            user=None,
            limit=20,
        )

        returned_ids = self.get_content_ids(
            result["results"],
            "artist",
        )

        self.assertNotIn(
            artist.id,
            returned_ids,
        )

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

        returned_ids = self.get_content_ids(
            result["results"],
            "community_post",
        )

        self.assertNotIn(
            post.id,
            returned_ids,
        )

    # ============================================================
    # COMMUNITY CONTENT
    # ============================================================

    def test_recent_community_post_is_included(self):
        post = self.create_community_post(
            content="Fresh community thought",
        )

        result = self.service.get_feed(
            user=None,
            limit=20,
        )

        returned_ids = self.get_content_ids(
            result["results"],
            "community_post",
        )

        self.assertIn(
            post.id,
            returned_ids,
        )

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

        followed_candidate = next(
            candidate
            for candidate in result["results"]
            if candidate.object_id == followed_post.id
            and candidate.content_type == "community_post"
        )

        unrelated_candidate = next(
            candidate
            for candidate in result["results"]
            if candidate.object_id == unrelated_post.id
            and candidate.content_type == "community_post"
        )

        self.assertGreater(
            followed_candidate.score,
            unrelated_candidate.score,
        )

    def test_mutual_user_post_gets_personalization_boost(self):
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
            content="Mutual's post",
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        candidate = next(
            candidate
            for candidate in result["results"]
            if candidate.content_type == "community_post"
            and candidate.object_id == mutual_post.id
        )

        self.assertEqual(
            candidate.source,
            "mutual",
        )

    # ============================================================
    # ARTIST FOLLOWING
    # ============================================================

    def test_followed_artist_song_is_added_to_feed(self):
        ArtistFollow.objects.create(
            user=self.user,
            artist=self.artist,
        )

        song = self.create_song(
            title="Followed Artist Song",
            slug="followed-artist-song",
            artist=self.artist,
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        candidates = [
            candidate
            for candidate in result["results"]
            if candidate.content_type == "song"
            and candidate.object_id == song.id
        ]

        self.assertTrue(candidates)

    def test_followed_artist_song_gets_personalization_boost(self):
        ArtistFollow.objects.create(
            user=self.user,
            artist=self.artist,
        )

        followed_song = self.create_song(
            title="Followed Song",
            slug="followed-song",
            artist=self.artist,
        )

        unrelated_song = self.create_song(
            title="Unrelated Song",
            slug="unrelated-song",
            artist=self.other_artist,
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        followed_candidate = next(
            candidate
            for candidate in result["results"]
            if candidate.content_type == "song"
            and candidate.object_id == followed_song.id
        )

        unrelated_candidate = next(
            candidate
            for candidate in result["results"]
            if candidate.content_type == "song"
            and candidate.object_id == unrelated_song.id
        )

        self.assertGreater(
            followed_candidate.score,
            unrelated_candidate.score,
        )

    # ============================================================
    # GENRE PREFERENCES
    # ============================================================

    def test_preferred_genre_song_gets_personalization_boost(self):
        UserGenrePreference.objects.create(
            user=self.user,
            genre=self.genre,
        )

        preferred_song = self.create_song(
            title="Preferred Genre Song",
            slug="preferred-genre-song",
            genre=self.genre,
        )

        other_song = self.create_song(
            title="Other Genre Song",
            slug="other-genre-song",
            genre=self.other_genre,
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        preferred_candidate = next(
            candidate
            for candidate in result["results"]
            if candidate.content_type == "song"
            and candidate.object_id == preferred_song.id
        )

        other_candidate = next(
            candidate
            for candidate in result["results"]
            if candidate.content_type == "song"
            and candidate.object_id == other_song.id
        )

        self.assertGreater(
            preferred_candidate.score,
            other_candidate.score,
        )

    # ============================================================
    # INTERACTION HISTORY
    # ============================================================

    def test_interacted_song_gets_personalization_boost(self):
        interacted_song = self.create_song(
            title="Previously Viewed",
            slug="previously-viewed",
        )

        other_song = self.create_song(
            title="Never Viewed",
            slug="never-viewed",
        )

        self.create_interaction(
            user=self.user,
            interaction_type="view_song",
            song=interacted_song,
            created_at=timezone.now(),
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        interacted_candidate = next(
            candidate
            for candidate in result["results"]
            if candidate.content_type == "song"
            and candidate.object_id == interacted_song.id
        )

        other_candidate = next(
            candidate
            for candidate in result["results"]
            if candidate.content_type == "song"
            and candidate.object_id == other_song.id
        )

        self.assertGreater(
            interacted_candidate.score,
            other_candidate.score,
        )

    def test_old_interaction_is_ignored(self):
        old_song = self.create_song(
            title="Old Interaction Song",
            slug="old-interaction-song",
        )

        current_song = self.create_song(
            title="Current Interaction Song",
            slug="current-interaction-song",
        )

        self.create_interaction(
            user=self.user,
            interaction_type="view_song",
            song=old_song,
            created_at=(
                timezone.now()
                - timedelta(days=120)
            ),
        )

        self.create_interaction(
            user=self.user,
            interaction_type="view_song",
            song=current_song,
            created_at=timezone.now(),
        )

        candidates = self.service._generate_candidates(
            user=self.user,
            candidate_limit=20,
        )

        context = self.service._build_user_context(
            user=self.user,
            candidates=candidates,
        )

        self.assertNotIn(
            old_song.id,
            context.interacted_song_ids,
        )

        self.assertIn(
            current_song.id,
            context.interacted_song_ids,
        )

    # ============================================================
    # LIKE SIGNALS
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

        liked_candidate = next(
            candidate
            for candidate in result["results"]
            if candidate.content_type == "community_post"
            and candidate.object_id == liked_post.id
        )

        other_candidate = next(
            candidate
            for candidate in result["results"]
            if candidate.content_type == "community_post"
            and candidate.object_id == other_post.id
        )

        self.assertLess(
            liked_candidate.score,
            other_candidate.score,
        )

    # ============================================================
    # DEDUPLICATION
    # ============================================================

    def test_same_object_is_not_returned_twice(self):
        ArtistFollow.objects.create(
            user=self.user,
            artist=self.artist,
        )

        song = self.create_song(
            title="Duplicate Candidate",
            slug="duplicate-candidate",
            artist=self.artist,
        )

        self.create_interaction(
            user=self.user,
            interaction_type="view_song",
            song=song,
            created_at=timezone.now(),
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        matching = [
            candidate
            for candidate in result["results"]
            if candidate.content_type == "song"
            and candidate.object_id == song.id
        ]

        self.assertEqual(
            len(matching),
            1,
        )

    # ============================================================
    # DIVERSITY
    # ============================================================

    def test_feed_does_not_repeat_same_content_type_three_times_in_a_row(
        self,
    ):
        artists = [
            Artist.objects.create(
                name=f"Diversity Artist {index}",
                slug=f"diversity-artist-{index}",
                is_active=True,
            )
            for index in range(6)
        ]

        songs = [
            self.create_song(
                title=f"Diversity Song {index}",
                slug=f"diversity-song-{index}",
                artist=artist,
            )
            for index, artist in enumerate(artists)
        ]

        candidates = [
            FeedCandidate(
                content_type="song",
                source="discovery",
                object=songs[0],
                score=100.0,
            ),
            FeedCandidate(
                content_type="song",
                source="discovery",
                object=songs[1],
                score=99.0,
            ),
            FeedCandidate(
                content_type="song",
                source="discovery",
                object=songs[2],
                score=98.0,
            ),
            FeedCandidate(
                content_type="song",
                source="discovery",
                object=songs[3],
                score=97.0,
            ),
            FeedCandidate(
                content_type="artist",
                source="discovery",
                object=artists[0],
                score=96.0,
            ),
            FeedCandidate(
                content_type="artist",
                source="discovery",
                object=artists[1],
                score=95.0,
            ),
            FeedCandidate(
                content_type="artist",
                source="discovery",
                object=artists[2],
                score=94.0,
            ),
        ]

        selected = self.service._select_diverse(
            candidates=candidates,
            limit=6,
        )

        content_types = [
            candidate.content_type
            for candidate in selected
        ]

        self.assertEqual(
            len(selected),
            6,
        )

        for index in range(
            2,
            len(content_types),
        ):
            self.assertFalse(
                (
                    content_types[index]
                    == content_types[index - 1]
                    == content_types[index - 2]
                ),
                msg=(
                    "Feed returned the same content type "
                    "three times consecutively: "
                    f"{content_types}"
                ),
            )

    # ============================================================
    # FEATURED CONTENT
    # ============================================================

    def test_featured_song_receives_featured_score(self):
        featured_song = self.create_song(
            title="Featured Song",
            slug="featured-song",
            is_featured=True,
        )

        normal_song = self.create_song(
            title="Normal Song",
            slug="normal-song",
            is_featured=False,
        )

        result = self.service.get_feed(
            user=None,
            limit=20,
        )

        featured_candidate = next(
            candidate
            for candidate in result["results"]
            if candidate.content_type == "song"
            and candidate.object_id == featured_song.id
        )

        normal_candidate = next(
            candidate
            for candidate in result["results"]
            if candidate.content_type == "song"
            and candidate.object_id == normal_song.id
        )

        self.assertGreater(
            featured_candidate.score,
            normal_candidate.score,
        )

    # ============================================================
    # SOURCE METADATA
    # ============================================================

    def test_followed_artist_candidate_has_correct_source(self):
        ArtistFollow.objects.create(
            user=self.user,
            artist=self.artist,
        )

        song = self.create_song(
            title="Followed Artist Song",
            slug="followed-artist-source",
            artist=self.artist,
        )

        result = self.service.get_feed(
            user=self.user,
            limit=20,
        )

        candidate = next(
            candidate
            for candidate in result["results"]
            if candidate.content_type == "song"
            and candidate.object_id == song.id
        )

        self.assertEqual(
            candidate.source,
            "followed_artist",
        )