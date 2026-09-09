from unfold.admin import ModelAdmin as UnfoldModelAdmin
from django.contrib import admin

from .models import (
    Album,
    AlbumFavorite,
    AlbumRating,
    AlbumTrack,
    Artist,
    ArtistFollow,
    CommunityPost,
    CommunityPostComment,
    CommunityPostCommentLike,
    CommunityPostCommentReport,
    CommunityPostLike,
    CommunityPostReport,
    CommunityPostTarget,
    EditorialArticle,
    EditorialArticleLike,
    EditorialArticleReport,
    EditorialComment,
    EditorialCommentLike,
    EditorialCommentReport,
    Genre,
    Song,
    SongFavorite,
    SongRating,
    UserFollow,
)


# ============================================================
# BASE ADMIN
# ============================================================

class TimeStampedAdmin(UnfoldModelAdmin):
    """
    Base admin configuration for models using TimeStampedModel.
    """

    readonly_fields = ("created_at", "updated_at")


# ============================================================
# GENRE
# ============================================================

@admin.register(Genre)
class GenreAdmin(TimeStampedAdmin):
    list_display = (
        "name",
        "slug",
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "slug",
        "description",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    ordering = ("name",)

    prepopulated_fields = {
        "slug": ("name",),
    }

    fieldsets = (
        (
            "Genre Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_active",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


# ============================================================
# ARTIST
# ============================================================

@admin.register(Artist)
class ArtistAdmin(TimeStampedAdmin):
    list_display = (
        "name",
        "country",
        "followers_count",
        "is_verified",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
        "bio",
        "country",
    )

    list_filter = (
        "is_verified",
        "is_active",
        "country",
        "created_at",
    )

    ordering = ("name",)

    prepopulated_fields = {
        "slug": ("name",),
    }

    readonly_fields = (
        "followers_count",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Artist Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "bio",
                    "country",
                )
            },
        ),
        # (
        #     "Images",
        #     {
        #         "fields": (
        #             "image",
        #         )
        #     },
        # ),
        (
            "Official Links",
            {
                "fields": (
                    "website_url",
                    "spotify_url",
                    "apple_music_url",
                    "youtube_url",
                    "instagram_url",
                )
            },
        ),
        (
            "Audience & Status",
            {
                "fields": (
                    "followers_count",
                    "is_verified",
                    "is_active",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


# ============================================================
# ALBUM TRACK INLINE
# ============================================================

class AlbumTrackInline(admin.TabularInline):
    model = AlbumTrack
    extra = 1

    autocomplete_fields = (
        "song",
    )

    fields = (
        "track_number",
        "song",
    )

    ordering = (
        "track_number",
    )


# ============================================================
# ALBUM
# ============================================================

@admin.register(Album)
class AlbumAdmin(TimeStampedAdmin):
    list_display = (
        "title",
        "release_type",
        "release_date",
        "status",
        "is_featured",
        "favorites_count",
        "ratings_count",
        "reviewed_by",
        "created_at",
    )

    search_fields = (
        "title",
        "slug",
        "description",
        "editorial_review",
        "artists__name",
    )

    list_filter = (
        "release_type",
        "status",
        "is_featured",
        "release_date",
        "created_at",
    )

    autocomplete_fields = (
        "reviewed_by",
    )

    filter_horizontal = (
        "artists",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    date_hierarchy = "release_date"

    ordering = (
        "-release_date",
        "-created_at",
    )

    readonly_fields = (
        "favorites_count",
        "ratings_count",
        "created_at",
        "updated_at",
    )

    inlines = (
        AlbumTrackInline,
    )

    fieldsets = (
        (
            "Album Information",
            {
                "fields": (
                    "title",
                    "slug",
                    "description",
                    "release_type",
                    "release_date",
                    "artists",
                )
            },
        ),
        (
            "Editorial Review",
            {
                "fields": (
                    "editorial_review",
                    "reviewed_by",
                )
            },
        ),
        (
            "Official Listening",
            {
                "fields": (
                    "spotify_url",
                    "apple_music_url",
                    "youtube_url",
                )
            },
        ),
        (
            "Publishing",
            {
                "fields": (
                    "status",
                    "published_at",
                    "is_featured",
                )
            },
        ),
        (
            "Engagement",
            {
                "fields": (
                    "favorites_count",
                    "ratings_count",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


# ============================================================
# SONG
# ============================================================

@admin.register(Song)
class SongAdmin(TimeStampedAdmin):
    list_display = (
        "title",
        "album",
        "release_date",
        "status",
        "is_featured",
        "editorial_score",
        "favorites_count",
        "ratings_count",
        "created_at",
    )

    search_fields = (
        "title",
        "slug",
        "description",
        "editorial_review",
        "artists__name",
        "featured_artists__name",
        "album__title",
    )

    list_filter = (
        "status",
        "is_featured",
        "release_date",
        "genres",
        "album",
        "created_at",
    )

    autocomplete_fields = (
        "album",
        "genres",
        "artists",
        "featured_artists",
        "reviewed_by",
    )

    date_hierarchy = "release_date"

    prepopulated_fields = {
        "slug": ("title",),
    }

    ordering = (
        "-release_date",
        "-created_at",
    )

    readonly_fields = (
        "favorites_count",
        "ratings_count",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Song Information",
            {
                "fields": (
                    "title",
                    "slug",
                    "description",
                    "album",
                    "artists",
                    "featured_artists",
                    "genres",
                    "release_date",
                )
            },
        ),
        (
            "Editorial Review",
            {
                "fields": (
                    "editorial_review",
                    "editorial_score",
                    "reviewed_by",
                )
            },
        ),
        (
            "Official Listening",
            {
                "fields": (
                    "spotify_url",
                    "apple_music_url",
                    "youtube_url",
                )
            },
        ),
        (
            "Publishing",
            {
                "fields": (
                    "status",
                    "published_at",
                    "is_featured",
                )
            },
        ),
        (
            "Engagement",
            {
                "fields": (
                    "favorites_count",
                    "ratings_count",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


# ============================================================
# ALBUM TRACK
# ============================================================

@admin.register(AlbumTrack)
class AlbumTrackAdmin(TimeStampedAdmin):
    list_display = (
        "album",
        "track_number",
        "song",
        "created_at",
    )

    search_fields = (
        "album__title",
        "song__title",
        "song__artists__name",
    )

    list_filter = (
        "album",
        "created_at",
    )

    autocomplete_fields = (
        "album",
        "song",
    )

    ordering = (
        "album",
        "track_number",
    )


# ============================================================
# SONG RATINGS
# ============================================================

@admin.register(SongRating)
class SongRatingAdmin(TimeStampedAdmin):
    list_display = (
        "song",
        "user",
        "rating",
        "created_at",
    )

    search_fields = (
        "song__title",
        "song__artists__name",
        "user__username",
        "user__email",
    )

    list_filter = (
        "rating",
        "created_at",
    )

    autocomplete_fields = (
        "user",
        "song",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    readonly_fields = (
        "user",
        "song",
        "rating",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False


# ============================================================
# ALBUM RATINGS
# ============================================================

@admin.register(AlbumRating)
class AlbumRatingAdmin(TimeStampedAdmin):
    list_display = (
        "album",
        "user",
        "rating",
        "created_at",
    )

    search_fields = (
        "album__title",
        "album__artists__name",
        "user__username",
        "user__email",
    )

    list_filter = (
        "rating",
        "created_at",
    )

    autocomplete_fields = (
        "user",
        "album",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    readonly_fields = (
        "user",
        "album",
        "rating",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False


# ============================================================
# EDITORIAL ARTICLE
# ============================================================

@admin.register(EditorialArticle)
class EditorialArticleAdmin(TimeStampedAdmin):
    list_display = (
        "title",
        "author",
        "status",
        "published_at",
        "is_featured",
        "views_count",
        "likes_count",
        "comments_count",
        "created_at",
    )

    search_fields = (
        "title",
        "slug",
        "excerpt",
        "content",
        "author__username",
        "author__email",
        "song__title",
        "artist__name",
        "album__title",
        "genres__name",
    )

    list_filter = (
        "status",
        "is_featured",
        "genres",
        "published_at",
        "created_at",
    )

    autocomplete_fields = (
        "author",
        "song",
        "artist",
        "album",
    )

    filter_horizontal = (
        "genres",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    date_hierarchy = "published_at"

    ordering = (
        "-published_at",
        "-created_at",
    )

    readonly_fields = (
        "views_count",
        "likes_count",
        "comments_count",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Article",
            {
                "fields": (
                    "title",
                    "slug",
                    "author",
                    "excerpt",
                    "content",
                )
            },
        ),
        (
            "Related Music",
            {
                "fields": (
                    "song",
                    "artist",
                    "album",
                    "genres",
                )
            },
        ),
        (
            "Publishing",
            {
                "fields": (
                    "status",
                    "published_at",
                    "is_featured",
                )
            },
        ),
        (
            "Engagement",
            {
                "fields": (
                    "views_count",
                    "likes_count",
                    "comments_count",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.action(description="Publish selected articles")
    def publish_articles(self, request, queryset):
        queryset.update(status="published")

    @admin.action(description="Archive selected articles")
    def archive_articles(self, request, queryset):
        queryset.update(status="archived")

    actions = (
        "publish_articles",
        "archive_articles",
    )


# ============================================================
# COMMUNITY POST TARGET
# ============================================================

class CommunityPostTargetInline(admin.StackedInline):
    model = CommunityPostTarget

    extra = 0
    max_num = 1

    autocomplete_fields = (
        "song",
        "album",
        "artist",
    )

    fieldsets = (
        (
            "Target",
            {
                "fields": (
                    "target_type",
                    "song",
                    "album",
                    "artist",
                )
            },
        ),
        (
            "External Identity",
            {
                "fields": (
                    "external_provider",
                    "external_content_type",
                    "external_id",
                )
            },
        ),
        (
            "Music Snapshot",
            {
                "fields": (
                    "title",
                    "artist_name",
                    "album_name",
                    "artwork_url",
                    "preview_url",
                    "spotify_url",
                    "apple_music_url",
                    "metadata",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# ============================================================
# COMMUNITY POST
# ============================================================

@admin.register(CommunityPost)
class CommunityPostAdmin(TimeStampedAdmin):
    list_display = (
        "id",
        "user",
        "target_display",
        "rating",
        "views_count",
        "likes_count",
        "comments_count",
        "status",
        "is_edited",
        "created_at",
    )

    search_fields = (
        "content",
        "user__username",
        "user__email",
        "target__title",
        "target__artist_name",
        "target__album_name",
        "target__external_id",
    )

    list_filter = (
        "status",
        "is_edited",
        "created_at",
    )

    autocomplete_fields = (
        "user",
    )

    readonly_fields = (
        "user",
        "views_count",
        "likes_count",
        "comments_count",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    inlines = (
        CommunityPostTargetInline,
    )

    fieldsets = (
        (
            "Post",
            {
                "fields": (
                    "user",
                    "content",
                    "rating",
                )
            },
        ),
        (
            "Engagement",
            {
                "fields": (
                    "views_count",
                    "likes_count",
                    "comments_count",
                )
            },
        ),
        (
            "Moderation",
            {
                "fields": (
                    "status",
                    "is_edited",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(description="Target")
    def target_display(self, obj):
        target = getattr(obj, "target", None)

        if not target:
            return "—"

        if target.title:
            if target.artist_name:
                return f"{target.title} — {target.artist_name}"
            return target.title

        return "Unknown target"

    @admin.action(description="Publish selected posts")
    def publish_posts(self, request, queryset):
        queryset.update(status="published")

    @admin.action(description="Hide selected posts")
    def hide_posts(self, request, queryset):
        queryset.update(status="hidden")

    @admin.action(description="Remove selected posts")
    def remove_posts(self, request, queryset):
        queryset.update(status="removed")

    actions = (
        "publish_posts",
        "hide_posts",
        "remove_posts",
    )


# ============================================================
# COMMUNITY POST LIKES
# ============================================================

@admin.register(CommunityPostLike)
class CommunityPostLikeAdmin(TimeStampedAdmin):
    list_display = (
        "post",
        "user",
        "created_at",
    )

    search_fields = (
        "post__content",
        "post__user__username",
        "user__username",
        "user__email",
    )

    list_filter = (
        "created_at",
    )

    autocomplete_fields = (
        "post",
        "user",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "post",
        "user",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False


# ============================================================
# COMMUNITY POST COMMENTS
# ============================================================

@admin.register(CommunityPostComment)
class CommunityPostCommentAdmin(TimeStampedAdmin):
    list_display = (
        "short_content",
        "user",
        "post",
        "parent",
        "views_count",
        "likes_count",
        "replies_count",
        "status",
        "is_edited",
        "created_at",
    )

    search_fields = (
        "content",
        "user__username",
        "user__email",
        "post__content",
        "post__target__title",
        "post__target__artist_name",
        "post__target__album_name",
    )

    list_filter = (
        "status",
        "is_edited",
        "created_at",
    )

    autocomplete_fields = (
        "user",
        "post",
        "parent",
    )

    readonly_fields = (
        "views_count",
        "likes_count",
        "replies_count",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Comment",
            {
                "fields": (
                    "user",
                    "post",
                    "parent",
                    "content",
                )
            },
        ),
        (
            "Engagement",
            {
                "fields": (
                    "views_count",
                    "likes_count",
                    "replies_count",
                )
            },
        ),
        (
            "Moderation",
            {
                "fields": (
                    "status",
                    "is_edited",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(description="Comment")
    def short_content(self, obj):
        if len(obj.content) > 80:
            return f"{obj.content[:80]}..."
        return obj.content

    @admin.action(description="Publish selected comments")
    def publish_comments(self, request, queryset):
        queryset.update(status="published")

    @admin.action(description="Hide selected comments")
    def hide_comments(self, request, queryset):
        queryset.update(status="hidden")

    @admin.action(description="Remove selected comments")
    def remove_comments(self, request, queryset):
        queryset.update(status="removed")

    actions = (
        "publish_comments",
        "hide_comments",
        "remove_comments",
    )


# ============================================================
# COMMUNITY POST COMMENT LIKES
# ============================================================

@admin.register(CommunityPostCommentLike)
class CommunityPostCommentLikeAdmin(TimeStampedAdmin):
    list_display = (
        "comment",
        "user",
        "created_at",
    )

    search_fields = (
        "comment__content",
        "user__username",
        "user__email",
    )

    list_filter = (
        "created_at",
    )

    autocomplete_fields = (
        "comment",
        "user",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "comment",
        "user",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False


# ============================================================
# EDITORIAL ARTICLE LIKES
# ============================================================

@admin.register(EditorialArticleLike)
class EditorialArticleLikeAdmin(TimeStampedAdmin):
    list_display = (
        "article",
        "user",
        "created_at",
    )

    search_fields = (
        "article__title",
        "article__slug",
        "user__username",
        "user__email",
    )

    list_filter = (
        "created_at",
    )

    autocomplete_fields = (
        "article",
        "user",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "article",
        "user",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False


# ============================================================
# EDITORIAL COMMENTS
# ============================================================

@admin.register(EditorialComment)
class EditorialCommentAdmin(TimeStampedAdmin):
    list_display = (
        "short_content",
        "user",
        "article",
        "parent",
        "views_count",
        "likes_count",
        "replies_count",
        "status",
        "is_edited",
        "created_at",
    )

    search_fields = (
        "content",
        "user__username",
        "user__email",
        "article__title",
        "article__slug",
    )

    list_filter = (
        "status",
        "is_edited",
        "created_at",
    )

    autocomplete_fields = (
        "user",
        "article",
        "parent",
    )

    readonly_fields = (
        "views_count",
        "likes_count",
        "replies_count",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Comment",
            {
                "fields": (
                    "user",
                    "article",
                    "parent",
                    "content",
                )
            },
        ),
        (
            "Engagement",
            {
                "fields": (
                    "views_count",
                    "likes_count",
                    "replies_count",
                )
            },
        ),
        (
            "Moderation",
            {
                "fields": (
                    "status",
                    "is_edited",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(description="Comment")
    def short_content(self, obj):
        if len(obj.content) > 80:
            return f"{obj.content[:80]}..."
        return obj.content

    @admin.action(description="Publish selected comments")
    def publish_comments(self, request, queryset):
        queryset.update(status="published")

    @admin.action(description="Hide selected comments")
    def hide_comments(self, request, queryset):
        queryset.update(status="hidden")

    @admin.action(description="Remove selected comments")
    def remove_comments(self, request, queryset):
        queryset.update(status="removed")

    actions = (
        "publish_comments",
        "hide_comments",
        "remove_comments",
    )


# ============================================================
# EDITORIAL COMMENT LIKES
# ============================================================

@admin.register(EditorialCommentLike)
class EditorialCommentLikeAdmin(TimeStampedAdmin):
    list_display = (
        "comment",
        "user",
        "created_at",
    )

    search_fields = (
        "comment__content",
        "comment__article__title",
        "user__username",
        "user__email",
    )

    list_filter = (
        "created_at",
    )

    autocomplete_fields = (
        "comment",
        "user",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "comment",
        "user",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False


# ============================================================
# SONG FAVORITES
# ============================================================

@admin.register(SongFavorite)
class SongFavoriteAdmin(TimeStampedAdmin):
    list_display = (
        "song",
        "user",
        "created_at",
    )

    search_fields = (
        "song__title",
        "song__artists__name",
        "user__username",
        "user__email",
    )

    list_filter = (
        "created_at",
    )

    autocomplete_fields = (
        "song",
        "user",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "song",
        "user",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False


# ============================================================
# ALBUM FAVORITES
# ============================================================

@admin.register(AlbumFavorite)
class AlbumFavoriteAdmin(TimeStampedAdmin):
    list_display = (
        "album",
        "user",
        "created_at",
    )

    search_fields = (
        "album__title",
        "album__artists__name",
        "user__username",
        "user__email",
    )

    list_filter = (
        "created_at",
    )

    autocomplete_fields = (
        "album",
        "user",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "album",
        "user",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False


# ============================================================
# ARTIST FOLLOWS
# ============================================================

@admin.register(ArtistFollow)
class ArtistFollowAdmin(TimeStampedAdmin):
    list_display = (
        "artist",
        "user",
        "created_at",
    )

    search_fields = (
        "artist__name",
        "artist__slug",
        "user__username",
        "user__email",
    )

    list_filter = (
        "created_at",
    )

    autocomplete_fields = (
        "artist",
        "user",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "artist",
        "user",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False


# ============================================================
# USER FOLLOWS
# ============================================================

@admin.register(UserFollow)
class UserFollowAdmin(TimeStampedAdmin):
    list_display = (
        "follower",
        "following",
        "created_at",
    )

    search_fields = (
        "follower__username",
        "follower__email",
        "following__username",
        "following__email",
    )

    list_filter = (
        "created_at",
    )

    autocomplete_fields = (
        "follower",
        "following",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "follower",
        "following",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False


# ============================================================
# COMMUNITY POST REPORTS
# ============================================================

@admin.register(CommunityPostReport)
class CommunityPostReportAdmin(TimeStampedAdmin):
    list_display = (
        "post",
        "user",
        "reason",
        "created_at",
    )

    search_fields = (
        "post__content",
        "post__target__title",
        "post__target__artist_name",
        "user__username",
        "user__email",
    )

    list_filter = (
        "reason",
        "created_at",
    )

    autocomplete_fields = (
        "post",
        "user",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    readonly_fields = (
        "post",
        "user",
        "reason",
        "details",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False


# ============================================================
# COMMUNITY POST COMMENT REPORTS
# ============================================================

@admin.register(CommunityPostCommentReport)
class CommunityPostCommentReportAdmin(TimeStampedAdmin):
    list_display = (
        "comment",
        "user",
        "reason",
        "created_at",
    )

    search_fields = (
        "comment__content",
        "comment__post__content",
        "user__username",
        "user__email",
    )

    list_filter = (
        "reason",
        "created_at",
    )

    autocomplete_fields = (
        "comment",
        "user",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    readonly_fields = (
        "comment",
        "user",
        "reason",
        "details",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False


# ============================================================
# EDITORIAL ARTICLE REPORTS
# ============================================================

@admin.register(EditorialArticleReport)
class EditorialArticleReportAdmin(TimeStampedAdmin):
    list_display = (
        "article",
        "user",
        "reason",
        "created_at",
    )

    search_fields = (
        "article__title",
        "article__slug",
        "user__username",
        "user__email",
    )

    list_filter = (
        "reason",
        "created_at",
    )

    autocomplete_fields = (
        "article",
        "user",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    readonly_fields = (
        "article",
        "user",
        "reason",
        "details",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False


# ============================================================
# EDITORIAL COMMENT REPORTS
# ============================================================

@admin.register(EditorialCommentReport)
class EditorialCommentReportAdmin(TimeStampedAdmin):
    list_display = (
        "comment",
        "user",
        "reason",
        "created_at",
    )

    search_fields = (
        "comment__content",
        "comment__article__title",
        "user__username",
        "user__email",
    )

    list_filter = (
        "reason",
        "created_at",
    )

    autocomplete_fields = (
        "comment",
        "user",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    readonly_fields = (
        "comment",
        "user",
        "reason",
        "details",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False