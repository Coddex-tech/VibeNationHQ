from rest_framework import serializers
from django.conf import settings
from django.urls import reverse
from .models import Song, Artist, DJ, MusicComment, Album
from utils.date_time_extra import format_hybrid_time
from .utils.get_media import get_primary_media, attach_media

class ArtistSerializer(serializers.ModelSerializer):
    """
    Compact Artist serializer for nested API responses.
    """

    class Meta:
        model = Artist

        fields = (
            "id",
            "name",
            "bio",
        )

class SongCardSerializer(serializers.ModelSerializer):
    """
    Serializer for Song cards displayed across the site.
    """

    artists = ArtistSerializer(
        many=True,
        read_only=True
    )

    media = serializers.SerializerMethodField()

    friendly_date = serializers.SerializerMethodField()

    page_url = serializers.SerializerMethodField()

    is_dj = serializers.SerializerMethodField()

    class Meta:
        model = Song

        fields = (
            "id",
            "title",
            "slug",
            "artists",
            "media",
            "friendly_date",
            "page_url",
            "is_dj",
        )

    def get_media(self, obj):

        media = get_primary_media(obj)

        request = self.context.get("request")

        if request:
            media["url"] = request.build_absolute_uri(
                media["url"]
            )

        return MediaSerializer(media).data

    def get_friendly_date(self, obj):
        return format_hybrid_time(obj.release_date)

    def get_page_url(self, obj):

        request = self.context.get("request")

        url = reverse(
            "music:song_detail",
            kwargs={
                "slug": obj.slug
            }
        )

        if request:
            return request.build_absolute_uri(url)

        return url

    def get_is_dj(self, obj):
        return False

class GenreSerializer(serializers.Serializer):
    """
    Compact Genre serializer.
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()


class TagSerializer(serializers.Serializer):
    """
    Compact Tag serializer.
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    url = serializers.URLField()


class MediaSerializer(serializers.Serializer):
    """
    Unified media serializer.
    """

    type = serializers.CharField()
    url = serializers.URLField()
    alt = serializers.CharField()


class AudioSerializer(serializers.Serializer):
    """
    Audio file serializer.
    """

    url = serializers.URLField()


class SeoSerializer(serializers.Serializer):
    """
    SEO/OpenGraph serializer.
    """

    title = serializers.CharField()
    description = serializers.CharField()
    image = serializers.URLField()
    url = serializers.URLField()


# ============ NEW OPTIMIZING ================
class MusicReplySerializer(serializers.ModelSerializer):
    """
    Serializes a flattened reply node.
    """

    friendly_date = serializers.SerializerMethodField()
    display_name = serializers.CharField(read_only=True)
    is_verified_staff = serializers.BooleanField(read_only=True)
    replying_to = serializers.CharField(read_only=True)

    class Meta:
        model = MusicComment
        fields = [
            "id",
            "parent_id",
            "display_name",
            "content",
            "friendly_date",
            "is_verified_staff",
            "replying_to",
        ]

    def get_friendly_date(self, obj):
        return format_hybrid_time(obj.created_at)


class MusicCommentSerializer(serializers.ModelSerializer):
    """
    Root comment serializer.
    """

    friendly_date = serializers.SerializerMethodField()
    display_name = serializers.CharField(read_only=True)
    is_verified_staff = serializers.BooleanField(read_only=True)

    replies = serializers.SerializerMethodField()
    total_replies_count = serializers.SerializerMethodField()

    class Meta:
        model = MusicComment
        fields = [
            "id",
            "display_name",
            "content",
            "friendly_date",
            "is_verified_staff",
            "replies",
            "total_replies_count",
        ]

    def get_friendly_date(self, obj):
        return format_hybrid_time(obj.created_at)

    def get_replies(self, obj):
        initial_batch = obj.get_all_replies()[:settings.MUSIC_INITIAL_REPLIES]

        return MusicReplySerializer(
            initial_batch,
            many=True
        ).data

    def get_total_replies_count(self, obj):
        return len(obj.get_all_replies())


class SongDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Song detail page.
    """

    artists = serializers.SerializerMethodField()
    genres = serializers.SerializerMethodField()

    tags = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()

    friendly_date = serializers.SerializerMethodField()

    page_title = serializers.SerializerMethodField()
    is_dj = serializers.SerializerMethodField()

    audio = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    
    seo = serializers.SerializerMethodField()

    class Meta:
        model = Song

        fields = [
            "id",
            "title",
            "slug",
            "page_title",
            "description",
            "friendly_date",
            "duration",
            "views",
            "is_dj",
            "artists",
            "genres",
            "tags",
            "media",
            "audio",
            "download_url",
            "seo",
        ]

    def get_artists(self, obj):

        return ArtistSerializer(
            obj.artists.all(),
            many=True
            ).data

    def get_genres(self, obj):
        return GenreSerializer(
            obj.genres.all(),
            many=True
        ).data

    def get_tags(self, obj):
        request = self.context.get("request")
        tags = []
        for tag in obj.tags.all():
            url = reverse(
                "music:songs_by_tag",
                kwargs={
                    "tag_slug": tag.slug
                }
            )
            if request:
                url = request.build_absolute_uri(url)
            tags.append({
                "id": tag.id,
                "name": tag.name,
                "slug": tag.slug,
                "url": url,
            })
        return TagSerializer(
            tags,
            many=True
        ).data

    def get_media(self, obj):
        media = get_primary_media(obj)
        request = self.context.get("request")
        if request:
            media["url"] = request.build_absolute_uri(media["url"])
        return media

    def get_page_title(self, obj):
        return f"{obj.title} | VibeNation"

    def get_is_dj(self, obj):
        return False

    def get_audio(self, obj):
        if not obj.audio_file:
            return None

        request = self.context.get("request")
        url = obj.audio_file.url

        if request:
            url = request.build_absolute_uri(url)

        return AudioSerializer({
            "url": url
        }).data

    def get_download_url(self, obj):
        request = self.context.get("request")
        url = reverse(
            "music:download_song",
            kwargs={
                "slug": obj.slug
            }
        )
        if request:
            return request.build_absolute_uri(url)
        return url

    def get_seo(self, obj):
        request = self.context.get("request")
        page_url = ""

        if request:
            page_url = request.build_absolute_uri()
        media = self.get_media(obj)

        return SeoSerializer({
            "title": obj.title,
            "description": obj.description,
            "image": media["url"],
            "url": page_url,
        }).data

    def get_friendly_date(self, obj):
        return format_hybrid_time(obj.release_date)

class DJCardSerializer(serializers.ModelSerializer):
    """
    Compact serializer used for all DJ cards.
    """

    title = serializers.CharField(
        source="dj_name",
        read_only=True
    )

    artists = ArtistSerializer(
        many=True,
        read_only=True
    )

    media = serializers.SerializerMethodField()

    friendly_date = serializers.SerializerMethodField()

    page_url = serializers.SerializerMethodField()

    is_dj = serializers.SerializerMethodField()

    class Meta:
        model = DJ

        fields = (
            "id",
            "title",
            "slug",
            "artists",
            "media",
            "friendly_date",
            "page_url",
            "is_dj",
        )

    def get_is_dj(self, obj):
        return True

    def get_media(self, obj):
        return MediaSerializer(
            get_primary_media(obj),
            context=self.context
        ).data

    def get_friendly_date(self, obj):
        return format_hybrid_time(obj.created_at)

    def get_page_url(self, obj):

        request = self.context.get("request")

        url = reverse(
            "music:dj_detail",
            kwargs={
                "slug": obj.slug
            }
        )

        if request:
            return request.build_absolute_uri(url)

        return url

class AlbumCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = [
            "id",
            "title",
            "slug",
            "group",
            "artist",
        ]

class AlbumDetailSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(
        read_only=True
    )

    class Meta:
        model = Album
        fields = [
            "id",
            "title",
            "slug",
            "artist",
            "cover",
            "release_date",
        ]

# =================== ENTIRE DETAIL PAGE SERIALIZERS INFRASTRUCTURE ===================
class BaseMusicPageSerializer(serializers.Serializer):
    """
    Shared payload for Music and DJ detail pages.
    """

    detail = serializers.SerializerMethodField()

    related_songs = serializers.SerializerMethodField()

    latest_songs = serializers.SerializerMethodField()

    latest_mixtapes = serializers.SerializerMethodField()

    trending_songs = serializers.SerializerMethodField()

    # --------------------------------------------------
    # Child serializer must implement this.
    # --------------------------------------------------

    def get_detail(self, obj):
        raise NotImplementedError(
            "Subclasses must implement get_content()."
        )

    # --------------------------------------------------
    # Shared Sections
    # --------------------------------------------------

    def get_related_songs(self, obj):
        return SongCardSerializer(
            self.context["related_songs"],
            many=True,
            context=self.context,
        ).data

    def get_latest_songs(self, obj):
        return SongCardSerializer(
            self.context["latest_songs"],
            many=True,
            context=self.context,
        ).data

    def get_latest_mixtapes(self, obj):
        return DJCardSerializer(
            self.context["latest_djs"],
            many=True,
            context=self.context,
        ).data

    def get_trending_songs(self, obj):
        return SongCardSerializer(
            self.context["trending_songs"],
            many=True,
            context=self.context,
        ).data

class SongPageSerializer(BaseMusicPageSerializer):
    """
    Complete Song Detail page payload.
    """

    def get_detail(self, obj):
        return SongDetailSerializer(
            obj,
            context=self.context,
        ).data
    
# =======================
# FOR DJ
# =======================
class DJDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for DJ Mix detail page.
    """

    title = serializers.CharField(source="dj_name", read_only=True)
    artists = serializers.SerializerMethodField()
    genres = serializers.SerializerMethodField()

    media = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    friendly_date = serializers.SerializerMethodField()

    page_title = serializers.SerializerMethodField()
    is_dj = serializers.SerializerMethodField()

    audio = serializers.SerializerMethodField()

    seo = serializers.SerializerMethodField()

    class Meta:
        model = DJ

        fields = [
            "id",
            "title",
            "slug",
            "page_title",
            "description",
            "friendly_date",
            "duration",
            "is_dj",
            "artists",
            "genres",
            "media",
            "audio",
            "download_url",
            "seo",
        ]

    def get_artists(self, obj):
        return ArtistSerializer(
            obj.artists.all(),
            many=True
        ).data

    def get_genres(self, obj):
        return GenreSerializer(
            obj.genres.all(),
            many=True
        ).data

    def get_media(self, obj):
        media = get_primary_media(obj)

        request = self.context.get("request")

        if request:
            media["url"] = request.build_absolute_uri(
                media["url"]
            )

        return MediaSerializer(media).data

    def get_page_title(self, obj):
        return f"{obj.dj_name} | VibeNation"

    def get_is_dj(self, obj):
        return True

    def get_audio(self, obj):

        if not obj.dj_file:
            return None

        request = self.context.get("request")

        url = obj.dj_file.url

        if request:
            url = request.build_absolute_uri(url)

        return AudioSerializer({
            "url": url
        }).data

    def get_download_url(self, obj):
        request = self.context.get("request")
        url = reverse(
            "music:download_song",
            kwargs={
                "slug": obj.slug
            }
        )
        if request:
            return request.build_absolute_uri(url)
        return url

    def get_seo(self, obj):

        request = self.context.get("request")

        page_url = ""

        if request:
            page_url = request.build_absolute_uri()

        media = self.get_media(obj)

        return SeoSerializer({
            "title": obj.dj_name,
            "description": obj.description,
            "image": media["url"],
            "url": page_url,
        }).data

    def get_friendly_date(self, obj):
        return format_hybrid_time(obj.created_at)

class DJPageSerializer(BaseMusicPageSerializer):
    """
    Complete DJ Detail page payload.
    """

    def get_detail(self, obj):
        return DJDetailSerializer(
            obj,
            context=self.context,
        ).data
