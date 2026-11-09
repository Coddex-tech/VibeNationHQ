from django.db import IntegrityError, models, transaction

from rest_framework.exceptions import ValidationError

from music.models import (
    Song,
    Album,
    SongFavorite,
    AlbumFavorite,
    EditorialArticle,
    EditorialArticleFavorite,
)


# ============================================================
# SONG FAVORITES
# ============================================================

class SongFavoriteService:
    """
    Business logic for users favoriting songs.
    """

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user,
        song: Song,
    ) -> SongFavorite:
        """
        Favorite a song.

        A user can only favorite a song once.
        The song must be published.
        """

        if song.status != Song.Status.PUBLISHED:
            raise ValidationError(
                "You can only favorite published songs."
            )

        if SongFavorite.objects.filter(
            user=user,
            song=song,
        ).exists():
            raise ValidationError(
                "You have already favorited this song."
            )

        try:
            favorite = SongFavorite.objects.create(
                user=user,
                song=song,
            )
        except IntegrityError:
            raise ValidationError(
                "You have already favorited this song."
            )

        Song.objects.filter(
            pk=song.pk,
        ).update(
            favorites_count=models.F("favorites_count") + 1,
        )

        return favorite

    @staticmethod
    @transaction.atomic
    def delete(
        *,
        favorite_instance: SongFavorite,
    ) -> None:
        """
        Remove a song favorite and decrement favorites_count.
        """

        song_id = favorite_instance.song_id

        deleted, _ = SongFavorite.objects.filter(
            pk=favorite_instance.pk,
        ).delete()

        if not deleted:
            return

        Song.objects.filter(
            pk=song_id,
            favorites_count__gt=0,
        ).update(
            favorites_count=models.F("favorites_count") - 1,
        )


# ============================================================
# ALBUM FAVORITES
# ============================================================

class AlbumFavoriteService:
    """
    Business logic for users favoriting albums.
    """

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user,
        album: Album,
    ) -> AlbumFavorite:
        """
        Favorite an album.

        A user can only favorite an album once.
        The album must be published.
        """

        if album.status != Album.Status.PUBLISHED:
            raise ValidationError(
                "You can only favorite published albums."
            )

        if AlbumFavorite.objects.filter(
            user=user,
            album=album,
        ).exists():
            raise ValidationError(
                "You have already favorited this album."
            )

        try:
            favorite = AlbumFavorite.objects.create(
                user=user,
                album=album,
            )
        except IntegrityError:
            raise ValidationError(
                "You have already favorited this album."
            )

        Album.objects.filter(
            pk=album.pk,
        ).update(
            favorites_count=models.F("favorites_count") + 1,
        )

        return favorite

    @staticmethod
    @transaction.atomic
    def delete(
        *,
        favorite_instance: AlbumFavorite,
    ) -> None:
        """
        Remove an album favorite and decrement favorites_count.
        """

        album_id = favorite_instance.album_id

        deleted, _ = AlbumFavorite.objects.filter(
            pk=favorite_instance.pk,
        ).delete()

        if not deleted:
            return

        Album.objects.filter(
            pk=album_id,
            favorites_count__gt=0,
        ).update(
            favorites_count=models.F("favorites_count") - 1,
        )


# ============================================================
# EDITORIAL ARTICLE FAVORITES
# ============================================================

class EditorialArticleFavoriteService:
    """
    Business logic for users favoriting editorial articles.
    """

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user,
        article: EditorialArticle,
    ) -> EditorialArticleFavorite:
        """
        Favorite a published editorial article.

        A user can only favorite an article once.
        """

        if article.status != EditorialArticle.Status.PUBLISHED:
            raise ValidationError(
                "You can only favorite published articles."
            )

        if EditorialArticleFavorite.objects.filter(
            user=user,
            article=article,
        ).exists():
            raise ValidationError(
                "You have already favorited this article."
            )

        try:
            favorite = EditorialArticleFavorite.objects.create(
                user=user,
                article=article,
            )
        except IntegrityError:
            raise ValidationError(
                "You have already favorited this article."
            )

        EditorialArticle.objects.filter(
            pk=article.pk,
        ).update(
            favorites_count=models.F("favorites_count") + 1,
        )

        return favorite

    @staticmethod
    @transaction.atomic
    def delete(
        *,
        favorite_instance: EditorialArticleFavorite,
    ) -> None:
        """
        Remove an article favorite and safely decrement its counter.
        """

        article_id = favorite_instance.article_id

        deleted, _ = EditorialArticleFavorite.objects.filter(
            pk=favorite_instance.pk,
        ).delete()

        if not deleted:
            return

        EditorialArticle.objects.filter(
            pk=article_id,
            favorites_count__gt=0,
        ).update(
            favorites_count=models.F("favorites_count") - 1,
        )
