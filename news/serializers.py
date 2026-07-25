from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings

from utils.date_time_extra import format_hybrid_time
from .models import News, Category, NewsComment
from music.serializers import SongCardSerializer

User = get_user_model()

class AuthorSerializer(serializers.ModelSerializer):
    """Minimal user serializer to keep payloads tight."""
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'full_name'
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class CategorySerializer(serializers.ModelSerializer):
    """Maps name and slug properties for clean frontend label rendering."""
    news_count = serializers.IntegerField(read_only=True, required=False)
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'news_count'
        ]

class NewsHomeSerializer(serializers.Serializer):
    """
    Homepage payload serializer.
    """

    hero_blocks = serializers.SerializerMethodField()
    music_feeds = serializers.SerializerMethodField()
    categorized_feeds = serializers.SerializerMethodField()


    def get_hero_blocks(self, obj):
        ctx = self.context

        return {
            "global_featured": NewsDetailSerializer(
                obj.get("global_featured"),
                context=ctx
            ).data if obj.get("global_featured") else None,

            "sponsored_feature": NewsCardSerializer(
                obj.get("sponsored_feature"),
                context=ctx
            ).data if obj.get("sponsored_feature") else None,

            "top_news": NewsCardSerializer(
                obj.get("top_news"),
                many=True,
                context=ctx
            ).data,

            "latest_news": NewsCardSerializer(
                obj.get("latest_news"),
                many=True,
                context=ctx
            ).data,
        }


    def get_music_feeds(self, obj):
        ctx = self.context
        return {
            "latest_songs": SongCardSerializer(
                obj.get("latest_songs"),
                many=True,
                context=ctx
            ).data,
        }

    def get_categorized_feeds(self, obj):
        ctx = self.context
        return {
            key: NewsCardSerializer(
                value,
                many=True,
                context=ctx
            ).data

            for key, value in obj.get("categorized_feeds").items()
        }

class NewsCardSerializer(serializers.ModelSerializer):
    """
    Compact serializer for news cards displayed across the site.
    """
    friendly_date = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            "id",
            "title",
            "slug",
            "friendly_date",
            "thumbnail_url",
        ]

    def get_thumbnail_url(self, obj):
        """Ensures absolute image target resolution regardless of environment."""
        if obj.thumbnail:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None

    def get_friendly_date(self, obj):
        return format_hybrid_time(
            obj.date_published
        )

# ============= NEW OPTIMIZING ============
class NewsReplySerializer(serializers.ModelSerializer):
    """Linear child reply objects mapping tree-nodes cleanly."""
    friendly_date = serializers.SerializerMethodField()
    display_name = serializers.CharField(read_only=True)
    is_verified_staff = serializers.BooleanField(read_only=True)
    replying_to = serializers.CharField(read_only=True)

    class Meta:
        model = NewsComment
        fields = [
            'id', 'parent_id', 'display_name', 'content', 
            'friendly_date', 'is_verified_staff', 'replying_to'
        ]

    def get_friendly_date(self, obj):
        return format_hybrid_time(obj.created_at)


class NewsCommentSerializer(serializers.ModelSerializer):
    """Root comment nodes packaging truncated replies window (:3)."""
    friendly_date = serializers.SerializerMethodField()
    display_name = serializers.CharField(read_only=True)
    is_verified_staff = serializers.BooleanField(read_only=True)
    replies = serializers.SerializerMethodField()
    total_replies_count = serializers.SerializerMethodField()

    class Meta:
        model = NewsComment
        fields = [
            'id', 'display_name', 'content', 'friendly_date', 
            'is_verified_staff', 'replies', 'total_replies_count'
        ]

    def get_friendly_date(self, obj):
        return format_hybrid_time(obj.created_at)

    def get_replies(self, obj):
        # Slice first 3 matching native template parameters
        initial_batch = obj.get_all_replies()[:settings.NEWS_INITIAL_REPLIES]
        return NewsReplySerializer(initial_batch, many=True).data

    def get_total_replies_count(self, obj):
        return len(obj.get_all_replies())


class NewsDetailSerializer(serializers.ModelSerializer):
    """Complete structural node compiling article state and context."""
    friendly_date = serializers.SerializerMethodField()
    category = CategorySerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    tags = serializers.SerializerMethodField()
    article_content = serializers.SerializerMethodField()

    comments = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'title', 'slug', 'category', 'thumbnail', 
            'image_caption', 'content', 'article_content', 'author', 'friendly_date', 
            'tags', 'is_sponsored', 'sponsor_name', 'is_featured', 'comments', 'total_comments'
        ]

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def get_friendly_date(self, obj):
        return format_hybrid_time(obj.date_published)

    def get_article_content(self, obj):
        from ads.utils import insert_dynamic_ads
        return insert_dynamic_ads(obj.content)

    def get_comments(self, obj):
        """Fetches only top-level root comments for this article node."""
        # Adjust filtering parameters if your comment model uses a different field name like 'news_post'
        root_comments = obj.comments.filter(parent__isnull=True).order_by('-created_at')[:settings.NEWS_INITIAL_COMMENTS]
        return NewsCommentSerializer(root_comments, many=True).data

    def get_total_comments(self, obj):
        return obj.comments.filter(
            parent__isnull=True,
            is_approved=True
        ).count()