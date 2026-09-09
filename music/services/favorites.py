from django.db import IntegrityError, models, transaction

from rest_framework.exceptions import ValidationError

from music.models import (
    Song,
    Album,
    SongFavorite,
    AlbumFavorite,
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