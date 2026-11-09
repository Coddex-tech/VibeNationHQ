from __future__ import annotations

from uuid import UUID

from rest_framework import serializers

from music.models import (
    Album,
    Artist,
    CommunityPost,
    EditorialArticle,
    Song,
)


class MusicFeedInteractionSerializer(serializers.Serializer):
    """
    Validates passive behavioral events submitted by clients.

    Clients may report views and preview plays.

    Engagement events such as likes, comments, favorites,
    ratings, and follows must be recorded server-side after
    their corresponding persistent action succeeds.
    """

    ALLOWED_INTERACTIONS = {
        "view_song": "song",
        "play_preview": "song",
        "view_album": "album",
        "view_artist": "artist",
        "view_community_post": "community_post",
        "view_editorial": "editorial",
    }

    TARGET_MODEL_BY_TYPE = {
        "song": Song,
        "album": Album,
        "artist": Artist,
        "community_post": CommunityPost,
        "editorial": EditorialArticle,
    }

    interaction_type = serializers.ChoiceField(
        choices=tuple(ALLOWED_INTERACTIONS.keys()),
    )

    target_type = serializers.ChoiceField(
        choices=tuple(TARGET_MODEL_BY_TYPE.keys()),
    )

    target_id = serializers.IntegerField(
        min_value=1,
    )

    idempotency_key = serializers.UUIDField(
        required=False,
        allow_null=True,
    )

    def validate_interaction_type(
        self,
        value: str,
    ) -> str:
        return value.strip().lower()

    def validate_target_type(
        self,
        value: str,
    ) -> str:
        return value.strip().lower()

    def validate(self, attrs):
        interaction_type = attrs["interaction_type"]
        target_type = attrs["target_type"]

        expected_target_type = (
            self.ALLOWED_INTERACTIONS.get(
                interaction_type,
            )
        )

        if expected_target_type is None:
            raise serializers.ValidationError(
                {
                    "interaction_type": (
                        "Unsupported passive interaction type."
                    )
                }
            )

        if target_type != expected_target_type:
            raise serializers.ValidationError(
                {
                    "target_type": (
                        f"Interaction '{interaction_type}' "
                        f"requires target type "
                        f"'{expected_target_type}'."
                    )
                }
            )

        return attrs

    def get_target_model(self):
        """
        Return the model associated with the validated
        target type.

        Call is_valid() before using this method.
        """
        if not hasattr(self, "_validated_data"):
            raise RuntimeError(
                "Call is_valid() before resolving "
                "the interaction target model."
            )

        target_type = self.validated_data["target_type"]

        return self.TARGET_MODEL_BY_TYPE[target_type]

    def get_target_id(self) -> int:
        """
        Return the validated target ID.

        Call is_valid() before using this method.
        """
        if not hasattr(self, "_validated_data"):
            raise RuntimeError(
                "Call is_valid() before resolving "
                "the interaction target ID."
            )

        return self.validated_data["target_id"]

    def get_idempotency_key(self) -> UUID | None:
        """
        Return the optional validated idempotency key.

        Call is_valid() before using this method.
        """
        if not hasattr(self, "_validated_data"):
            raise RuntimeError(
                "Call is_valid() before resolving "
                "the idempotency key."
            )

        return self.validated_data.get("idempotency_key")
