from django.db import IntegrityError, transaction, models

from rest_framework.exceptions import ValidationError

from music.models import (
    SongRating,
    AlbumRating,
    Song,
    Album,
)


# ============================================================
# SONG RATINGS
# ============================================================

class SongRatingService:
    """
    Business logic for user ratings on songs.
    """

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user,
        song: Song,
        rating,
    ) -> SongRating:
        """
        Create a user's rating for a song.

        A user can only have one rating per song.
        The song must be published.
        """

        if song.status != Song.Status.PUBLISHED:
            raise ValidationError(
                "You can only rate published songs."
            )

        if SongRating.objects.filter(
            user=user,
            song=song,
        ).exists():
            raise ValidationError(
                "You have already rated this song."
            )

        try:
            song_rating = SongRating.objects.create(
                user=user,
                song=song,
                rating=rating,
            )
        except IntegrityError:
            raise ValidationError(
                "You have already rated this song."
            )

        Song.objects.filter(
            pk=song.pk,
        ).update(
            ratings_count=models.F("ratings_count") + 1,
        )

        return song_rating

    @staticmethod
    @transaction.atomic
    def update(
        *,
        rating_instance: SongRating,
        rating,
    ) -> SongRating:
        """
        Update an existing song rating.

        Updating a rating does not change ratings_count.
        """

        if rating_instance.song.status != Song.Status.PUBLISHED:
            raise ValidationError(
                "You can only rate published songs."
            )

        rating_instance.rating = rating
        rating_instance.save(
            update_fields=[
                "rating",
                "updated_at",
            ]
        )

        return rating_instance

    @staticmethod
    @transaction.atomic
    def delete(
        *,
        rating_instance: SongRating,
    ) -> None:
        """
        Delete a user's song rating and decrement ratings_count.
        """

        song_id = rating_instance.song_id

        deleted, _ = SongRating.objects.filter(
            pk=rating_instance.pk,
        ).delete()

        if not deleted:
            return

        Song.objects.filter(
            pk=song_id,
            ratings_count__gt=0,
        ).update(
            ratings_count=models.F("ratings_count") - 1,
        )


# ============================================================
# ALBUM RATINGS
# ============================================================

class AlbumRatingService:
    """
    Business logic for user ratings on albums.
    """

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user,
        album: Album,
        rating,
    ) -> AlbumRating:
        """
        Create a user's rating for an album.

        A user can only have one rating per album.
        The album must be published.
        """

        if album.status != Album.Status.PUBLISHED:
            raise ValidationError(
                "You can only rate published albums."
            )

        if AlbumRating.objects.filter(
            user=user,
            album=album,
        ).exists():
            raise ValidationError(
                "You have already rated this album."
            )

        try:
            album_rating = AlbumRating.objects.create(
                user=user,
                album=album,
                rating=rating,
            )
        except IntegrityError:
            raise ValidationError(
                "You have already rated this album."
            )

        Album.objects.filter(
            pk=album.pk,
        ).update(
            ratings_count=models.F("ratings_count") + 1,
        )

        return album_rating

    @staticmethod
    @transaction.atomic
    def update(
        *,
        rating_instance: AlbumRating,
        rating,
    ) -> AlbumRating:
        """
        Update an existing album rating.

        Updating a rating does not change ratings_count.
        """

        if rating_instance.album.status != Album.Status.PUBLISHED:
            raise ValidationError(
                "You can only rate published albums."
            )

        rating_instance.rating = rating
        rating_instance.save(
            update_fields=[
                "rating",
                "updated_at",
            ]
        )

        return rating_instance

    @staticmethod
    @transaction.atomic
    def delete(
        *,
        rating_instance: AlbumRating,
    ) -> None:
        """
        Delete a user's album rating and decrement ratings_count.
        """

        album_id = rating_instance.album_id

        deleted, _ = AlbumRating.objects.filter(
            pk=rating_instance.pk,
        ).delete()

        if not deleted:
            return

        Album.objects.filter(
            pk=album_id,
            ratings_count__gt=0,
        ).update(
            ratings_count=models.F("ratings_count") - 1,
        )