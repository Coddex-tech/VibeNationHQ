from rest_framework import serializers

from django.db import transaction

from music.models import (
    CommunityPost,
    CommunityPostTarget,
    CommunityPostComment,
    CommunityPostReport,
    CommunityPostCommentReport, 
    Song,
    Album,
    Artist,
)

from .base import (
    BaseModelSerializer,
    validate_half_star_rating
)

from .catalog import (
    ArtistCardSerializer,
    AlbumCardSerializer,
    SongCardSerializer,
)


# ============================================================
# COMMUNITY POST TARGET — READ
# ============================================================

class CommunityPostTargetSerializer(BaseModelSerializer):
    """
    Read-only representation of the content attached to
    a community post.

    A target can reference exactly one of:

    - VibeNation Song
    - VibeNation Album
    - VibeNation Artist
    - External music catalog item
    """

    song = SongCardSerializer(
        read_only=True,
    )

    album = AlbumCardSerializer(
        read_only=True,
    )

    artist = ArtistCardSerializer(
        read_only=True,
    )

    class Meta:
        model = CommunityPostTarget
        fields = [
            "id",
            "target_type",

            # Internal targets
            "song",
            "album",
            "artist",

            # External target identity
            "external_provider",
            "external_content_type",
            "external_id",

            # External metadata snapshot
            "title",
            "artist_name",
            "album_name",
            "artwork_url",
            "preview_url",
            "spotify_url",
            "apple_music_url",
        ]

        read_only_fields = fields


# ============================================================
# COMMUNITY POST TARGET — CREATE INPUT
# ============================================================

class CommunityPostTargetCreateSerializer(serializers.Serializer):
    """
    Validates the target a user wants to attach to a
    community post.

    The client can attach exactly one of:

    - an internal VibeNation Song
    - an internal VibeNation Album
    - an internal VibeNation Artist
    - an external music catalog item

    Server-controlled snapshot fields such as title,
    artwork, artist name, metadata, etc. are intentionally
    NOT accepted from the client.
    """

    target_type = serializers.ChoiceField(
        choices=CommunityPostTarget.TargetType.choices,
    )

    # --------------------------------------------------------
    # Internal targets
    # --------------------------------------------------------

    song = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.filter(
            status=Song.Status.PUBLISHED,
        ),
        required=False,
    )

    album = serializers.PrimaryKeyRelatedField(
        queryset=Album.objects.filter(
            status=Album.Status.PUBLISHED,
        ),
        required=False,
    )

    artist = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.filter(
            is_active=True,
        ),
        required=False,
    )

    # --------------------------------------------------------
    # External target
    # --------------------------------------------------------

    external_provider = serializers.ChoiceField(
        choices=CommunityPostTarget.ExternalProvider.choices,
        required=False,
    )

    external_content_type = serializers.ChoiceField(
        choices=CommunityPostTarget.ExternalContentType.choices,
        required=False,
    )

    external_id = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=False,
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    def validate(self, attrs):
        target_type = attrs["target_type"]

        song = attrs.get("song")
        album = attrs.get("album")
        artist = attrs.get("artist")

        external_provider = attrs.get("external_provider")
        external_content_type = attrs.get("external_content_type")
        external_id = attrs.get("external_id")

        # ====================================================
        # SONG
        # ====================================================

        if target_type == CommunityPostTarget.TargetType.SONG:

            if not song:
                raise serializers.ValidationError({
                    "song": "A song is required when target_type is 'song'."
                })

            if album or artist:
                raise serializers.ValidationError(
                    "A song target cannot include an album or artist."
                )

            if (
                external_provider
                or external_content_type
                or external_id
            ):
                raise serializers.ValidationError(
                    "A song target cannot include external target fields."
                )

        # ====================================================
        # ALBUM
        # ====================================================

        elif target_type == CommunityPostTarget.TargetType.ALBUM:

            if not album:
                raise serializers.ValidationError({
                    "album": "An album is required when target_type is 'album'."
                })

            if song or artist:
                raise serializers.ValidationError(
                    "An album target cannot include a song or artist."
                )

            if (
                external_provider
                or external_content_type
                or external_id
            ):
                raise serializers.ValidationError(
                    "An album target cannot include external target fields."
                )

        # ====================================================
        # ARTIST
        # ====================================================

        elif target_type == CommunityPostTarget.TargetType.ARTIST:

            if not artist:
                raise serializers.ValidationError({
                    "artist": "An artist is required when target_type is 'artist'."
                })

            if song or album:
                raise serializers.ValidationError(
                    "An artist target cannot include a song or album."
                )

            if (
                external_provider
                or external_content_type
                or external_id
            ):
                raise serializers.ValidationError(
                    "An artist target cannot include external target fields."
                )

        # ====================================================
        # EXTERNAL
        # ====================================================

        elif target_type == CommunityPostTarget.TargetType.EXTERNAL:

            if not external_provider:
                raise serializers.ValidationError({
                    "external_provider": (
                        "This field is required for an external target."
                    )
                })

            if not external_content_type:
                raise serializers.ValidationError({
                    "external_content_type": (
                        "This field is required for an external target."
                    )
                })

            if not external_id:
                raise serializers.ValidationError({
                    "external_id": (
                        "This field is required for an external target."
                    )
                })

            if song or album or artist:
                raise serializers.ValidationError(
                    "An external target cannot include an internal target."
                )

        return attrs


