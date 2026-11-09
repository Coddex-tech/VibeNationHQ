from rest_framework import serializers

from music.serializers.catalog import (
    AlbumCardSerializer,
    ArtistCardSerializer,
    SongCardSerializer,
)


class PublicProfileMusicItemSerializer(
    serializers.Serializer
):
    """
    Read-only representation of one unique canonical music
    entity in a user's public profile Music timeline.

    The view supplies:
        - target_type
        - post_count
        - latest_post_at
        - entity

    The entity is serialized using its existing catalog card
    serializer, keeping catalog representations consistent
    across VibeNation.
    """

    target_type = serializers.ChoiceField(
        choices=[
            "song",
            "album",
            "artist",
        ],
        read_only=True,
    )

    post_count = serializers.IntegerField(
        read_only=True,
        min_value=1,
    )

    latest_post_at = serializers.DateTimeField(
        read_only=True,
    )

    entity = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "target_type",
            "post_count",
            "latest_post_at",
            "entity",
        ]

    def get_entity(self, obj):
        """
        Serialize the hydrated catalog entity according
        to its canonical target type.
        """

        target_type = obj["target_type"]
        entity = obj["entity"]

        serializer_classes = {
            "song": SongCardSerializer,
            "album": AlbumCardSerializer,
            "artist": ArtistCardSerializer,
        }

        serializer_class = serializer_classes.get(
            target_type,
        )

        if serializer_class is None:
            return None

        return serializer_class(
            entity,
            context=self.context,
        ).data