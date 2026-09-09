from django.db import IntegrityError, models, transaction
from django.contrib.auth import get_user_model

from rest_framework.exceptions import ValidationError

from music.models import (
    Artist,
    ArtistFollow,
    UserFollow,
)


User = get_user_model()


# ============================================================
# ARTIST FOLLOWS
# ============================================================

class ArtistFollowService:
    """
    Business logic for users following artists.
    """

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user,
        artist: Artist,
    ) -> ArtistFollow:
        """
        Follow an artist.

        The artist must be active.
        A user can only follow an artist once.
        """

        if not artist.is_active:
            raise ValidationError(
                "You can only follow active artists."
            )

        if ArtistFollow.objects.filter(
            user=user,
            artist=artist,
        ).exists():
            raise ValidationError(
                "You are already following this artist."
            )

        try:
            follow = ArtistFollow.objects.create(
                user=user,
                artist=artist,
            )
        except IntegrityError:
            raise ValidationError(
                "You are already following this artist."
            )

        Artist.objects.filter(
            pk=artist.pk,
        ).update(
            followers_count=models.F("followers_count") + 1,
        )

        return follow

    @staticmethod
    @transaction.atomic
    def delete(
        *,
        follow_instance: ArtistFollow,
    ) -> None:
        """
        Unfollow an artist and decrement followers_count.
        """

        artist_id = follow_instance.artist_id

        deleted, _ = ArtistFollow.objects.filter(
            pk=follow_instance.pk,
        ).delete()

        if not deleted:
            return

        Artist.objects.filter(
            pk=artist_id,
            followers_count__gt=0,
        ).update(
            followers_count=models.F("followers_count") - 1,
        )


# ============================================================
# USER FOLLOWS
# ============================================================

class UserFollowService:
    """
    Business logic for users following other users.
    """

    @staticmethod
    @transaction.atomic
    def create(
        *,
        follower,
        following,
    ) -> UserFollow:
        """
        Follow another user.

        A user cannot follow themselves.
        A user can only follow another user once.
        """

        if follower.pk == following.pk:
            raise ValidationError(
                "You cannot follow yourself."
            )

        if UserFollow.objects.filter(
            follower=follower,
            following=following,
        ).exists():
            raise ValidationError(
                "You are already following this user."
            )

        try:
            follow = UserFollow.objects.create(
                follower=follower,
                following=following,
            )
        except IntegrityError:
            raise ValidationError(
                "You are already following this user."
            )

        return follow

    @staticmethod
    @transaction.atomic
    def delete(
        *,
        follow_instance: UserFollow,
    ) -> None:
        """
        Remove a user follow relationship.
        """

        UserFollow.objects.filter(
            pk=follow_instance.pk,
        ).delete()