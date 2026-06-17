from rest_framework import serializers
from django.contrib.auth import get_user_model
from utils.date_time_extra import format_hybrid_time
from .models import News, Category

User = get_user_model()

class AuthorSerializer(serializers.ModelSerializer):
    """Minimal user serializer to keep payloads tight."""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class CategorySerializer(serializers.ModelSerializer):
    """Maps name and slug properties for clean frontend label rendering."""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class NewsSerializer(serializers.ModelSerializer):
    friendly_date = serializers.SerializerMethodField()
    category = CategorySerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    
    # 2. FIXED: Changed to SerializerMethodField so it calls your get_tags function
    tags = serializers.SerializerMethodField()
    
    is_active_sponsor = serializers.BooleanField(source='is_currently_sponsored', read_only=True)
    absolute_url = serializers.CharField(source='get_absolute_url', read_only=True)
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'title', 'slug', 'absolute_url', 'category', 'thumbnail_url', 
            'image_caption', 'content', 'author', 'friendly_date', 'views', 'tags',
            'is_sponsored', 'sponsor_name', 'is_active_sponsor', 'is_featured'
        ]

    def get_tags(self, obj):
        """Manually flattens the django-taggit manager into a clean array of strings."""
        return [tag.name for tag in obj.tags.all()]

    def get_thumbnail_url(self, obj):
        """Ensures absolute image target resolution regardless of environment."""
        if obj.thumbnail:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None

    def get_friendly_date(self, obj):
        return format_hybrid_time(obj.date_published)