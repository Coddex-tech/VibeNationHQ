from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from rest_framework.exceptions import ValidationError

from music.models import (
    Album,
    Artist,
    Song,
    SongRating,
    AlbumRating,
    AlbumFavorite,
    SongFavorite,
    UserFollow,
    ArtistFollow,
    EditorialComment,
    CommunityPost,
    CommunityPostComment,
    CommunityPostCommentLike,
    CommunityPostLike,
    EditorialArticle,
    EditorialArticleLike,
    EditorialCommentLike,
    EditorialArticleReport,
    CommunityPostReport,
    EditorialCommentReport,
    CommunityPostCommentReport,

)

from music.services.ratings import (
    SongRatingService,
    AlbumRatingService,
)

from music.services.favorites import (
    SongFavoriteService,
    AlbumFavoriteService,
)

from music.services.follows import (
    ArtistFollowService,
    UserFollowService,
)

from music.services.likes import (
    EditorialArticleLikeService,
    CommunityPostLikeService,
    EditorialCommentLikeService,
    CommunityPostCommentLikeService,
)

from music.services.community import (
    CommunityPostService,
    CommunityPostTarget,
    CommunityPostCommentService,
    CommunityPostReport,
    EditorialArticleReport,
    EditorialArticleReportService,
    EditorialCommentReportService,
    CommunityPostReportService,
    CommunityPostCommentReportService
)


User = get_user_model()


class RatingServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ratinguser",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="otherratinguser",
            password="testpass123",
        )

        self.artist = Artist.objects.create(
            name="Rating Artist",
            slug="rating-artist",
            is_active=True,
        )

        self.song = Song.objects.create(
            title="Rating Song",
            slug="rating-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.song.artists.add(self.artist)

        self.album = Album.objects.create(
            title="Rating Album",
            slug="rating-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.album.artists.add(self.artist)

    # ========================================================
    # SONG RATING SERVICE
    # ========================================================

    def test_create_song_rating(self):
        rating = SongRatingService.create(
            user=self.user,
            song=self.song,
            rating=4.5,
        )

        self.assertEqual(rating.user, self.user)
        self.assertEqual(rating.song, self.song)
        self.assertEqual(float(rating.rating), 4.5)

        self.song.refresh_from_db()

        self.assertEqual(self.song.ratings_count, 1)

    def test_create_song_rating_rejects_duplicate(self):
        SongRating.objects.create(
            user=self.user,
            song=self.song,
            rating=4.0,
        )

        with self.assertRaises(ValidationError):
            SongRatingService.create(
                user=self.user,
                song=self.song,
                rating=5.0,
            )

        self.song.refresh_from_db()

        self.assertEqual(self.song.ratings_count, 0)

    def test_create_song_rating_rejects_unpublished_song(self):
        draft_song = Song.objects.create(
            title="Draft Rating Song",
            slug="draft-rating-song",
            status=Song.Status.DRAFT,
        )

        with self.assertRaises(ValidationError):
            SongRatingService.create(
                user=self.user,
                song=draft_song,
                rating=4.0,
            )

        self.assertFalse(
            SongRating.objects.filter(
                user=self.user,
                song=draft_song,
            ).exists()
        )

    def test_create_song_rating_allows_different_users(self):
        first_rating = SongRatingService.create(
            user=self.user,
            song=self.song,
            rating=4.0,
        )

        second_rating = SongRatingService.create(
            user=self.other_user,
            song=self.song,
            rating=5.0,
        )

        self.assertNotEqual(
            first_rating.id,
            second_rating.id,
        )

        self.song.refresh_from_db()

        self.assertEqual(self.song.ratings_count, 2)

    def test_update_song_rating(self):
        rating = SongRatingService.create(
            user=self.user,
            song=self.song,
            rating=3.5,
        )

        updated_rating = SongRatingService.update(
            rating_instance=rating,
            rating=5.0,
        )

        updated_rating.refresh_from_db()
        self.song.refresh_from_db()

        self.assertEqual(float(updated_rating.rating), 5.0)
        self.assertEqual(self.song.ratings_count, 1)

    def test_update_song_rating_does_not_change_counter(self):
        rating = SongRatingService.create(
            user=self.user,
            song=self.song,
            rating=3.0,
        )

        SongRatingService.update(
            rating_instance=rating,
            rating=4.5,
        )

        self.song.refresh_from_db()

        self.assertEqual(self.song.ratings_count, 1)

    def test_delete_song_rating(self):
        rating = SongRatingService.create(
            user=self.user,
            song=self.song,
            rating=4.0,
        )

        self.song.refresh_from_db()
        self.assertEqual(self.song.ratings_count, 1)

        SongRatingService.delete(
            rating_instance=rating,
        )

        self.song.refresh_from_db()

        self.assertEqual(self.song.ratings_count, 0)

        self.assertFalse(
            SongRating.objects.filter(
                pk=rating.pk,
            ).exists()
        )

    def test_delete_song_rating_decrements_correctly_with_multiple_ratings(self):
        first_rating = SongRatingService.create(
            user=self.user,
            song=self.song,
            rating=4.0,
        )

        SongRatingService.create(
            user=self.other_user,
            song=self.song,
            rating=5.0,
        )

        self.song.refresh_from_db()

        self.assertEqual(self.song.ratings_count, 2)

        SongRatingService.delete(
            rating_instance=first_rating,
        )

        self.song.refresh_from_db()

        self.assertEqual(self.song.ratings_count, 1)

    def test_delete_song_rating_does_not_make_counter_negative(self):
        rating = SongRating.objects.create(
            user=self.user,
            song=self.song,
            rating=4.0,
        )

        self.song.ratings_count = 0
        self.song.save(update_fields=["ratings_count"])

        SongRatingService.delete(
            rating_instance=rating,
        )

        self.song.refresh_from_db()

        self.assertEqual(self.song.ratings_count, 0)

    # ========================================================
    # ALBUM RATING SERVICE
    # ========================================================

    def test_create_album_rating(self):
        rating = AlbumRatingService.create(
            user=self.user,
            album=self.album,
            rating=4.5,
        )

        self.assertEqual(rating.user, self.user)
        self.assertEqual(rating.album, self.album)
        self.assertEqual(float(rating.rating), 4.5)

        self.album.refresh_from_db()

        self.assertEqual(self.album.ratings_count, 1)

    def test_create_album_rating_rejects_duplicate(self):
        AlbumRating.objects.create(
            user=self.user,
            album=self.album,
            rating=4.0,
        )

        with self.assertRaises(ValidationError):
            AlbumRatingService.create(
                user=self.user,
                album=self.album,
                rating=5.0,
            )

        self.album.refresh_from_db()

        self.assertEqual(self.album.ratings_count, 0)

    def test_create_album_rating_rejects_unpublished_album(self):
        draft_album = Album.objects.create(
            title="Draft Rating Album",
            slug="draft-rating-album",
            status=Album.Status.DRAFT,
        )

        with self.assertRaises(ValidationError):
            AlbumRatingService.create(
                user=self.user,
                album=draft_album,
                rating=4.0,
            )

        self.assertFalse(
            AlbumRating.objects.filter(
                user=self.user,
                album=draft_album,
            ).exists()
        )

    def test_create_album_rating_allows_different_users(self):
        first_rating = AlbumRatingService.create(
            user=self.user,
            album=self.album,
            rating=4.0,
        )

        second_rating = AlbumRatingService.create(
            user=self.other_user,
            album=self.album,
            rating=5.0,
        )

        self.assertNotEqual(
            first_rating.id,
            second_rating.id,
        )

        self.album.refresh_from_db()

        self.assertEqual(self.album.ratings_count, 2)

    def test_update_album_rating(self):
        rating = AlbumRatingService.create(
            user=self.user,
            album=self.album,
            rating=3.5,
        )

        updated_rating = AlbumRatingService.update(
            rating_instance=rating,
            rating=5.0,
        )

        updated_rating.refresh_from_db()
        self.album.refresh_from_db()

        self.assertEqual(float(updated_rating.rating), 5.0)
        self.assertEqual(self.album.ratings_count, 1)

    def test_update_album_rating_does_not_change_counter(self):
        rating = AlbumRatingService.create(
            user=self.user,
            album=self.album,
            rating=3.0,
        )

        AlbumRatingService.update(
            rating_instance=rating,
            rating=4.5,
        )

        self.album.refresh_from_db()

        self.assertEqual(self.album.ratings_count, 1)

    def test_delete_album_rating(self):
        rating = AlbumRatingService.create(
            user=self.user,
            album=self.album,
            rating=4.0,
        )

        self.album.refresh_from_db()
        self.assertEqual(self.album.ratings_count, 1)

        AlbumRatingService.delete(
            rating_instance=rating,
        )

        self.album.refresh_from_db()

        self.assertEqual(self.album.ratings_count, 0)

        self.assertFalse(
            AlbumRating.objects.filter(
                pk=rating.pk,
            ).exists()
        )

    def test_delete_album_rating_decrements_correctly_with_multiple_ratings(self):
        first_rating = AlbumRatingService.create(
            user=self.user,
            album=self.album,
            rating=4.0,
        )

        AlbumRatingService.create(
            user=self.other_user,
            album=self.album,
            rating=5.0,
        )

        self.album.refresh_from_db()

        self.assertEqual(self.album.ratings_count, 2)

        AlbumRatingService.delete(
            rating_instance=first_rating,
        )

        self.album.refresh_from_db()

        self.assertEqual(self.album.ratings_count, 1)

    def test_delete_album_rating_does_not_make_counter_negative(self):
        rating = AlbumRating.objects.create(
            user=self.user,
            album=self.album,
            rating=4.0,
        )

        self.album.ratings_count = 0
        self.album.save(update_fields=["ratings_count"])

        AlbumRatingService.delete(
            rating_instance=rating,
        )

        self.album.refresh_from_db()

        self.assertEqual(self.album.ratings_count, 0)


class FavoriteServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="favoriteuser",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="otherfavoriteuser",
            password="testpass123",
        )

        self.artist = Artist.objects.create(
            name="Favorite Artist",
            slug="favorite-artist",
            is_active=True,
        )

        self.song = Song.objects.create(
            title="Favorite Song",
            slug="favorite-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.song.artists.add(self.artist)

        self.album = Album.objects.create(
            title="Favorite Album",
            slug="favorite-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.album.artists.add(self.artist)

    # ========================================================
    # SONG FAVORITES
    # ========================================================

    def test_create_song_favorite(self):
        favorite = SongFavoriteService.create(
            user=self.user,
            song=self.song,
        )

        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.song, self.song)

        self.song.refresh_from_db()

        self.assertEqual(self.song.favorites_count, 1)

    def test_create_song_favorite_rejects_duplicate(self):
        SongFavorite.objects.create(
            user=self.user,
            song=self.song,
        )

        with self.assertRaises(ValidationError):
            SongFavoriteService.create(
                user=self.user,
                song=self.song,
            )

        self.song.refresh_from_db()

        self.assertEqual(self.song.favorites_count, 0)

    def test_create_song_favorite_rejects_unpublished_song(self):
        draft_song = Song.objects.create(
            title="Draft Favorite Song",
            slug="draft-favorite-song",
            status=Song.Status.DRAFT,
        )

        with self.assertRaises(ValidationError):
            SongFavoriteService.create(
                user=self.user,
                song=draft_song,
            )

        self.assertFalse(
            SongFavorite.objects.filter(
                user=self.user,
                song=draft_song,
            ).exists()
        )

    def test_create_song_favorite_allows_different_users(self):
        first_favorite = SongFavoriteService.create(
            user=self.user,
            song=self.song,
        )

        second_favorite = SongFavoriteService.create(
            user=self.other_user,
            song=self.song,
        )

        self.assertNotEqual(
            first_favorite.id,
            second_favorite.id,
        )

        self.song.refresh_from_db()

        self.assertEqual(self.song.favorites_count, 2)

    def test_delete_song_favorite(self):
        favorite = SongFavoriteService.create(
            user=self.user,
            song=self.song,
        )

        self.song.refresh_from_db()

        self.assertEqual(self.song.favorites_count, 1)

        SongFavoriteService.delete(
            favorite_instance=favorite,
        )

        self.song.refresh_from_db()

        self.assertEqual(self.song.favorites_count, 0)

        self.assertFalse(
            SongFavorite.objects.filter(
                pk=favorite.pk,
            ).exists()
        )

    def test_delete_song_favorite_decrements_correctly_with_multiple_favorites(self):
        first_favorite = SongFavoriteService.create(
            user=self.user,
            song=self.song,
        )

        SongFavoriteService.create(
            user=self.other_user,
            song=self.song,
        )

        self.song.refresh_from_db()

        self.assertEqual(self.song.favorites_count, 2)

        SongFavoriteService.delete(
            favorite_instance=first_favorite,
        )

        self.song.refresh_from_db()

        self.assertEqual(self.song.favorites_count, 1)

    def test_delete_song_favorite_does_not_make_counter_negative(self):
        favorite = SongFavorite.objects.create(
            user=self.user,
            song=self.song,
        )

        self.song.favorites_count = 0
        self.song.save(
            update_fields=["favorites_count"]
        )

        SongFavoriteService.delete(
            favorite_instance=favorite,
        )

        self.song.refresh_from_db()

        self.assertEqual(self.song.favorites_count, 0)

    # ========================================================
    # ALBUM FAVORITES
    # ========================================================

    def test_create_album_favorite(self):
        favorite = AlbumFavoriteService.create(
            user=self.user,
            album=self.album,
        )

        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.album, self.album)

        self.album.refresh_from_db()

        self.assertEqual(self.album.favorites_count, 1)

    def test_create_album_favorite_rejects_duplicate(self):
        AlbumFavorite.objects.create(
            user=self.user,
            album=self.album,
        )

        with self.assertRaises(ValidationError):
            AlbumFavoriteService.create(
                user=self.user,
                album=self.album,
            )

        self.album.refresh_from_db()

        self.assertEqual(self.album.favorites_count, 0)

    def test_create_album_favorite_rejects_unpublished_album(self):
        draft_album = Album.objects.create(
            title="Draft Favorite Album",
            slug="draft-favorite-album",
            status=Album.Status.DRAFT,
        )

        with self.assertRaises(ValidationError):
            AlbumFavoriteService.create(
                user=self.user,
                album=draft_album,
            )

        self.assertFalse(
            AlbumFavorite.objects.filter(
                user=self.user,
                album=draft_album,
            ).exists()
        )

    def test_create_album_favorite_allows_different_users(self):
        first_favorite = AlbumFavoriteService.create(
            user=self.user,
            album=self.album,
        )

        second_favorite = AlbumFavoriteService.create(
            user=self.other_user,
            album=self.album,
        )

        self.assertNotEqual(
            first_favorite.id,
            second_favorite.id,
        )

        self.album.refresh_from_db()

        self.assertEqual(self.album.favorites_count, 2)

    def test_delete_album_favorite(self):
        favorite = AlbumFavoriteService.create(
            user=self.user,
            album=self.album,
        )

        self.album.refresh_from_db()

        self.assertEqual(self.album.favorites_count, 1)

        AlbumFavoriteService.delete(
            favorite_instance=favorite,
        )

        self.album.refresh_from_db()

        self.assertEqual(self.album.favorites_count, 0)

        self.assertFalse(
            AlbumFavorite.objects.filter(
                pk=favorite.pk,
            ).exists()
        )

    def test_delete_album_favorite_decrements_correctly_with_multiple_favorites(self):
        first_favorite = AlbumFavoriteService.create(
            user=self.user,
            album=self.album,
        )

        AlbumFavoriteService.create(
            user=self.other_user,
            album=self.album,
        )

        self.album.refresh_from_db()

        self.assertEqual(self.album.favorites_count, 2)

        AlbumFavoriteService.delete(
            favorite_instance=first_favorite,
        )

        self.album.refresh_from_db()

        self.assertEqual(self.album.favorites_count, 1)

    def test_delete_album_favorite_does_not_make_counter_negative(self):
        favorite = AlbumFavorite.objects.create(
            user=self.user,
            album=self.album,
        )

        self.album.favorites_count = 0
        self.album.save(
            update_fields=["favorites_count"]
        )

        AlbumFavoriteService.delete(
            favorite_instance=favorite,
        )

        self.album.refresh_from_db()

        self.assertEqual(self.album.favorites_count, 0)


class FollowServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="followuser",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="otherfollowuser",
            password="testpass123",
        )

        self.third_user = User.objects.create_user(
            username="thirdfollowuser",
            password="testpass123",
        )

        self.artist = Artist.objects.create(
            name="Follow Artist",
            slug="follow-artist",
            is_active=True,
        )

    # ========================================================
    # ARTIST FOLLOWS
    # ========================================================

    def test_create_artist_follow(self):
        follow = ArtistFollowService.create(
            user=self.user,
            artist=self.artist,
        )

        self.assertEqual(follow.user, self.user)
        self.assertEqual(follow.artist, self.artist)

        self.artist.refresh_from_db()

        self.assertEqual(
            self.artist.followers_count,
            1,
        )

    def test_create_artist_follow_rejects_duplicate(self):
        ArtistFollow.objects.create(
            user=self.user,
            artist=self.artist,
        )

        with self.assertRaises(ValidationError):
            ArtistFollowService.create(
                user=self.user,
                artist=self.artist,
            )

        self.artist.refresh_from_db()

        self.assertEqual(
            self.artist.followers_count,
            0,
        )

    def test_create_artist_follow_rejects_inactive_artist(self):
        inactive_artist = Artist.objects.create(
            name="Inactive Follow Artist",
            slug="inactive-follow-artist",
            is_active=False,
        )

        with self.assertRaises(ValidationError):
            ArtistFollowService.create(
                user=self.user,
                artist=inactive_artist,
            )

        self.assertFalse(
            ArtistFollow.objects.filter(
                user=self.user,
                artist=inactive_artist,
            ).exists()
        )

    def test_create_artist_follow_allows_different_users(self):
        first_follow = ArtistFollowService.create(
            user=self.user,
            artist=self.artist,
        )

        second_follow = ArtistFollowService.create(
            user=self.other_user,
            artist=self.artist,
        )

        self.assertNotEqual(
            first_follow.id,
            second_follow.id,
        )

        self.artist.refresh_from_db()

        self.assertEqual(
            self.artist.followers_count,
            2,
        )

    def test_delete_artist_follow(self):
        follow = ArtistFollowService.create(
            user=self.user,
            artist=self.artist,
        )

        self.artist.refresh_from_db()

        self.assertEqual(
            self.artist.followers_count,
            1,
        )

        ArtistFollowService.delete(
            follow_instance=follow,
        )

        self.artist.refresh_from_db()

        self.assertEqual(
            self.artist.followers_count,
            0,
        )

        self.assertFalse(
            ArtistFollow.objects.filter(
                pk=follow.pk,
            ).exists()
        )

    def test_delete_artist_follow_decrements_correctly_with_multiple_followers(self):
        first_follow = ArtistFollowService.create(
            user=self.user,
            artist=self.artist,
        )

        ArtistFollowService.create(
            user=self.other_user,
            artist=self.artist,
        )

        self.artist.refresh_from_db()

        self.assertEqual(
            self.artist.followers_count,
            2,
        )

        ArtistFollowService.delete(
            follow_instance=first_follow,
        )

        self.artist.refresh_from_db()

        self.assertEqual(
            self.artist.followers_count,
            1,
        )

    def test_delete_artist_follow_does_not_make_counter_negative(self):
        follow = ArtistFollow.objects.create(
            user=self.user,
            artist=self.artist,
        )

        self.artist.followers_count = 0
        self.artist.save(
            update_fields=["followers_count"]
        )

        ArtistFollowService.delete(
            follow_instance=follow,
        )

        self.artist.refresh_from_db()

        self.assertEqual(
            self.artist.followers_count,
            0,
        )

    # ========================================================
    # USER FOLLOWS
    # ========================================================

    def test_create_user_follow(self):
        follow = UserFollowService.create(
            follower=self.user,
            following=self.other_user,
        )

        self.assertEqual(
            follow.follower,
            self.user,
        )

        self.assertEqual(
            follow.following,
            self.other_user,
        )

    def test_create_user_follow_rejects_duplicate(self):
        UserFollow.objects.create(
            follower=self.user,
            following=self.other_user,
        )

        with self.assertRaises(ValidationError):
            UserFollowService.create(
                follower=self.user,
                following=self.other_user,
            )

    def test_create_user_follow_rejects_self_follow(self):
        with self.assertRaises(ValidationError):
            UserFollowService.create(
                follower=self.user,
                following=self.user,
            )

        self.assertFalse(
            UserFollow.objects.filter(
                follower=self.user,
                following=self.user,
            ).exists()
        )

    def test_create_user_follow_allows_multiple_users(self):
        first_follow = UserFollowService.create(
            follower=self.user,
            following=self.other_user,
        )

        second_follow = UserFollowService.create(
            follower=self.user,
            following=self.third_user,
        )

        self.assertNotEqual(
            first_follow.id,
            second_follow.id,
        )

        self.assertEqual(
            UserFollow.objects.filter(
                follower=self.user,
            ).count(),
            2,
        )

    def test_create_user_follow_allows_following_in_both_directions(self):
        first_follow = UserFollowService.create(
            follower=self.user,
            following=self.other_user,
        )

        second_follow = UserFollowService.create(
            follower=self.other_user,
            following=self.user,
        )

        self.assertNotEqual(
            first_follow.id,
            second_follow.id,
        )

        self.assertEqual(
            UserFollow.objects.count(),
            2,
        )

    def test_delete_user_follow(self):
        follow = UserFollowService.create(
            follower=self.user,
            following=self.other_user,
        )

        UserFollowService.delete(
            follow_instance=follow,
        )

        self.assertFalse(
            UserFollow.objects.filter(
                pk=follow.pk,
            ).exists()
        )

    def test_delete_user_follow_is_safe_if_already_deleted(self):
        follow = UserFollow.objects.create(
            follower=self.user,
            following=self.other_user,
        )

        follow_id = follow.pk

        UserFollowService.delete(
            follow_instance=follow,
        )

        UserFollowService.delete(
            follow_instance=follow,
        )

        self.assertFalse(
            UserFollow.objects.filter(
                pk=follow_id,
            ).exists()
        )


class LikeServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="likeuser",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="otherlikeuser",
            password="testpass123",
        )

        self.artist = Artist.objects.create(
            name="Like Artist",
            slug="like-artist",
            is_active=True,
        )

        self.article = EditorialArticle.objects.create(
            title="Like Article",
            slug="like-article",
            excerpt="Article excerpt.",
            content="Article content.",
            author=self.user,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.post = CommunityPost.objects.create(
            user=self.user,
            content="Like community post.",
            status=CommunityPost.Status.PUBLISHED,
        )

        self.editorial_comment = EditorialComment.objects.create(
            user=self.user,
            article=self.article,
            content="Editorial comment.",
            status=EditorialComment.Status.PUBLISHED,
        )

        self.post_comment = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Community comment.",
            status=CommunityPostComment.Status.PUBLISHED,
        )

    # ========================================================
    # EDITORIAL ARTICLE LIKES
    # ========================================================

    def test_create_article_like(self):
        like = EditorialArticleLikeService.create(
            user=self.user,
            article=self.article,
        )

        self.assertEqual(like.user, self.user)
        self.assertEqual(like.article, self.article)

        self.article.refresh_from_db()

        self.assertEqual(self.article.likes_count, 1)

    def test_create_article_like_rejects_duplicate(self):
        EditorialArticleLike.objects.create(
            user=self.user,
            article=self.article,
        )

        with self.assertRaises(ValidationError):
            EditorialArticleLikeService.create(
                user=self.user,
                article=self.article,
            )

        self.article.refresh_from_db()

        self.assertEqual(self.article.likes_count, 0)

    def test_create_article_like_rejects_unpublished_article(self):
        draft = EditorialArticle.objects.create(
            title="Draft Article",
            slug="draft-article",
            excerpt="Draft.",
            content="Draft content.",
            author=self.user,
            status=EditorialArticle.Status.DRAFT,
        )

        with self.assertRaises(ValidationError):
            EditorialArticleLikeService.create(
                user=self.user,
                article=draft,
            )

        self.assertFalse(
            EditorialArticleLike.objects.filter(
                user=self.user,
                article=draft,
            ).exists()
        )

    def test_create_article_like_allows_different_users(self):
        EditorialArticleLikeService.create(
            user=self.user,
            article=self.article,
        )

        EditorialArticleLikeService.create(
            user=self.other_user,
            article=self.article,
        )

        self.article.refresh_from_db()

        self.assertEqual(self.article.likes_count, 2)

    def test_delete_article_like(self):
        like = EditorialArticleLikeService.create(
            user=self.user,
            article=self.article,
        )

        EditorialArticleLikeService.delete(
            like_instance=like,
        )

        self.article.refresh_from_db()

        self.assertEqual(self.article.likes_count, 0)

        self.assertFalse(
            EditorialArticleLike.objects.filter(
                pk=like.pk,
            ).exists()
        )

    # ========================================================
    # COMMUNITY POST LIKES
    # ========================================================

    def test_create_post_like(self):
        like = CommunityPostLikeService.create(
            user=self.user,
            post=self.post,
        )

        self.assertEqual(like.user, self.user)
        self.assertEqual(like.post, self.post)

        self.post.refresh_from_db()

        self.assertEqual(self.post.likes_count, 1)

    def test_create_post_like_rejects_duplicate(self):
        CommunityPostLike.objects.create(
            user=self.user,
            post=self.post,
        )

        with self.assertRaises(ValidationError):
            CommunityPostLikeService.create(
                user=self.user,
                post=self.post,
            )

        self.post.refresh_from_db()

        self.assertEqual(self.post.likes_count, 0)

    def test_create_post_like_rejects_hidden_post(self):
        hidden_post = CommunityPost.objects.create(
            user=self.user,
            content="Hidden post.",
            status=CommunityPost.Status.HIDDEN,
        )

        with self.assertRaises(ValidationError):
            CommunityPostLikeService.create(
                user=self.user,
                post=hidden_post,
            )

    def test_create_post_like_allows_different_users(self):
        CommunityPostLikeService.create(
            user=self.user,
            post=self.post,
        )

        CommunityPostLikeService.create(
            user=self.other_user,
            post=self.post,
        )

        self.post.refresh_from_db()

        self.assertEqual(self.post.likes_count, 2)

    def test_delete_post_like(self):
        like = CommunityPostLikeService.create(
            user=self.user,
            post=self.post,
        )

        CommunityPostLikeService.delete(
            like_instance=like,
        )

        self.post.refresh_from_db()

        self.assertEqual(self.post.likes_count, 0)

        self.assertFalse(
            CommunityPostLike.objects.filter(
                pk=like.pk,
            ).exists()
        )

    # ========================================================
    # EDITORIAL COMMENT LIKES
    # ========================================================

    def test_create_editorial_comment_like(self):
        like = EditorialCommentLikeService.create(
            user=self.user,
            comment=self.editorial_comment,
        )

        self.assertEqual(
            like.comment,
            self.editorial_comment,
        )

        self.editorial_comment.refresh_from_db()

        self.assertEqual(
            self.editorial_comment.likes_count,
            1,
        )

    def test_create_editorial_comment_like_rejects_duplicate(self):
        EditorialCommentLike.objects.create(
            user=self.user,
            comment=self.editorial_comment,
        )

        with self.assertRaises(ValidationError):
            EditorialCommentLikeService.create(
                user=self.user,
                comment=self.editorial_comment,
            )

    def test_create_editorial_comment_like_rejects_unpublished_comment(self):
        draft_comment = EditorialComment.objects.create(
            user=self.user,
            article=self.article,
            content="Draft comment.",
            status=EditorialComment.Status.HIDDEN,
        )

        with self.assertRaises(ValidationError):
            EditorialCommentLikeService.create(
                user=self.user,
                comment=draft_comment,
            )

    def test_create_editorial_comment_like_rejects_comment_on_unpublished_article(self):
        draft_article = EditorialArticle.objects.create(
            title="Unpublished Article",
            slug="unpublished-article",
            excerpt="Draft.",
            content="Draft content.",
            author=self.user,
            status=EditorialArticle.Status.DRAFT,
        )

        comment = EditorialComment.objects.create(
            user=self.user,
            article=draft_article,
            content="Comment.",
            status=EditorialComment.Status.PUBLISHED,
        )

        with self.assertRaises(ValidationError):
            EditorialCommentLikeService.create(
                user=self.user,
                comment=comment,
            )

    def test_delete_editorial_comment_like(self):
        like = EditorialCommentLikeService.create(
            user=self.user,
            comment=self.editorial_comment,
        )

        EditorialCommentLikeService.delete(
            like_instance=like,
        )

        self.editorial_comment.refresh_from_db()

        self.assertEqual(
            self.editorial_comment.likes_count,
            0,
        )

    # ========================================================
    # COMMUNITY POST COMMENT LIKES
    # ========================================================

    def test_create_post_comment_like(self):
        like = CommunityPostCommentLikeService.create(
            user=self.user,
            comment=self.post_comment,
        )

        self.assertEqual(
            like.comment,
            self.post_comment,
        )

        self.post_comment.refresh_from_db()

        self.assertEqual(
            self.post_comment.likes_count,
            1,
        )

    def test_create_post_comment_like_rejects_duplicate(self):
        CommunityPostCommentLike.objects.create(
            user=self.user,
            comment=self.post_comment,
        )

        with self.assertRaises(ValidationError):
            CommunityPostCommentLikeService.create(
                user=self.user,
                comment=self.post_comment,
            )

    def test_create_post_comment_like_rejects_hidden_comment(self):
        hidden_comment = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Hidden comment.",
            status=CommunityPostComment.Status.HIDDEN,
        )

        with self.assertRaises(ValidationError):
            CommunityPostCommentLikeService.create(
                user=self.user,
                comment=hidden_comment,
            )

    def test_create_post_comment_like_rejects_comment_on_hidden_post(self):
        hidden_post = CommunityPost.objects.create(
            user=self.user,
            content="Hidden post.",
            status=CommunityPost.Status.HIDDEN,
        )

        comment = CommunityPostComment.objects.create(
            user=self.user,
            post=hidden_post,
            content="Comment.",
            status=CommunityPostComment.Status.PUBLISHED,
        )

        with self.assertRaises(ValidationError):
            CommunityPostCommentLikeService.create(
                user=self.user,
                comment=comment,
            )

    def test_delete_post_comment_like(self):
        like = CommunityPostCommentLikeService.create(
            user=self.user,
            comment=self.post_comment,
        )

        CommunityPostCommentLikeService.delete(
            like_instance=like,
        )

        self.post_comment.refresh_from_db()

        self.assertEqual(
            self.post_comment.likes_count,
            0,
        )

        self.assertFalse(
            CommunityPostCommentLike.objects.filter(
                pk=like.pk,
            ).exists()
        )


class CommunityPostServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="communityuser",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="othercommunityuser",
            password="testpass123",
        )

        self.artist = Artist.objects.create(
            name="Community Artist",
            slug="community-artist",
            is_active=True,
        )

        self.song = Song.objects.create(
            title="Community Song",
            slug="community-song",
            status=Song.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        self.song.artists.add(self.artist)

        self.album = Album.objects.create(
            title="Community Album",
            slug="community-album",
            status=Album.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        self.album.artists.add(self.artist)

    def test_create_post_with_song_target(self):
        post = CommunityPostService.create(
            user=self.user,
            content="This song is seriously underrated.",
            rating=4.5,
            target_data={
                "target_type": CommunityPostTarget.TargetType.SONG,
                "song": self.song,
            },
        )

        self.assertEqual(post.user, self.user)
        self.assertEqual(
            post.content,
            "This song is seriously underrated.",
        )
        self.assertEqual(post.rating, 4.5)

        target = CommunityPostTarget.objects.get(post=post)

        self.assertEqual(
            target.target_type,
            CommunityPostTarget.TargetType.SONG,
        )
        self.assertEqual(target.song, self.song)

    def test_create_post_with_album_target(self):
        post = CommunityPostService.create(
            user=self.user,
            content="Great album from start to finish.",
            rating=5.0,
            target_data={
                "target_type": CommunityPostTarget.TargetType.ALBUM,
                "album": self.album,
            },
        )

        target = CommunityPostTarget.objects.get(post=post)

        self.assertEqual(
            target.target_type,
            CommunityPostTarget.TargetType.ALBUM,
        )
        self.assertEqual(target.album, self.album)

    def test_create_post_with_artist_target(self):
        post = CommunityPostService.create(
            user=self.user,
            content="This artist deserves way more attention.",
            target_data={
                "target_type": CommunityPostTarget.TargetType.ARTIST,
                "artist": self.artist,
            },
        )

        target = CommunityPostTarget.objects.get(post=post)

        self.assertEqual(
            target.target_type,
            CommunityPostTarget.TargetType.ARTIST,
        )
        self.assertEqual(target.artist, self.artist)

    def test_external_target_is_rejected(self):
        with self.assertRaises(ValidationError):
            CommunityPostService.create(
                user=self.user,
                content="Great track.",
                target_data={
                    "target_type": CommunityPostTarget.TargetType.EXTERNAL,
                },
            )

        self.assertEqual(
            CommunityPost.objects.count(),
            0,
        )

        self.assertEqual(
            CommunityPostTarget.objects.count(),
            0,
        )

    def test_create_is_atomic_when_target_creation_fails(self):
        with self.assertRaises(ValidationError):
            CommunityPostService.create(
                user=self.user,
                content="This should roll back.",
                target_data={
                    "target_type": CommunityPostTarget.TargetType.EXTERNAL,
                },
            )

        self.assertFalse(
            CommunityPost.objects.filter(
                content="This should roll back."
            ).exists()
        )

    def test_update_post(self):
        post = CommunityPost.objects.create(
            user=self.user,
            content="Original content",
            rating=3.5,
        )

        CommunityPostTarget.objects.create(
            post=post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=self.song,
        )

        updated = CommunityPostService.update(
            post=post,
            content="Updated content",
            rating=4.5,
        )

        post.refresh_from_db()

        self.assertEqual(updated.pk, post.pk)
        self.assertEqual(post.content, "Updated content")
        self.assertEqual(post.rating, 4.5)
        self.assertTrue(post.is_edited)

    def test_update_does_not_change_target(self):
        post = CommunityPost.objects.create(
            user=self.user,
            content="Original content",
        )

        target = CommunityPostTarget.objects.create(
            post=post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=self.song,
        )

        CommunityPostService.update(
            post=post,
            content="Changed content",
            rating=4.0,
        )

        target.refresh_from_db()

        self.assertEqual(target.song, self.song)
        self.assertEqual(
            target.target_type,
            CommunityPostTarget.TargetType.SONG,
        )

    def test_update_sets_is_edited_even_when_rating_is_unchanged(self):
        post = CommunityPost.objects.create(
            user=self.user,
            content="Original content",
            rating=4.0,
        )

        CommunityPostService.update(
            post=post,
            content="New content",
            rating=4.0,
        )

        post.refresh_from_db()

        self.assertTrue(post.is_edited)

    def test_delete_post(self):
        post = CommunityPost.objects.create(
            user=self.user,
            content="Delete this post.",
        )

        CommunityPostTarget.objects.create(
            post=post,
            target_type=CommunityPostTarget.TargetType.SONG,
            song=self.song,
        )

        post_id = post.pk

        CommunityPostService.delete(post=post)

        self.assertFalse(
            CommunityPost.objects.filter(pk=post_id).exists()
        )

        self.assertFalse(
            CommunityPostTarget.objects.filter(post_id=post_id).exists()
        )

    def test_delete_is_safe_for_related_target(self):
        post = CommunityPost.objects.create(
            user=self.user,
            content="Post with target.",
        )

        CommunityPostTarget.objects.create(
            post=post,
            target_type=CommunityPostTarget.TargetType.ARTIST,
            artist=self.artist,
        )

        CommunityPostService.delete(post=post)

        self.assertEqual(
            CommunityPost.objects.count(),
            0,
        )

        self.assertEqual(
            CommunityPostTarget.objects.count(),
            0,
        )


class CommunityPostCommentServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="commentuser",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="othercommentuser",
            password="testpass123",
        )

        self.post = CommunityPost.objects.create(
            user=self.user,
            content="This is a community post.",
            status=CommunityPost.Status.PUBLISHED,
        )

        self.other_post = CommunityPost.objects.create(
            user=self.other_user,
            content="Another community post.",
            status=CommunityPost.Status.PUBLISHED,
        )

    def test_create_top_level_comment(self):
        comment = CommunityPostCommentService.create(
            user=self.user,
            post=self.post,
            content="Great post!",
        )

        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.post, self.post)
        self.assertIsNone(comment.parent)
        self.assertEqual(comment.content, "Great post!")

        self.post.refresh_from_db()

        self.assertEqual(self.post.comments_count, 1)

    def test_create_reply(self):
        parent = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Original comment",
        )

        reply = CommunityPostCommentService.create(
            user=self.other_user,
            post=self.post,
            content="I agree with you.",
            parent=parent,
        )

        self.assertEqual(reply.parent, parent)
        self.assertEqual(reply.post, self.post)

        self.post.refresh_from_db()
        parent.refresh_from_db()

        self.assertEqual(self.post.comments_count, 1)
        self.assertEqual(parent.replies_count, 1)

    def test_create_comment_increments_post_counter(self):
        CommunityPostCommentService.create(
            user=self.user,
            post=self.post,
            content="First comment",
        )

        CommunityPostCommentService.create(
            user=self.other_user,
            post=self.post,
            content="Second comment",
        )

        self.post.refresh_from_db()

        self.assertEqual(self.post.comments_count, 2)

    def test_create_reply_increments_both_counters(self):
        parent = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Parent comment",
        )

        CommunityPostCommentService.create(
            user=self.other_user,
            post=self.post,
            content="Reply",
            parent=parent,
        )

        self.post.refresh_from_db()
        parent.refresh_from_db()

        self.assertEqual(self.post.comments_count, 1)
        self.assertEqual(parent.replies_count, 1)

    def test_cannot_comment_on_hidden_post(self):
        self.post.status = CommunityPost.Status.HIDDEN
        self.post.save(update_fields=["status"])

        with self.assertRaises(ValidationError):
            CommunityPostCommentService.create(
                user=self.user,
                post=self.post,
                content="This should fail.",
            )

        self.assertEqual(
            CommunityPostComment.objects.count(),
            0,
        )

    def test_cannot_reply_to_comment_from_another_post(self):
        parent = CommunityPostComment.objects.create(
            user=self.user,
            post=self.other_post,
            content="Comment on another post",
        )

        with self.assertRaises(ValidationError):
            CommunityPostCommentService.create(
                user=self.user,
                post=self.post,
                content="Invalid reply",
                parent=parent,
            )

        self.assertEqual(
            CommunityPostComment.objects.count(),
            1,
        )

    def test_cannot_reply_to_hidden_comment(self):
        parent = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Hidden comment",
            status=CommunityPostComment.Status.HIDDEN,
        )

        with self.assertRaises(ValidationError):
            CommunityPostCommentService.create(
                user=self.other_user,
                post=self.post,
                content="Reply to hidden comment",
                parent=parent,
            )

    def test_update_comment(self):
        comment = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Original content",
        )

        updated = CommunityPostCommentService.update(
            comment=comment,
            content="Updated content",
        )

        comment.refresh_from_db()

        self.assertEqual(updated.pk, comment.pk)
        self.assertEqual(comment.content, "Updated content")
        self.assertTrue(comment.is_edited)

    def test_update_does_not_change_parent(self):
        parent = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Parent",
        )

        reply = CommunityPostComment.objects.create(
            user=self.other_user,
            post=self.post,
            parent=parent,
            content="Original reply",
        )

        CommunityPostCommentService.update(
            comment=reply,
            content="Updated reply",
        )

        reply.refresh_from_db()

        self.assertEqual(reply.parent_id, parent.pk)

    def test_delete_top_level_comment_decrements_post_counter(self):
        comment = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Delete me",
        )

        self.post.comments_count = 1
        self.post.save(update_fields=["comments_count"])

        CommunityPostCommentService.delete(
            comment=comment,
        )

        self.post.refresh_from_db()

        self.assertEqual(self.post.comments_count, 0)

        self.assertFalse(
            CommunityPostComment.objects.filter(
                pk=comment.pk
            ).exists()
        )

    def test_delete_reply_decrements_post_and_parent_counters(self):
        parent = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Parent",
            replies_count=1,
        )

        reply = CommunityPostComment.objects.create(
            user=self.other_user,
            post=self.post,
            parent=parent,
            content="Reply",
        )

        self.post.comments_count = 1
        self.post.save(update_fields=["comments_count"])

        CommunityPostCommentService.delete(
            comment=reply,
        )

        self.post.refresh_from_db()
        parent.refresh_from_db()

        self.assertEqual(self.post.comments_count, 0)
        self.assertEqual(parent.replies_count, 0)

    def test_delete_is_safe_when_comment_already_deleted(self):
        comment = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Delete twice",
        )

        CommunityPostCommentService.delete(
            comment=comment,
        )

        # Calling delete again should not crash.
        CommunityPostCommentService.delete(
            comment=comment,
        )

        self.assertFalse(
            CommunityPostComment.objects.filter(
                pk=comment.pk
            ).exists()
        )

class CommunityReportServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="reportuser",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="otherreportuser",
            password="testpass123",
        )

        self.article = EditorialArticle.objects.create(
            title="Reportable Article",
            slug="reportable-article",
            excerpt="Article excerpt",
            content="Article content",
            author=self.user,
            status=EditorialArticle.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        self.post = CommunityPost.objects.create(
            user=self.user,
            content="Reportable post.",
            status=CommunityPost.Status.PUBLISHED,
        )

        self.editorial_comment = EditorialComment.objects.create(
            user=self.user,
            article=self.article,
            content="Reportable editorial comment.",
            status=EditorialComment.Status.PUBLISHED,
        )

        self.community_comment = CommunityPostComment.objects.create(
            user=self.user,
            post=self.post,
            content="Reportable community comment.",
            status=CommunityPostComment.Status.PUBLISHED,
        )

    def test_report_published_article(self):
        report = EditorialArticleReportService.create(
            user=self.other_user,
            article=self.article,
            reason=EditorialArticleReport.Reason.SPAM,
            details="This looks like spam.",
        )

        self.assertEqual(report.user, self.other_user)
        self.assertEqual(report.article, self.article)
        self.assertEqual(
            report.reason,
            EditorialArticleReport.Reason.SPAM,
        )
        self.assertEqual(
            report.details,
            "This looks like spam.",
        )

    def test_cannot_report_same_article_twice(self):
        EditorialArticleReportService.create(
            user=self.other_user,
            article=self.article,
            reason=EditorialArticleReport.Reason.SPAM,
        )

        with self.assertRaises(ValidationError):
            EditorialArticleReportService.create(
                user=self.other_user,
                article=self.article,
                reason=EditorialArticleReport.Reason.SPAM,
            )

        self.assertEqual(
            EditorialArticleReport.objects.count(),
            1,
        )

    def test_cannot_report_unpublished_article(self):
        self.article.status = EditorialArticle.Status.DRAFT
        self.article.save(update_fields=["status"])

        with self.assertRaises(ValidationError):
            EditorialArticleReportService.create(
                user=self.other_user,
                article=self.article,
                reason=EditorialArticleReport.Reason.SPAM,
            )

        self.assertEqual(
            EditorialArticleReport.objects.count(),
            0,
        )

    def test_different_users_can_report_same_article(self):
        EditorialArticleReportService.create(
            user=self.user,
            article=self.article,
            reason=EditorialArticleReport.Reason.SPAM,
        )

        EditorialArticleReportService.create(
            user=self.other_user,
            article=self.article,
            reason=EditorialArticleReport.Reason.COPYRIGHT,
        )

        self.assertEqual(
            EditorialArticleReport.objects.count(),
            2,
        )

    def test_report_published_post(self):
        report = CommunityPostReportService.create(
            user=self.other_user,
            post=self.post,
            reason=CommunityPostReport.Reason.SPAM,
            details="Spam post.",
        )

        self.assertEqual(report.user, self.other_user)
        self.assertEqual(report.post, self.post)

    def test_cannot_report_same_post_twice(self):
        CommunityPostReportService.create(
            user=self.other_user,
            post=self.post,
            reason=CommunityPostReport.Reason.SPAM,
        )

        with self.assertRaises(ValidationError):
            CommunityPostReportService.create(
                user=self.other_user,
                post=self.post,
                reason=CommunityPostReport.Reason.SPAM,
            )

        self.assertEqual(
            CommunityPostReport.objects.count(),
            1,
        )

    def test_cannot_report_hidden_post(self):
        self.post.status = CommunityPost.Status.HIDDEN
        self.post.save(update_fields=["status"])

        with self.assertRaises(ValidationError):
            CommunityPostReportService.create(
                user=self.other_user,
                post=self.post,
                reason=CommunityPostReport.Reason.SPAM,
            )

        self.assertEqual(
            CommunityPostReport.objects.count(),
            0,
        )

    def test_different_users_can_report_same_post(self):
        CommunityPostReportService.create(
            user=self.user,
            post=self.post,
            reason=CommunityPostReport.Reason.SPAM,
        )

        CommunityPostReportService.create(
            user=self.other_user,
            post=self.post,
            reason=CommunityPostReport.Reason.HARASSMENT,
        )

        self.assertEqual(
            CommunityPostReport.objects.count(),
            2,
        )

    def test_report_published_editorial_comment(self):
        report = EditorialCommentReportService.create(
            user=self.other_user,
            comment=self.editorial_comment,
            reason=EditorialCommentReport.Reason.SPAM,
            details="Spam comment.",
        )

        self.assertEqual(report.user, self.other_user)
        self.assertEqual(report.comment, self.editorial_comment)

    def test_cannot_report_same_editorial_comment_twice(self):
        EditorialCommentReportService.create(
            user=self.other_user,
            comment=self.editorial_comment,
            reason=EditorialCommentReport.Reason.SPAM,
        )

        with self.assertRaises(ValidationError):
            EditorialCommentReportService.create(
                user=self.other_user,
                comment=self.editorial_comment,
                reason=EditorialCommentReport.Reason.SPAM,
            )

        self.assertEqual(
            EditorialCommentReport.objects.count(),
            1,
        )

    def test_cannot_report_hidden_editorial_comment(self):
        self.editorial_comment.status = EditorialComment.Status.HIDDEN
        self.editorial_comment.save(update_fields=["status"])

        with self.assertRaises(ValidationError):
            EditorialCommentReportService.create(
                user=self.other_user,
                comment=self.editorial_comment,
                reason=EditorialCommentReport.Reason.SPAM,
            )

        self.assertEqual(
            EditorialCommentReport.objects.count(),
            0,
        )

    def test_cannot_report_comment_on_unpublished_article(self):
        self.article.status = EditorialArticle.Status.DRAFT
        self.article.save(update_fields=["status"])

        with self.assertRaises(ValidationError):
            EditorialCommentReportService.create(
                user=self.other_user,
                comment=self.editorial_comment,
                reason=EditorialCommentReport.Reason.SPAM,
            )

        self.assertEqual(
            EditorialCommentReport.objects.count(),
            0,
        )

    def test_report_published_community_comment(self):
        report = CommunityPostCommentReportService.create(
            user=self.other_user,
            comment=self.community_comment,
            reason=CommunityPostCommentReport.Reason.SPAM,
            details="Spam comment.",
        )

        self.assertEqual(report.user, self.other_user)
        self.assertEqual(report.comment, self.community_comment)

    def test_cannot_report_same_community_comment_twice(self):
        CommunityPostCommentReportService.create(
            user=self.other_user,
            comment=self.community_comment,
            reason=CommunityPostCommentReport.Reason.SPAM,
        )

        with self.assertRaises(ValidationError):
            CommunityPostCommentReportService.create(
                user=self.other_user,
                comment=self.community_comment,
                reason=CommunityPostCommentReport.Reason.SPAM,
            )

        self.assertEqual(
            CommunityPostCommentReport.objects.count(),
            1,
        )

    def test_cannot_report_hidden_community_comment(self):
        self.community_comment.status = (
            CommunityPostComment.Status.HIDDEN
        )
        self.community_comment.save(update_fields=["status"])

        with self.assertRaises(ValidationError):
            CommunityPostCommentReportService.create(
                user=self.other_user,
                comment=self.community_comment,
                reason=CommunityPostCommentReport.Reason.SPAM,
            )

        self.assertEqual(
            CommunityPostCommentReport.objects.count(),
            0,
        )

    def test_cannot_report_comment_on_hidden_post(self):
        self.post.status = CommunityPost.Status.HIDDEN
        self.post.save(update_fields=["status"])

        with self.assertRaises(ValidationError):
            CommunityPostCommentReportService.create(
                user=self.other_user,
                comment=self.community_comment,
                reason=CommunityPostCommentReport.Reason.SPAM,
            )

        self.assertEqual(
            CommunityPostCommentReport.objects.count(),
            0,
        )

    def test_report_does_not_change_post_counters(self):
        original_likes = self.post.likes_count
        original_comments = self.post.comments_count

        CommunityPostReportService.create(
            user=self.other_user,
            post=self.post,
            reason=CommunityPostReport.Reason.SPAM,
        )

        self.post.refresh_from_db()

        self.assertEqual(self.post.likes_count, original_likes)
        self.assertEqual(
            self.post.comments_count,
            original_comments,
        )