# ============================================================
# COMMUNITY POST
# ============================================================

class CommunityPostSerializer(BaseModelSerializer):
    """
    Read-only representation of a community post.

    Includes:

    - author
    - post content
    - optional rating
    - attached music/content target
    - engagement counters
    - moderation state
    - timestamps
    """

    target = CommunityPostTargetSerializer(
        read_only=True,
    )

    class Meta:
        model = CommunityPost

        fields = [
            "id",

            # Author
            "user",

            # Content
            "content",
            "rating",

            # Target
            "target",

            # Engagement
            "views_count",
            "likes_count",
            "comments_count",

            # Moderation / state
            "status",
            "is_edited",

            # Timestamps
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields


# ============================================================
# COMMUNITY POST — CREATE INPUT
# ============================================================
class CommunityPostCreateSerializer(serializers.ModelSerializer):
    """
    Serializer used when a user creates a community post.

    Client-controlled fields:
    - content
    - rating
    - target

    The optional rating represents the user's personal rating
    expressed through this community post.

    It does NOT replace or modify the structured SongRating
    or AlbumRating system.

    Server-controlled fields:
    - user
    - views_count
    - likes_count
    - comments_count
    - status
    - is_edited
    - created_at
    - updated_at
    """

    rating = serializers.DecimalField(
        max_digits=2,
        decimal_places=1,
        required=False,
        allow_null=True,
        validators=[
            validate_half_star_rating,
        ],
    )

    target = CommunityPostTargetCreateSerializer(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = CommunityPost

        fields = [
            "content",
            "rating",
            "target",
        ]

    @transaction.atomic
    def create(self, validated_data):
        """
        Create the community post and its target atomically.

        If target creation fails, the post creation is rolled back too.
        """

        target_data = validated_data.pop("target", None)

        user = self.context["request"].user

        post = CommunityPost.objects.create(
            user=user,
            **validated_data,
        )

        if target_data:
            self._create_target(
                post=post,
                target_data=target_data,
            )

        return post

    def _create_target(self, post, target_data):
        """
        Create the CommunityPostTarget associated with the post.

        Internal targets can be created immediately.

        External targets will later be resolved through a dedicated
        external music metadata service.
        """

        target_type = target_data["target_type"]

        # ====================================================
        # INTERNAL SONG
        # ====================================================

        if target_type == CommunityPostTarget.TargetType.SONG:
            CommunityPostTarget.objects.create(
                post=post,
                target_type=target_type,
                song=target_data["song"],
            )
            return

        # ====================================================
        # INTERNAL ALBUM
        # ====================================================

        if target_type == CommunityPostTarget.TargetType.ALBUM:
            CommunityPostTarget.objects.create(
                post=post,
                target_type=target_type,
                album=target_data["album"],
            )
            return

        # ====================================================
        # INTERNAL ARTIST
        # ====================================================

        if target_type == CommunityPostTarget.TargetType.ARTIST:
            CommunityPostTarget.objects.create(
                post=post,
                target_type=target_type,
                artist=target_data["artist"],
            )
            return

        # ====================================================
        # EXTERNAL
        # ====================================================

        if target_type == CommunityPostTarget.TargetType.EXTERNAL:
            raise serializers.ValidationError({
                "target": (
                    "External targets are not available yet. "
                    "They must be resolved by the external music "
                    "catalog service before the target can be created."
                )
            })


# ============================================================
# COMMUNITY POST — UPDATE INPUT
# ============================================================

class CommunityPostUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer used when a user edits their community post.

    Users can update:
    - content
    - rating

    The attached target cannot be changed after creation.

    Server-controlled fields such as the author, engagement
    counters, status, edit state, and timestamps cannot be
    modified by the client.
    """

    rating = serializers.DecimalField(
        max_digits=2,
        decimal_places=1,
        required=False,
        allow_null=True,
        validators=[
            validate_half_star_rating,
        ],
    )

    class Meta:
        model = CommunityPost

        fields = [
            "content",
            "rating",
        ]

    def update(self, instance, validated_data):
        """
        Update the editable fields and mark the post as edited.
        """

        instance.content = validated_data.get(
            "content",
            instance.content,
        )

        if "rating" in validated_data:
            instance.rating = validated_data["rating"]

        instance.is_edited = True

        instance.save(
            update_fields=[
                "content",
                "rating",
                "is_edited",
                "updated_at",
            ]
        )

        return instance


# ============================================================
# ============================================================
# COMMUNITY POST COMMENT — CREATE INPUT
# ============================================================
# ============================================================
class CommunityPostCommentSerializer(BaseModelSerializer):
    """
    Read-only representation of a community post comment.
    """

    class Meta:
        model = CommunityPostComment

        fields = [
            "id",
            "user",
            "post",
            "parent",
            "content",

            "views_count",
            "likes_count",
            "replies_count",

            "status",
            "is_edited",

            "created_at",
            "updated_at",
        ]

        read_only_fields = fields
        

class CommunityPostCommentCreateSerializer(
    serializers.ModelSerializer
):
    """
    Serializer used when a user creates a comment or reply.

    Client-controlled fields:
    - content
    - post
    - parent

    Server-controlled fields:
    - user
    - views_count
    - likes_count
    - replies_count
    - status
    - is_edited
    - timestamps
    """

    class Meta:
        model = CommunityPostComment

        fields = [
            "post",
            "parent",
            "content",
        ]

    def validate_post(self, value):
        """
        Only allow comments on published community posts.
        """

        if value.status != CommunityPost.Status.PUBLISHED:
            raise serializers.ValidationError(
                "Comments can only be added to published posts."
            )

        return value

    def validate(self, attrs):
        """
        Validate the parent comment when creating a reply.
        """

        post = attrs["post"]
        parent = attrs.get("parent")

        if parent is None:
            return attrs

        # ----------------------------------------------------
        # Parent must belong to the same post
        # ----------------------------------------------------

        if parent.post_id != post.id:
            raise serializers.ValidationError({
                "parent": (
                    "The parent comment must belong to the same post."
                )
            })

        # ----------------------------------------------------
        # Parent must be published
        # ----------------------------------------------------

        if parent.status != CommunityPostComment.Status.PUBLISHED:
            raise serializers.ValidationError({
                "parent": (
                    "You cannot reply to a hidden or removed comment."
                )
            })

        return attrs

    def create(self, validated_data):
        """
        Create the comment using the authenticated user.
        """

        user = self.context["request"].user

        return CommunityPostComment.objects.create(
            user=user,
            **validated_data,
        )


# ============================================================
# COMMUNITY POST COMMENT — UPDATE INPUT
# ============================================================

class CommunityPostCommentUpdateSerializer(
    serializers.ModelSerializer
):
    """
    Serializer used when a user edits their comment.

    Only the comment content can be changed.

    The post, parent, author, counters, moderation state,
    edit state, and timestamps cannot be modified by the client.
    """

    class Meta:
        model = CommunityPostComment

        fields = [
            "content",
        ]

    def update(self, instance, validated_data):
        """
        Update the comment and mark it as edited.
        """

        instance.content = validated_data["content"]
        instance.is_edited = True

        instance.save(
            update_fields=[
                "content",
                "is_edited",
                "updated_at",
            ]
        )

        return instance


# ============================================================
# ============================================================
# COMMUNITY POST REPORT
# ============================================================
# ============================================================

class CommunityPostReportSerializer(BaseModelSerializer):
    """
    Read-only representation of a report submitted against
    a community post.
    """

    class Meta:
        model = CommunityPostReport

        fields = [
            "id",
            "user",
            "post",
            "reason",
            "details",
            "created_at",
        ]

        read_only_fields = fields


class CommunityPostReportCreateSerializer(
    serializers.ModelSerializer
):
    """
    Serializer used when a user reports a community post.

    The authenticated user and reported post are assigned
    server-side.
    """

    class Meta:
        model = CommunityPostReport

        fields = [
            "reason",
            "details",
        ]


# ============================================================
# COMMUNITY POST COMMENT REPORT
# ============================================================

class CommunityPostCommentReportSerializer(
    BaseModelSerializer
):
    """
    Read-only representation of a report submitted against
    a community post comment.
    """

    class Meta:
        model = CommunityPostCommentReport

        fields = [
            "id",
            "user",
            "comment",
            "reason",
            "details",
            "created_at",
        ]

        read_only_fields = fields


class CommunityPostCommentReportCreateSerializer(
    serializers.ModelSerializer
):
    """
    Serializer used when a user reports a community post comment.

    The authenticated user and reported comment are assigned
    server-side.
    """

    class Meta:
        model = CommunityPostCommentReport

        fields = [
            "reason",
            "details",
        ]