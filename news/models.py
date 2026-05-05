from django.db import models
from django.utils.text import slugify
from sortedm2m.fields import SortedManyToManyField
from taggit_autosuggest.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field
from music.compress_image import handle_webp_compression
from django.utils import timezone
from django.urls import reverse

class NewsManager(models.Manager):
    def public(self):
        """
        Returns only news that is marked as published AND 
        whose publication date has already arrived.
        """
        return self.filter(
            is_published=True, 
            date_published__lte=timezone.now()
        )
    
    def sponsored(self):
        """
        Database-level version of your check.
        Filters for: Is Sponsored AND (Hasn't Expired OR Has no Expiry date).
        """
        now = timezone.now()
        return self.public().filter(
            models.Q(is_sponsored=True) & 
            (models.Q(expires_at__gt=now) | models.Q(expires_at__isnull=True))
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
    slug = models.SlugField(unique=True, blank=True)
    category = SortedManyToManyField(Category, related_name='news')
    thumbnail = models.ImageField(upload_to='news_thumbnails/', blank=True, null=True)
    image_caption = models.CharField(max_length=255, blank=True)
    is_sponsored = models.BooleanField(default=False)
    sponsor_name = models.CharField(max_length=100, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True)
    content = CKEditor5Field('Content', config_name='default') # CKEditor
    author = models.CharField(max_length=100, default='VibeNation')
    date_published = models.DateTimeField(default=timezone.now, help_text="Set a future date to schedule this post.")
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
        if self.is_sponsored and self.expires_at:
            return timezone.now() < self.expires_at
        return self.is_sponsored

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


class NewsComment(models.Model):
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    name = models.CharField(max_length=100)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    def get_all_replies(self):
        """
        Returns ALL replies flattened under the top comment.
        This is required for one-level visual nesting.
        """
        all_replies = []

        def collect(comment):
            for reply in comment.replies.all():
                all_replies.append(reply)
                collect(reply)

        collect(self)
        return sorted(all_replies, key=lambda r: r.created_at)

    @property
    def replying_to(self):
        return self.parent.name if self.parent else None

    def __str__(self):
        return self.content[:30]
