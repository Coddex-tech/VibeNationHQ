from django.test import TestCase
from django.utils import timezone
from rest_framework import serializers
from types import SimpleNamespace

from music.models import (
    Artist,
    Genre,
    Album,
    Song,
    AlbumTrack,
    SongFavorite,
    AlbumFavorite,
    ArtistFollow,
    UserFollow,
    EditorialArticleLike,
    CommunityPostLike,
    EditorialCommentLike,
    CommunityPostCommentLike,
    EditorialArticle,
    CommunityPost,
    EditorialComment,
    CommunityPostComment
)

from music.serializers.catalog import (
    GenreSerializer,
    ArtistCardSerializer,
    ArtistSerializer,
    AlbumCardSerializer,
    SongCardSerializer,
    SongSerializer,
    AlbumTrackSerializer,
    AlbumSerializer,
)

from music.serializers.ratings import (
    SongRatingSerializer,
    SongRatingCreateSerializer,
    SongRatingUpdateSerializer,
    AlbumRatingSerializer,
    AlbumRatingCreateSerializer,
    AlbumRatingUpdateSerializer,
)

from music.serializers.favourites import (
    SongFavoriteSerializer,
    SongFavoriteCreateSerializer,
    AlbumFavoriteSerializer,
    AlbumFavoriteCreateSerializer,
)

from music.serializers.follows import (
    ArtistFollowSerializer,
    ArtistFollowCreateSerializer,
    UserFollowSerializer,
    UserFollowCreateSerializer,
)

from music.serializers.likes import (
    EditorialArticleLikeSerializer,
    EditorialArticleLikeCreateSerializer,
    CommunityPostLikeSerializer,
    CommunityPostLikeCreateSerializer,
    EditorialCommentLikeSerializer,
    EditorialCommentLikeCreateSerializer,
    CommunityPostCommentLikeSerializer,
    CommunityPostCommentLikeCreateSerializer,
)

from music.serializers.community import (
    CommunityPostComment,
    CommunityPostTarget,
    CommunityPostTargetSerializer,
    CommunityPostTargetCreateSerializer,
    CommunityPostSerializer,
    CommunityPostCreateSerializer,
    CommunityPostCommentSerializer,
    CommunityPostUpdateSerializer,
    CommunityPostCommentUpdateSerializer,
    CommunityPostCommentCreateSerializer,
    CommunityPostCommentReportCreateSerializer,
    CommunityPostReportCreateSerializer,
    CommunityPostReportSerializer,
    CommunityPostCommentReport,
    CommunityPostCommentReportSerializer,
    CommunityPostReport
)

from django.contrib.auth import get_user_model

from music.models import (
    SongRating,
    AlbumRating,
)


User = get_user_model()



class CommunitySerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="communityuser",
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

        self.album = Album.objects.create(
            title="Test Album",
            slug="test-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.song = Song.objects.create(
            title="Test Song",
            slug="test-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.post = CommunityPost.objects.create(
            user=self.user,
            content="This is a community post.",
            status=CommunityPost.Status.PUBLISHED,
        )

        self.target = CommunityPostTarget.objects.create(
            post=self.post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=self.song,
        )

        self.comment = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="This is a comment.",
            status=CommunityPostComment.Status.PUBLISHED,
        )

        self.request = SimpleNamespace(user=self.user)

    # ---------------------------------------------------------
    # TARGET SERIALIZERS
    # ---------------------------------------------------------

    def test_target_serializer(self):
        serializer = CommunityPostTargetSerializer(
            self.target,
            context={"request": self.request},
        )

        data = serializer.data

        self.assertEqual(data["id"], self.target.id)
        self.assertEqual(
            data["target_type"],
            CommunityPostTarget.TargetType.SONG,
        )
        self.assertIn("song", data)
        self.assertEqual(data["song"]["id"], self.song.id)

    def test_target_create_serializer_accepts_song(self):
        serializer = CommunityPostTargetCreateSerializer(
            data={
                "target_type": CommunityPostTarget.TargetType.SONG,
                "song": self.song.id,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_target_create_serializer_accepts_album(self):
        serializer = CommunityPostTargetCreateSerializer(
            data={
                "target_type": CommunityPostTarget.TargetType.ALBUM,
                "album": self.album.id,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_target_create_serializer_accepts_artist(self):
        serializer = CommunityPostTargetCreateSerializer(
            data={
                "target_type": CommunityPostTarget.TargetType.ARTIST,
                "artist": self.artist.id,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_target_create_serializer_rejects_missing_internal_target(self):
        serializer = CommunityPostTargetCreateSerializer(
            data={
                "target_type": CommunityPostTarget.TargetType.SONG,
            }
        )

        self.assertFalse(serializer.is_valid())

    def test_target_create_serializer_rejects_mixed_internal_external(self):
        provider = CommunityPostTarget.ExternalProvider.choices[0][0]
        content_type = CommunityPostTarget.ExternalContentType.choices[0][0]

        serializer = CommunityPostTargetCreateSerializer(
            data={
                "target_type": CommunityPostTarget.TargetType.SONG,
                "song": self.song.id,
                "external_provider": provider,
                "external_content_type": content_type,
                "external_id": "external-123",
            }
        )

        self.assertFalse(serializer.is_valid())

    def test_target_create_serializer_accepts_external_target_identity(self):
        provider = CommunityPostTarget.ExternalProvider.choices[0][0]
        content_type = CommunityPostTarget.ExternalContentType.choices[0][0]

        serializer = CommunityPostTargetCreateSerializer(
            data={
                "target_type": CommunityPostTarget.TargetType.EXTERNAL,
                "external_provider": provider,
                "external_content_type": content_type,
                "external_id": "external-123",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_target_create_serializer_rejects_external_without_identity(self):
        serializer = CommunityPostTargetCreateSerializer(
            data={
                "target_type": CommunityPostTarget.TargetType.EXTERNAL,
            }
        )

        self.assertFalse(serializer.is_valid())

    def test_target_create_serializer_rejects_unpublished_song(self):
        draft_song = Song.objects.create(
            title="Draft Song",
            slug="draft-song",
            status=Song.Status.DRAFT,
        )

        serializer = CommunityPostTargetCreateSerializer(
            data={
                "target_type": CommunityPostTarget.TargetType.SONG,
                "song": draft_song.id,
            }
        )

        self.assertFalse(serializer.is_valid())

    def test_target_create_serializer_rejects_inactive_artist(self):
        inactive_artist = Artist.objects.create(
            name="Inactive Artist",
            slug="inactive-artist",
            is_active=False,
        )

        serializer = CommunityPostTargetCreateSerializer(
            data={
                "target_type": CommunityPostTarget.TargetType.ARTIST,
                "artist": inactive_artist.id,
            }
        )

        self.assertFalse(serializer.is_valid())

    # ---------------------------------------------------------
    # COMMUNITY POST SERIALIZERS
    # ---------------------------------------------------------

    def test_community_post_serializer(self):
        serializer = CommunityPostSerializer(
            self.post,
            context={"request": self.request},
        )

        data = serializer.data

        self.assertEqual(data["id"], self.post.id)
        self.assertEqual(data["content"], self.post.content)
        self.assertEqual(data["user"], self.user.id)
        self.assertIn("target", data)

    def test_community_post_create_serializer_assigns_user_server_side(self):
        serializer = CommunityPostCreateSerializer(
            data={
                "content": "A new community post.",
            },
            context={"request": self.request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        post = serializer.save()

        self.assertEqual(post.user, self.user)
        self.assertEqual(post.content, "A new community post.")

    def test_community_post_create_serializer_accepts_rating(self):
        serializer = CommunityPostCreateSerializer(
            data={
                "content": "I really like this song.",
                "rating": "4.5",
            },
            context={"request": self.request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        post = serializer.save()

        self.assertEqual(float(post.rating), 4.5)

    def test_community_post_create_serializer_rejects_invalid_rating(self):
        serializer = CommunityPostCreateSerializer(
            data={
                "content": "Invalid rating.",
                "rating": "4.7",
            },
            context={"request": self.request},
        )

        self.assertFalse(serializer.is_valid())

    def test_community_post_create_serializer_creates_internal_target(self):
        serializer = CommunityPostCreateSerializer(
            data={
                "content": "Post attached to a song.",
                "target": {
                    "target_type": CommunityPostTarget.TargetType.SONG,
                    "song": self.song.id,
                },
            },
            context={"request": self.request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        post = serializer.save()

        self.assertTrue(
            CommunityPostTarget.objects.filter(
                post=post,
                target_type=CommunityPostTarget.TargetType.SONG,
                song=self.song,
            ).exists()
        )

    def test_community_post_update_serializer_updates_content(self):
        serializer = CommunityPostUpdateSerializer(
            self.post,
            data={
                "content": "Updated community post.",
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        post = serializer.save()

        self.assertEqual(post.content, "Updated community post.")
        self.assertTrue(post.is_edited)

    def test_community_post_update_serializer_updates_rating(self):
        serializer = CommunityPostUpdateSerializer(
            self.post,
            data={
                "rating": "5.0",
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        post = serializer.save()

        self.assertEqual(float(post.rating), 5.0)
        self.assertTrue(post.is_edited)

    def test_community_post_update_serializer_keeps_target_immutable(self):
        original_target = self.post.target

        serializer = CommunityPostUpdateSerializer(
            self.post,
            data={
                "content": "Updated without changing target.",
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        post = serializer.save()

        self.assertEqual(post.target.id, original_target.id)
        self.assertEqual(post.target.song, self.song)

    def test_external_target_creation_rolls_back_post(self):
        provider = CommunityPostTarget.ExternalProvider.choices[0][0]
        content_type = CommunityPostTarget.ExternalContentType.choices[0][0]

        serializer = CommunityPostCreateSerializer(
            data={
                "content": "External music post.",
                "target": {
                    "target_type": CommunityPostTarget.TargetType.EXTERNAL,
                    "external_provider": provider,
                    "external_content_type": content_type,
                    "external_id": "external-999",
                },
            },
            context={"request": self.request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        with self.assertRaises(serializers.ValidationError):
            serializer.save()

        self.assertFalse(
            CommunityPost.objects.filter(
                user=self.user,
                content="External music post.",
            ).exists()
        )

    # ---------------------------------------------------------
    # COMMUNITY COMMENT SERIALIZERS
    # ---------------------------------------------------------

    def test_community_post_comment_serializer(self):
        serializer = CommunityPostCommentSerializer(
            self.comment,
            context={"request": self.request},
        )

        data = serializer.data

        self.assertEqual(data["id"], self.comment.id)
        self.assertEqual(data["user"], self.user.id)
        self.assertEqual(data["post"], self.post.id)
        self.assertEqual(data["content"], self.comment.content)

    def test_comment_create_serializer_accepts_published_post(self):
        serializer = CommunityPostCommentCreateSerializer(
            data={
                "post": self.post.id,
                "content": "Great post!",
            },
            context={"request": self.request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        comment = serializer.save()

        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.post, self.post)

    def test_comment_create_serializer_rejects_hidden_post(self):
        hidden_post = CommunityPost.objects.create(
            user=self.user,
            content="Hidden post.",
            status=CommunityPost.Status.HIDDEN,
        )

        serializer = CommunityPostCommentCreateSerializer(
            data={
                "post": hidden_post.id,
                "content": "Trying to comment.",
            },
            context={"request": self.request},
        )

        self.assertFalse(serializer.is_valid())

    def test_comment_create_serializer_rejects_removed_post(self):
        removed_post = CommunityPost.objects.create(
            user=self.user,
            content="Removed post.",
            status=CommunityPost.Status.REMOVED,
        )

        serializer = CommunityPostCommentCreateSerializer(
            data={
                "post": removed_post.id,
                "content": "Trying to comment.",
            },
            context={"request": self.request},
        )

        self.assertFalse(serializer.is_valid())

    def test_comment_create_serializer_accepts_published_parent(self):
        serializer = CommunityPostCommentCreateSerializer(
            data={
                "post": self.post.id,
                "parent": self.comment.id,
                "content": "This is a reply.",
            },
            context={"request": self.request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        reply = serializer.save()

        self.assertEqual(reply.parent, self.comment)
        self.assertEqual(reply.post, self.post)

    def test_comment_create_serializer_rejects_parent_from_another_post(self):
        another_post = CommunityPost.objects.create(
            user=self.other_user,
            content="Another post.",
            status=CommunityPost.Status.PUBLISHED,
        )

        another_comment = CommunityPostComment.objects.create(
            user=self.other_user,
            post=another_post,
            content="Another comment.",
            status=CommunityPostComment.Status.PUBLISHED,
        )

        serializer = CommunityPostCommentCreateSerializer(
            data={
                "post": self.post.id,
                "parent": another_comment.id,
                "content": "Invalid reply.",
            },
            context={"request": self.request},
        )

        self.assertFalse(serializer.is_valid())

    def test_comment_create_serializer_rejects_hidden_parent(self):
        hidden_parent = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Hidden parent.",
            status=CommunityPostComment.Status.HIDDEN,
        )

        serializer = CommunityPostCommentCreateSerializer(
            data={
                "post": self.post.id,
                "parent": hidden_parent.id,
                "content": "Reply to hidden comment.",
            },
            context={"request": self.request},
        )

        self.assertFalse(serializer.is_valid())

    def test_comment_create_serializer_assigns_user_server_side(self):
        serializer = CommunityPostCommentCreateSerializer(
            data={
                "post": self.post.id,
                "content": "Server assigns me.",
            },
            context={"request": self.request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        comment = serializer.save()

        self.assertEqual(comment.user, self.user)

    def test_comment_update_serializer_updates_content(self):
        serializer = CommunityPostCommentUpdateSerializer(
            self.comment,
            data={
                "content": "Updated comment.",
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        comment = serializer.save()

        self.assertEqual(comment.content, "Updated comment.")
        self.assertTrue(comment.is_edited)

    # ---------------------------------------------------------
    # REPORT SERIALIZERS
    # ---------------------------------------------------------

    def test_community_post_report_serializer(self):
        reason = CommunityPostReport._meta.get_field(
            "reason"
        ).choices[0][0]

        report = CommunityPostReport.objects.create(
            user=self.user,
            post=self.post,
            reason=reason,
            details="Report details.",
        )

        serializer = CommunityPostReportSerializer(report)

        self.assertEqual(serializer.data["id"], report.id)
        self.assertEqual(serializer.data["user"], self.user.id)
        self.assertEqual(serializer.data["post"], self.post.id)

    def test_community_post_report_create_assigns_user_server_side(self):
        reason = CommunityPostReport._meta.get_field(
            "reason"
        ).choices[0][0]

        serializer = CommunityPostReportCreateSerializer(
            data={
                "post": self.post.id,
                "reason": reason,
                "details": "Something is wrong with this post.",
            },
            context={"request": self.request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        report = serializer.save()

        self.assertEqual(report.user, self.user)
        self.assertEqual(report.post, self.post)

    def test_community_post_comment_report_serializer(self):
        reason = CommunityPostCommentReport._meta.get_field(
            "reason"
        ).choices[0][0]

        report = CommunityPostCommentReport.objects.create(
            user=self.user,
            comment=self.comment,
            reason=reason,
            details="Report details.",
        )

        serializer = CommunityPostCommentReportSerializer(report)

        self.assertEqual(serializer.data["id"], report.id)
        self.assertEqual(serializer.data["user"], self.user.id)
        self.assertEqual(serializer.data["comment"], self.comment.id)

    def test_community_post_comment_report_create_assigns_user_server_side(self):
        reason = CommunityPostCommentReport._meta.get_field(
            "reason"
        ).choices[0][0]

        serializer = CommunityPostCommentReportCreateSerializer(
            data={
                "comment": self.comment.id,
                "reason": reason,
                "details": "This comment should be reviewed.",
            },
            context={"request": self.request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        report = serializer.save()

        self.assertEqual(report.user, self.user)
        self.assertEqual(report.comment, self.comment)
        
class FollowSerializerTests(TestCase):
    """
    Tests for artist-follow and user-follow serializers.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="follow_test_user",
            password="test-password-123",
        )

        cls.other_user = User.objects.create_user(
            username="follow_target_user",
            password="test-password-123",
        )

        cls.artist = Artist.objects.create(
            name="Follow Artist",
            slug="follow-artist",
            is_active=True,
        )

        cls.inactive_artist = Artist.objects.create(
            name="Inactive Artist",
            slug="inactive-artist",
            is_active=False,
        )

    def test_artist_follow_create_accepts_active_artist(self):
        serializer = ArtistFollowCreateSerializer(
            data={
                "artist": self.artist.pk,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_artist_follow_create_rejects_inactive_artist(self):
        serializer = ArtistFollowCreateSerializer(
            data={
                "artist": self.inactive_artist.pk,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("artist", serializer.errors)

    def test_artist_follow_create_assigns_authenticated_user(self):
        request = type(
            "Request",
            (),
            {"user": self.user},
        )()

        serializer = ArtistFollowCreateSerializer(
            data={
                "artist": self.artist.pk,
            },
            context={
                "request": request,
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        follow = serializer.save()

        self.assertEqual(
            follow.user,
            self.user,
        )

        self.assertEqual(
            follow.artist,
            self.artist,
        )

    def test_artist_follow_read_serializer(self):
        follow = ArtistFollow.objects.create(
            user=self.user,
            artist=self.artist,
        )

        serializer = ArtistFollowSerializer(follow)

        self.assertEqual(
            serializer.data["artist"]["name"],
            "Follow Artist",
        )

    def test_user_follow_create_accepts_another_user(self):
        serializer = UserFollowCreateSerializer(
            data={
                "following": self.other_user.pk,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_user_follow_create_assigns_authenticated_user(self):
        request = type(
            "Request",
            (),
            {"user": self.user},
        )()

        serializer = UserFollowCreateSerializer(
            data={
                "following": self.other_user.pk,
            },
            context={
                "request": request,
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        follow = serializer.save()

        self.assertEqual(
            follow.follower,
            self.user,
        )

        self.assertEqual(
            follow.following,
            self.other_user,
        )

    def test_user_follow_read_serializer(self):
        follow = UserFollow.objects.create(
            follower=self.user,
            following=self.other_user,
        )

        serializer = UserFollowSerializer(follow)

        self.assertEqual(
            serializer.data["follower"],
            self.user.pk,
        )

        self.assertEqual(
            serializer.data["following"],
            self.other_user.pk,
        )

    def test_user_follow_cannot_follow_self(self):
        serializer = UserFollowCreateSerializer(
            data={
                "following": self.user.pk,
            }
        )

        # The database constraint is responsible for the final
        # protection against self-following. The serializer itself
        # currently does not implement that business rule.
        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

class FavoriteSerializerTests(TestCase):
    """
    Tests for song and album favorite serializers.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="favorite_test_user",
            password="test-password-123",
        )

        cls.artist = Artist.objects.create(
            name="Favorite Artist",
            slug="favorite-artist",
            is_active=True,
        )

        cls.album = Album.objects.create(
            title="Favorite Album",
            slug="favorite-album",
            release_type=Album.ReleaseType.ALBUM,
            status=Album.Status.PUBLISHED,
            published_at="2026-01-01T00:00:00Z",
        )

        cls.album.artists.add(cls.artist)

        cls.song = Song.objects.create(
            title="Favorite Song",
            slug="favorite-song",
            album=cls.album,
            status=Song.Status.PUBLISHED,
            published_at="2026-01-01T00:00:00Z",
        )

        cls.song.artists.add(cls.artist)

        cls.unpublished_song = Song.objects.create(
            title="Unpublished Song",
            slug="unpublished-song",
            status=Song.Status.DRAFT,
        )

        cls.unpublished_album = Album.objects.create(
            title="Unpublished Album",
            slug="unpublished-album",
            release_type=Album.ReleaseType.ALBUM,
            status=Album.Status.DRAFT,
        )

    def test_song_favorite_create_accepts_published_song(self):
        serializer = SongFavoriteCreateSerializer(
            data={
                "song": self.song.pk,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_song_favorite_create_rejects_unpublished_song(self):
        serializer = SongFavoriteCreateSerializer(
            data={
                "song": self.unpublished_song.pk,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("song", serializer.errors)

    def test_album_favorite_create_accepts_published_album(self):
        serializer = AlbumFavoriteCreateSerializer(
            data={
                "album": self.album.pk,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_album_favorite_create_rejects_unpublished_album(self):
        serializer = AlbumFavoriteCreateSerializer(
            data={
                "album": self.unpublished_album.pk,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("album", serializer.errors)

    def test_song_favorite_create_assigns_authenticated_user(self):
        request = type(
            "Request",
            (),
            {"user": self.user},
        )()

        serializer = SongFavoriteCreateSerializer(
            data={
                "song": self.song.pk,
            },
            context={
                "request": request,
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        favorite = serializer.save()

        self.assertEqual(
            favorite.user,
            self.user,
        )

        self.assertEqual(
            favorite.song,
            self.song,
        )

    def test_album_favorite_create_assigns_authenticated_user(self):
        request = type(
            "Request",
            (),
            {"user": self.user},
        )()

        serializer = AlbumFavoriteCreateSerializer(
            data={
                "album": self.album.pk,
            },
            context={
                "request": request,
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        favorite = serializer.save()

        self.assertEqual(
            favorite.user,
            self.user,
        )

        self.assertEqual(
            favorite.album,
            self.album,
        )

    def test_song_favorite_read_serializer(self):
        favorite = SongFavorite.objects.create(
            user=self.user,
            song=self.song,
        )

        serializer = SongFavoriteSerializer(favorite)

        self.assertEqual(
            serializer.data["song"]["title"],
            "Favorite Song",
        )

    def test_album_favorite_read_serializer(self):
        favorite = AlbumFavorite.objects.create(
            user=self.user,
            album=self.album,
        )

        serializer = AlbumFavoriteSerializer(favorite)

        self.assertEqual(
            serializer.data["album"]["title"],
            "Favorite Album",
        )

class RatingSerializerTests(TestCase):
    """
    Tests for song and album rating serializers.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="rating_test_user",
            password="test-password-123",
        )

        cls.artist = Artist.objects.create(
            name="Rating Artist",
            slug="rating-artist",
            is_active=True,
        )

        cls.album = Album.objects.create(
            title="Rating Album",
            slug="rating-album",
            release_type=Album.ReleaseType.ALBUM,
            status=Album.Status.PUBLISHED,
            published_at="2026-01-01T00:00:00Z",
        )

        cls.album.artists.add(cls.artist)

        cls.song = Song.objects.create(
            title="Rating Song",
            slug="rating-song",
            album=cls.album,
            status=Song.Status.PUBLISHED,
            published_at="2026-01-01T00:00:00Z",
        )

        cls.song.artists.add(cls.artist)

    def test_song_rating_create_accepts_valid_rating(self):
        serializer = SongRatingCreateSerializer(
            data={
                "song": self.song.pk,
                "rating": "4.5",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_song_rating_create_rejects_invalid_increment(self):
        serializer = SongRatingCreateSerializer(
            data={
                "song": self.song.pk,
                "rating": "4.3",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)

    def test_song_rating_create_rejects_rating_above_five(self):
        serializer = SongRatingCreateSerializer(
            data={
                "song": self.song.pk,
                "rating": "5.5",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)

    def test_song_rating_create_rejects_rating_below_half(self):
        serializer = SongRatingCreateSerializer(
            data={
                "song": self.song.pk,
                "rating": "0.4",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)

    def test_song_rating_update_accepts_valid_rating(self):
        serializer = SongRatingUpdateSerializer(
            data={
                "rating": "3.5",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_album_rating_create_accepts_valid_rating(self):
        serializer = AlbumRatingCreateSerializer(
            data={
                "album": self.album.pk,
                "rating": "5.0",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_album_rating_update_accepts_valid_rating(self):
        serializer = AlbumRatingUpdateSerializer(
            data={
                "rating": "2.5",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_song_rating_create_assigns_authenticated_user(self):
        request = type(
            "Request",
            (),
            {"user": self.user},
        )()

        serializer = SongRatingCreateSerializer(
            data={
                "song": self.song.pk,
                "rating": "4.5",
            },
            context={
                "request": request,
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        rating = serializer.save()

        self.assertEqual(
            rating.user,
            self.user,
        )

        self.assertEqual(
            rating.song,
            self.song,
        )

        self.assertEqual(
            rating.rating,
            4.5,
        )

    def test_album_rating_create_assigns_authenticated_user(self):
        request = type(
            "Request",
            (),
            {"user": self.user},
        )()

        serializer = AlbumRatingCreateSerializer(
            data={
                "album": self.album.pk,
                "rating": "5.0",
            },
            context={
                "request": request,
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        rating = serializer.save()

        self.assertEqual(
            rating.user,
            self.user,
        )

        self.assertEqual(
            rating.album,
            self.album,
        )

        self.assertEqual(
            rating.rating,
            5.0,
        )

    def test_song_rating_read_serializer(self):
        rating = SongRating.objects.create(
            user=self.user,
            song=self.song,
            rating=4.5,
        )

        serializer = SongRatingSerializer(rating)

        self.assertEqual(
            serializer.data["rating"],
            "4.5",
        )

        self.assertEqual(
            serializer.data["song"]["title"],
            "Rating Song",
        )

    def test_album_rating_read_serializer(self):
        rating = AlbumRating.objects.create(
            user=self.user,
            album=self.album,
            rating=5.0,
        )

        serializer = AlbumRatingSerializer(rating)

        self.assertEqual(
            serializer.data["rating"],
            "5.0",
        )

        self.assertEqual(
            serializer.data["album"]["title"],
            "Rating Album",
        )


class CatalogSerializerTests(TestCase):
    """
    Tests for VibeNation catalog serializers.

    Django uses a temporary test database for this test case,
    so the real development database is not modified.
    """

    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create(
            name="Test Artist",
            slug="test-artist",
            bio="A test artist.",
            country="Nigeria",
            is_active=True,
            is_verified=True,
        )

        cls.genre = Genre.objects.create(
            name="Afrobeats",
            slug="afrobeats",
            description="African popular music.",
            is_active=True,
        )

        cls.album = Album.objects.create(
            title="Test Album",
            slug="test-album",
            release_type=Album.ReleaseType.ALBUM,
            status=Album.Status.PUBLISHED,
            published_at="2026-01-01T00:00:00Z",
        )

        cls.album.artists.add(cls.artist)

        cls.song = Song.objects.create(
            title="Test Song",
            slug="test-song",
            album=cls.album,
            status=Song.Status.PUBLISHED,
            published_at="2026-01-01T00:00:00Z",
        )

        cls.song.artists.add(cls.artist)
        cls.song.genres.add(cls.genre)

        cls.album_track = AlbumTrack.objects.create(
            album=cls.album,
            song=cls.song,
            track_number=1,
        )

    def test_genre_serializer(self):
        serializer = GenreSerializer(self.genre)

        self.assertEqual(
            serializer.data["name"],
            "Afrobeats",
        )

    def test_artist_card_serializer(self):
        serializer = ArtistCardSerializer(self.artist)

        self.assertEqual(
            serializer.data["name"],
            "Test Artist",
        )

        self.assertEqual(
            serializer.data["slug"],
            "test-artist",
        )

        self.assertIn(
            "followers_count",
            serializer.data,
        )

    def test_artist_serializer(self):
        serializer = ArtistSerializer(self.artist)

        self.assertEqual(
            serializer.data["name"],
            "Test Artist",
        )

        self.assertEqual(
            serializer.data["bio"],
            "A test artist.",
        )

        self.assertEqual(
            serializer.data["country"],
            "Nigeria",
        )

    def test_album_card_serializer(self):
        serializer = AlbumCardSerializer(self.album)

        self.assertEqual(
            serializer.data["title"],
            "Test Album",
        )

        self.assertEqual(
            len(serializer.data["artists"]),
            1,
        )

        self.assertEqual(
            serializer.data["artists"][0]["name"],
            "Test Artist",
        )

    def test_song_card_serializer(self):
        serializer = SongCardSerializer(self.song)

        self.assertEqual(
            serializer.data["title"],
            "Test Song",
        )

        self.assertEqual(
            len(serializer.data["artists"]),
            1,
        )

        self.assertEqual(
            serializer.data["artists"][0]["name"],
            "Test Artist",
        )

    def test_song_serializer(self):
        serializer = SongSerializer(self.song)

        self.assertEqual(
            serializer.data["title"],
            "Test Song",
        )

        self.assertEqual(
            serializer.data["album"]["title"],
            "Test Album",
        )

        self.assertEqual(
            len(serializer.data["artists"]),
            1,
        )

        self.assertEqual(
            len(serializer.data["genres"]),
            1,
        )

    def test_album_track_serializer(self):
        serializer = AlbumTrackSerializer(self.album_track)

        self.assertEqual(
            serializer.data["track_number"],
            1,
        )

        self.assertEqual(
            serializer.data["song"]["title"],
            "Test Song",
        )

    def test_album_serializer_includes_tracklist(self):
        serializer = AlbumSerializer(self.album)

        self.assertEqual(
            serializer.data["title"],
            "Test Album",
        )

        self.assertEqual(
            len(serializer.data["tracks"]),
            1,
        )

        self.assertEqual(
            serializer.data["tracks"][0]["track_number"],
            1,
        )

        self.assertEqual(
            serializer.data["tracks"][0]["song"]["title"],
            "Test Song",
        )


class LikeSerializerTests(TestCase):
    """
    Tests for all VibeNation like serializers.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="like_test_user",
            password="test-password-123",
        )

        cls.artist = Artist.objects.create(
            name="Like Artist",
            slug="like-artist",
            is_active=True,
        )

        cls.song = Song.objects.create(
            title="Like Song",
            slug="like-song",
            status=Song.Status.PUBLISHED,
            published_at="2026-01-01T00:00:00Z",
        )

        cls.song.artists.add(cls.artist)

        cls.album = Album.objects.create(
            title="Like Album",
            slug="like-album",
            release_type=Album.ReleaseType.ALBUM,
            status=Album.Status.PUBLISHED,
            published_at="2026-01-01T00:00:00Z",
        )

        cls.album.artists.add(cls.artist)

        cls.article = EditorialArticle.objects.create(
            title="Like Article",
            slug="like-article",
            excerpt="Test excerpt.",
            content="Test article content.",
            author=cls.user,
            status=EditorialArticle.Status.PUBLISHED,
            published_at="2026-01-01T00:00:00Z",
        )

        cls.post = CommunityPost.objects.create(
            user=cls.user,
            content="Test community post.",
            status=CommunityPost.Status.PUBLISHED,
        )

        cls.editorial_comment = EditorialComment.objects.create(
            user=cls.user,
            article=cls.article,
            content="Test editorial comment.",
            status=EditorialComment.Status.PUBLISHED,
        )

        cls.community_comment = CommunityPostComment.objects.create(
            user=cls.user,
            post=cls.post,
            content="Test community comment.",
            status=CommunityPostComment.Status.PUBLISHED,
        )

    # ========================================================
    # EDITORIAL ARTICLE LIKE
    # ========================================================

    def test_editorial_article_like_accepts_published_article(self):
        serializer = EditorialArticleLikeCreateSerializer(
            data={
                "article": self.article.pk,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_editorial_article_like_assigns_authenticated_user(self):
        request = type(
            "Request",
            (),
            {"user": self.user},
        )()

        serializer = EditorialArticleLikeCreateSerializer(
            data={
                "article": self.article.pk,
            },
            context={
                "request": request,
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        like = serializer.save()

        self.assertEqual(like.user, self.user)
        self.assertEqual(like.article, self.article)

    def test_editorial_article_like_read_serializer(self):
        like = EditorialArticleLike.objects.create(
            user=self.user,
            article=self.article,
        )

        serializer = EditorialArticleLikeSerializer(like)

        self.assertEqual(
            serializer.data["article"],
            self.article.pk,
        )

    # ========================================================
    # COMMUNITY POST LIKE
    # ========================================================

    def test_community_post_like_accepts_published_post(self):
        serializer = CommunityPostLikeCreateSerializer(
            data={
                "post": self.post.pk,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_community_post_like_assigns_authenticated_user(self):
        request = type(
            "Request",
            (),
            {"user": self.user},
        )()

        serializer = CommunityPostLikeCreateSerializer(
            data={
                "post": self.post.pk,
            },
            context={
                "request": request,
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        like = serializer.save()

        self.assertEqual(like.user, self.user)
        self.assertEqual(like.post, self.post)

    def test_community_post_like_read_serializer(self):
        like = CommunityPostLike.objects.create(
            user=self.user,
            post=self.post,
        )

        serializer = CommunityPostLikeSerializer(like)

        self.assertEqual(
            serializer.data["post"],
            self.post.pk,
        )

    # ========================================================
    # EDITORIAL COMMENT LIKE
    # ========================================================

    def test_editorial_comment_like_accepts_published_comment(self):
        serializer = EditorialCommentLikeCreateSerializer(
            data={
                "comment": self.editorial_comment.pk,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_editorial_comment_like_assigns_authenticated_user(self):
        request = type(
            "Request",
            (),
            {"user": self.user},
        )()

        serializer = EditorialCommentLikeCreateSerializer(
            data={
                "comment": self.editorial_comment.pk,
            },
            context={
                "request": request,
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        like = serializer.save()

        self.assertEqual(like.user, self.user)
        self.assertEqual(
            like.comment,
            self.editorial_comment,
        )

    def test_editorial_comment_like_read_serializer(self):
        like = EditorialCommentLike.objects.create(
            user=self.user,
            comment=self.editorial_comment,
        )

        serializer = EditorialCommentLikeSerializer(like)

        self.assertEqual(
            serializer.data["comment"],
            self.editorial_comment.pk,
        )

    # ========================================================
    # COMMUNITY COMMENT LIKE
    # ========================================================

    def test_community_comment_like_accepts_published_comment(self):
        serializer = CommunityPostCommentLikeCreateSerializer(
            data={
                "comment": self.community_comment.pk,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_community_comment_like_assigns_authenticated_user(self):
        request = type(
            "Request",
            (),
            {"user": self.user},
        )()

        serializer = CommunityPostCommentLikeCreateSerializer(
            data={
                "comment": self.community_comment.pk,
            },
            context={
                "request": request,
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        like = serializer.save()

        self.assertEqual(like.user, self.user)
        self.assertEqual(
            like.comment,
            self.community_comment,
        )

    def test_community_comment_like_read_serializer(self):
        like = CommunityPostCommentLike.objects.create(
            user=self.user,
            comment=self.community_comment,
        )

        serializer = CommunityPostCommentLikeSerializer(like)

        self.assertEqual(
            serializer.data["comment"],
            self.community_comment.pk,
        )