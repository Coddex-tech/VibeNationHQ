from rest_framework import serializers

from django.contrib.auth import get_user_model

from music.models import (
    Album,
    Artist,
    CommunityPost,
    CommunityPostComment,
    CommunityPostCommentReport,
    CommunityPostReport,
    CommunityPostTarget,
    Song,
)

from .base import (
    BaseModelSerializer,
    validate_half_star_rating,
)

from .catalog import (
    AlbumCardSerializer,
    ArtistCardSerializer,
    SongCardSerializer,
)


User = get_user_model()


# ============================================================
# USER DETAIL
# ============================================================



class CommunityUserSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "is_following",
        ]
        read_only_fields = fields

    def get_is_following(self, obj):
        """
        Read the follow state annotated by the queryset.

        The default is False for contexts that don't annotate
        the user, such as comment serialization.
        """
        return bool(
            getattr(
                obj,
                "is_following",
                False,
            )
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

    For canonical Song targets, preview_url is resolved from
    the Song's provider identity records rather than stored
    directly on the Song model.
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

    preview_url = serializers.SerializerMethodField()

    def get_preview_url(self, obj):
        """
        Return an available provider preview URL for a
        canonical Song target.

        Provider preview URLs live on MusicProviderIdentity,
        not on the canonical Song model.

        The community post views prefetch the provider
        identities, so this method can resolve the URL
        without causing an additional query per post.
        """

        if (
            obj.target_type
            != CommunityPostTarget.TargetType.SONG
        ):
            return obj.preview_url or None

        song = obj.song

        if song is None:
            return None

        prefetched_objects = getattr(
            song,
            "_prefetched_objects_cache",
            {},
        )

        provider_identities = prefetched_objects.get(
            "provider_identities",
        )

        if provider_identities is None:
            return None

        for identity in provider_identities:
            if identity.preview_url:
                return identity.preview_url

        return None

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

            # External metadata snapshot / resolved preview
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


class CommunityPostTargetCreateSerializer(
    serializers.Serializer,
):
    """
    Validates the canonical music target a user wants
    to attach to a community post.

    External provider results must first pass through the
    music provider import pipeline and become canonical
    VibeNationHQ records.

    Therefore, the community post API does not directly
    create external targets.

    A Song or Album does not need to be catalog-published
    before it can be attached to a community post. Draft
    canonical records are allowed because community usage
    and catalog publication are separate concerns.

    Archived records cannot be attached.
    """

    target_type = serializers.ChoiceField(
        choices=CommunityPostTarget.TargetType.choices,
    )

    # --------------------------------------------------------
    # Internal targets
    #
    # Community posts may reference canonical Songs/Albums
    # that are still in editorial DRAFT status.
    #
    # ARCHIVED records remain excluded.
    # --------------------------------------------------------

    song = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.exclude(
            status=Song.Status.ARCHIVED,
        ),
        required=False,
    )

    album = serializers.PrimaryKeyRelatedField(
        queryset=Album.objects.exclude(
            status=Album.Status.ARCHIVED,
        ),
        required=False,
    )

    artist = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(),
        required=False,
    )

    # --------------------------------------------------------
    # External fields
    #
    # These are intentionally defined so direct external
    # attachment attempts can be rejected explicitly.
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

        external_provider = attrs.get(
            "external_provider",
        )
        external_content_type = attrs.get(
            "external_content_type",
        )
        external_id = attrs.get(
            "external_id",
        )

        has_external_fields = any(
            value is not None
            for value in (
                external_provider,
                external_content_type,
                external_id,
            )
        )

        if target_type == CommunityPostTarget.TargetType.SONG:
            if song is None:
                raise serializers.ValidationError({
                    "song": (
                        "A song is required when "
                        "target_type is 'song'."
                    ),
                })

            if album is not None or artist is not None:
                raise serializers.ValidationError(
                    "A song target cannot include "
                    "an album or artist."
                )

            if has_external_fields:
                raise serializers.ValidationError(
                    "A song target cannot include "
                    "external target fields."
                )

            return attrs

        if target_type == CommunityPostTarget.TargetType.ALBUM:
            if album is None:
                raise serializers.ValidationError({
                    "album": (
                        "An album is required when "
                        "target_type is 'album'."
                    ),
                })

            if song is not None or artist is not None:
                raise serializers.ValidationError(
                    "An album target cannot include "
                    "a song or artist."
                )

            if has_external_fields:
                raise serializers.ValidationError(
                    "An album target cannot include "
                    "external target fields."
                )

            return attrs

        if target_type == CommunityPostTarget.TargetType.ARTIST:
            if artist is None:
                raise serializers.ValidationError({
                    "artist": (
                        "An artist is required when "
                        "target_type is 'artist'."
                    ),
                })

            if song is not None or album is not None:
                raise serializers.ValidationError(
                    "An artist target cannot include "
                    "a song or album."
                )

            if has_external_fields:
                raise serializers.ValidationError(
                    "An artist target cannot include "
                    "external target fields."
                )

            return attrs

        if target_type == CommunityPostTarget.TargetType.EXTERNAL:
            raise serializers.ValidationError({
                "target_type": (
                    "External music results must be imported "
                    "into the VibeNationHQ catalog before "
                    "they can be attached to a community post."
                ),
            })

        raise serializers.ValidationError({
            "target_type": (
                "Invalid community post target type."
            ),
        })


