from django.contrib.auth import get_user_model

from rest_framework import serializers

from music.serializers.catalog import ArtistCardSerializer


User = get_user_model()


# ============================================================
# PUBLIC USER CONNECTION
# ============================================================

class PublicConnectionUserSerializer(
    serializers.ModelSerializer
):
    """
    Read-only representation of a user in another user's
    public connections list.

    The is_following field represents whether the authenticated
    viewer follows this user.

    The view should annotate the queryset with is_following
    using Exists() to avoid additional queries per user.
    """

    profile_image = serializers.SerializerMethodField()

    is_following = serializers.BooleanField(
        read_only=True,
        default=False,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "display_name",
            "profile_image",
            "is_verified",
            "is_identity_verified",
            "is_following",
        ]
        read_only_fields = fields

    def get_profile_image(self, obj):
        """
        Return an absolute profile image URL when a request
        is available in the serializer context.
        """

        if not obj.profile_image:
            return None

        image_url = obj.profile_image.url

        request = self.context.get("request")

        if request is not None:
            return request.build_absolute_uri(image_url)

        return image_url


# ============================================================
# PUBLIC ARTIST CONNECTION
# ============================================================

class PublicConnectionArtistSerializer(
    ArtistCardSerializer
):
    """
    Read-only artist representation in a user's public
    followed-artists list.

    Extends ArtistCardSerializer without changing its
    existing API representation elsewhere.

    The is_following field represents whether the authenticated
    viewer follows this artist.

    The view should annotate the queryset with is_following
    using Exists() to avoid additional queries per artist.
    """

    is_following = serializers.BooleanField(
        read_only=True,
        default=False,
    )

    class Meta(ArtistCardSerializer.Meta):
        fields = [
            *ArtistCardSerializer.Meta.fields,
            "is_following",
        ]
        read_only_fields = fields