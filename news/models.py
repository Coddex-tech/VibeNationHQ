from django.conf import settings
from django.db import models
from vibenation.models_base import BaseComment # Clean core import
from django.utils.text import slugify
from sortedm2m.fields import SortedManyToManyField
from taggit_autosuggest.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field
from music.compress_image import handle_webp_compression
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse

class IpBlock(models.Model):
    ip_address = models.GenericIPAddressField(db_index=True, unique=True)
    reason = models.CharField(max_length=255, blank=True)
    blocked_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.ip_address} (Expires: {self.expires_at})"

    class Meta:
        verbose_name = "IpBlock"
        verbose_name_plural = "Blocked IP Address"

class NewsManager(models.Manager):
    def public(self):
        return self.filter(
            is_published=True, 
            date_published__lte=timezone.now()
        )
    
    def sponsored(self):
        """
        Strictly pulls active sponsored items
        """
        now = timezone.now()
        return self.public().filter(
            models.Q(is_sponsored=True) & 
            (models.Q(expires_at__gt=now) | models.Q(expires_at__isnull=True))
        )

    def regular_news(self):
        """
        🔥 HIGH PERFORMANCE READ: Pulls standard news AND any expired 
        sponsored posts together seamlessly. Zero database stress.
        """
        now = timezone.now()
        return self.public().filter(
            models.Q(is_sponsored=False) | 
            (models.Q(is_sponsored=True) & models.Q(expires_at__lte=now))
        )

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=120, unique=True, editable=True, null=True, blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class News(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    category = SortedManyToManyField(Category, related_name='news')
    thumbnail = models.ImageField(upload_to='news_thumbnails/', blank=True, null=True)
    image_caption = models.CharField(max_length=255, blank=True)
    is_sponsored = models.BooleanField(default=False)
    sponsor_name = models.CharField(max_length=100, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True, help_text="Set an expiry date for this sponsored post.")
    is_featured = models.BooleanField(default=False)
    content = CKEditor5Field('Content', config_name='default') # CKEditor
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    date_published = models.DateTimeField(default=timezone.now, help_text="You can set a future date to schedule this post.")
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    tags = TaggableManager()
    is_published = models.BooleanField(default=True)

    # CONNECT THE MANAGER
    objects = NewsManager() 

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_published']
        verbose_name = "News"
        verbose_name_plural = "News"

    def get_absolute_url(self):
        return reverse('news:news_details', kwargs={'slug': self.slug})

    # SPONSORED POST EXPIRING
    def is_currently_sponsored(self):
        """Checks if the post is sponsored and hasn't expired yet."""
        if self.is_sponsored:
            # If it has an expiration date and we've crossed it, it's no longer active!
            if self.expires_at and timezone.now() >= self.expires_at:
                return False
            return True
        return False

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if self.thumbnail:
            is_new_image = False
            
            if not self.pk:
                is_new_image = True
            else:
                try:
                    old_instance = News.objects.get(pk=self.pk)
                    if old_instance.thumbnail.name != self.thumbnail.name:
                        is_new_image = True
                except News.DoesNotExist:
                    is_new_image = True

            if is_new_image or not str(self.thumbnail.name).lower().endswith('.webp'):
                compressed_file = handle_webp_compression(self.thumbnail, self.title)
                if compressed_file:
                    self.thumbnail = compressed_file

        super().save(*args, **kwargs)



class NewsView(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='views_log')
    created_at = models.DateTimeField(auto_now_add=True)


class NewsComment(BaseComment):
    # Keep only the custom model relationships unique to the News ecosystem
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name='comments'
    )