# ============================================================
# COMMUNITY POST — READ
# ============================================================


class CommunityPostSerializer(BaseModelSerializer):
    """
    Read-only representation of a community post.

    favorites_count is dynamically annotated by querysets
    that need the total favorite count. It is intentionally
    not stored on the CommunityPost model.
    """

    user = CommunityUserSerializer(
        read_only=True,
    )

    target = CommunityPostTargetSerializer(
        read_only=True,
    )

    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()

    class Meta:
        model = CommunityPost

        fields = [
            "id",

            # Author
            "user",

            # Content
            "content",
            "slug",
            "rating",

            # Target
            "target",

            # Engagement
            "views_count",
            "likes_count",
            "comments_count",
            "favorites_count",
            "is_liked",
            "is_favorited",

            # Moderation / state
            "status",
            "is_edited",

            # Timestamps
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields

    def get_is_liked(self, obj):
        request = self.context.get("request")

        if (
            request is None
            or not request.user.is_authenticated
        ):
            return False

        return bool(
            getattr(
                obj,
                "is_liked",
                False,
            )
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")

        if (
            request is None
            or not request.user.is_authenticated
        ):
            return False

        return bool(
            getattr(
                obj,
                "is_favorited",
                False,
            )
        )

    def get_favorites_count(self, obj):
        return int(
            getattr(
                obj,
                "favorites_count",
                0,
            )
        )


# ============================================================
# COMMUNITY POST — CREATE INPUT
# ============================================================


class CommunityPostCreateSerializer(
    serializers.ModelSerializer,
):
    """
    Validates input for creating a community post.

    A post may be:

    - text-only
    - attached to a Song
    - attached to an Album
    - attached to an Artist

    Ratings are only valid when the post has a Song or
    Album target.

    Database creation is handled by CommunityPostService.
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

    def validate(self, attrs):
        content = attrs.get(
            "content",
            "",
        )

        if not isinstance(content, str):
            raise serializers.ValidationError({
                "content": (
                    "Post content must be a valid string."
                ),
            })

        content = content.strip()

        if not content:
            raise serializers.ValidationError({
                "content": (
                    "Post content cannot be empty."
                ),
            })

        attrs["content"] = content

        rating = attrs.get("rating")
        target = attrs.get("target")

        # No target means this is an ordinary text post.
        if target is None:
            if rating is not None:
                raise serializers.ValidationError({
                    "rating": (
                        "A rating can only be added when "
                        "a song or album is attached."
                    ),
                })

            return attrs

        target_type = target["target_type"]

        # Ratings are valid only for songs and albums.
        if rating is not None:
            if target_type not in {
                CommunityPostTarget.TargetType.SONG,
                CommunityPostTarget.TargetType.ALBUM,
            }:
                raise serializers.ValidationError({
                    "rating": (
                        "A rating can only be added to "
                        "a song or album."
                    ),
                })

        return attrs


# ============================================================
# COMMUNITY POST — UPDATE INPUT
# ============================================================


class CommunityPostUpdateSerializer(
    serializers.ModelSerializer,
):
    """
    Serializer used when a user edits their community post.

    Users can update:

    - content
    - rating

    The attached target cannot be changed after creation.

    A rating remains valid only when the post has a Song or
    Album target.
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

    def validate(self, attrs):
        content = attrs.get(
            "content",
        )

        if content is not None:
            if not isinstance(content, str):
                raise serializers.ValidationError({
                    "content": (
                        "Post content must be a valid string."
                    ),
                })

            content = content.strip()

            if not content:
                raise serializers.ValidationError({
                    "content": (
                        "Post content cannot be empty."
                    ),
                })

            attrs["content"] = content

        if "rating" in attrs:
            rating = attrs["rating"]

            if rating is not None:
                target = getattr(
                    self.instance,
                    "target",
                    None,
                )

                if target is None:
                    raise serializers.ValidationError({
                        "rating": (
                            "A rating can only be added when "
                            "a song or album is attached."
                        ),
                    })

                if target.target_type not in {
                    CommunityPostTarget.TargetType.SONG,
                    CommunityPostTarget.TargetType.ALBUM,
                }:
                    raise serializers.ValidationError({
                        "rating": (
                            "A rating can only be added to "
                            "a song or album."
                        ),
                    })

        return attrs


# ============================================================
# COMMUNITY POST COMMENT — READ
# ============================================================
class CommunityPostCommentSerializer(
    BaseModelSerializer,
):
    """
    Read-only representation of a community post comment.
    """

    user = CommunityUserSerializer(
        read_only=True,
    )

    post_creator_id = serializers.IntegerField(
        source="post.user_id",
        read_only=True,
    )

    thread_replies_count = serializers.SerializerMethodField()

    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = CommunityPostComment

        fields = [
            "id",
            "user",
            "post",
            "post_creator_id",
            "parent",
            "content",

            "views_count",
            "likes_count",
            "replies_count",
            "thread_replies_count",

            "is_liked",

            "status",
            "is_edited",

            "created_at",
            "updated_at",
        ]

        read_only_fields = fields

    def get_is_liked(self, obj):
        """
        Read the like state annotated by the queryset.

        Anonymous users and querysets without the annotation
        safely default to False.
        """
        request = self.context.get("request")

        if (
            request is None
            or not request.user.is_authenticated
        ):
            return False

        return bool(
            getattr(
                obj,
                "is_liked",
                False,
            )
        )

    def get_thread_replies_count(self, obj):
        """
        Return the total number of published descendants
        belonging to a root comment, including nested replies.
        """
        # Nested replies do not display their own thread count.
        if obj.parent_id is not None:
            return 0

        # The root-list queryset annotates this count to avoid
        # making a separate database query for every root comment.
        annotated_count = getattr(obj, "thread_replies_count", None)

        if annotated_count is not None:
            return annotated_count

        # Fallback for objects serialized outside that queryset,
        # such as a newly created root comment.
        return obj.thread_replies.filter(
            status=CommunityPostComment.Status.PUBLISHED,
            post__status=CommunityPost.Status.PUBLISHED,
        ).count()


# ============================================================
# COMMUNITY POST COMMENT — CREATE INPUT
# ============================================================


class CommunityPostCommentCreateSerializer(
    serializers.ModelSerializer,
):
    """
    Validates input for creating a comment or reply.

    Database creation and comment counters are handled by
    CommunityPostCommentService.
    """

    content = serializers.CharField(
        max_length=10000,
        trim_whitespace=True,
        allow_blank=False,
    )

    class Meta:
        model = CommunityPostComment

        fields = [
            "post",
            "parent",
            "content",
        ]

    def validate_post(self, value):
        if value.status != CommunityPost.Status.PUBLISHED:
            raise serializers.ValidationError(
                "Comments can only be added to published posts."
            )

        return value

    def validate(self, attrs):
        post = attrs["post"]
        parent = attrs.get("parent")

        if parent is None:
            return attrs

        if parent.post_id != post.id:
            raise serializers.ValidationError({
                "parent": (
                    "The parent comment must belong "
                    "to the same post."
                ),
            })

        if parent.status != (
            CommunityPostComment.Status.PUBLISHED
        ):
            raise serializers.ValidationError({
                "parent": (
                    "You cannot reply to a hidden "
                    "or removed comment."
                ),
            })

        return attrs


# ============================================================
# COMMUNITY POST COMMENT — UPDATE INPUT
# ============================================================


class CommunityPostCommentUpdateSerializer(
    serializers.ModelSerializer,
):
    """
    Validates input when a user edits their comment.

    The API view/service must also enforce the 15-minute
    editing window and comment ownership.
    """

    content = serializers.CharField(
        max_length=10000,
        trim_whitespace=True,
        allow_blank=False,
    )

    class Meta:
        model = CommunityPostComment

        fields = [
            "content",
        ]

    def validate_content(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Comment content cannot be empty."
            )

        return value


# ============================================================
# COMMUNITY POST REPORT
# ============================================================


class CommunityPostReportSerializer(
    BaseModelSerializer,
):
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
    serializers.ModelSerializer,
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
    BaseModelSerializer,
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
    serializers.ModelSerializer,
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