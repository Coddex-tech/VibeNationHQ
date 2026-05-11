import os
from .utils import clean_mp3_tags
from django.db import models
from django.utils.text import slugify
from taggit_autosuggest.managers import TaggableManager
from sortedm2m.fields import SortedManyToManyField
# for default cover
from mutagen.mp3 import MP3
from django.core.files.base import ContentFile
from PIL import Image
import io
from .compress_image import handle_webp_compression

class Artist(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=140, unique=True)  # You will enter manually in admin
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)  # Enter manually in admin

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Song(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    cover_image = models.ImageField(upload_to="covers/", blank=True, null=True)
    original_cover = models.ImageField(upload_to="temp_covers/", blank=True, null=True)
    group = models.CharField(max_length=50, blank=True, null=True, default='Music')
    release_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    download = models.PositiveBigIntegerField(default=0)
    audio_file = models.FileField(upload_to="songs/")
    artists = SortedManyToManyField('Artist', related_name="songs")
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name="songs")
    tags = TaggableManager()
    album = models.ForeignKey('Album', on_delete=models.CASCADE, related_name='songs', null=True, blank=True)
    views = models.PositiveBigIntegerField(default=0)
    rating_total = models.PositiveIntegerField(default=0)
    rating_count = models.PositiveIntegerField(default=0)
    duration = models.CharField(max_length=10, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Duration
        if self.audio_file and not self.duration:
            try:
                from mutagen.mp3 import MP3
                audio = MP3(self.audio_file)
                total_seconds = int(audio.info.length)
                self.duration = f"{total_seconds // 60}:{total_seconds % 60:02d}"
            except: 
                self.duration = ""

        # Compression to .webp
        if self.cover_image and not self.cover_image.name.lower().endswith('.webp'):
            self.cover_image = handle_webp_compression(self.cover_image, self.title)
        
        if self.original_cover and not self.original_cover.name.lower().endswith('.webp'):
            self.original_cover = handle_webp_compression(self.original_cover, f"{self.title}_original")

        super().save(*args, **kwargs)

        # ID3 & Tag Cleaning
        if not getattr(self, '_processing', False):
            self._processing = True
            
            # Only extract from MP3 if both image fields are empty
            if self.audio_file and not self.cover_image and not self.original_cover:
                try:
                    from mutagen.mp3 import MP3
                    from mutagen.id3 import ID3, APIC
                    audio = MP3(self.audio_file.path, ID3=ID3)
                    for tag in audio.tags.values():
                        if isinstance(tag, APIC):
                            from django.core.files.base import ContentFile
                            # Extract and compress immediately
                            self.original_cover = handle_webp_compression(ContentFile(tag.data), f"{self.title}_extracted")
                            break
                except: 
                    pass

            # TAG CLEANING
            logo_path = os.path.join('media', 'logo', 'VibeNation_cover.png')
            if self.audio_file and os.path.exists(logo_path):
                artist_list = ", ".join([a.name for a in self.artists.all()])
                clean_mp3_tags(self.audio_file.path, self.title, artist_list, logo_path)

            # Final save to commit the extracted cover
            super().save(update_fields=["original_cover"])
            del self._processing
    
class DJ(models.Model):
    dj_name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True) # Changed to blank=True for auto-gen
    genre = models.CharField(max_length=100, blank=True, null=True, default="Mixtape")
    artists = SortedManyToManyField('Artist', related_name='mixtapes')
    dj_file = models.FileField(upload_to="mixtapes/")
    group = models.CharField(max_length=10, default="Mixtape")
    dj_cover = models.ImageField(upload_to="djs/")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="djs")
    duration = models.CharField(max_length=10, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.dj_name)

        # WebP Compression (Only for dj_cover)
        if self.dj_cover and not self.dj_cover.name.lower().endswith('.webp'):
            self.dj_cover = handle_webp_compression(self.dj_cover, self.dj_name)

        # Calculate Duration
        if self.dj_file and not self.duration:
            try:
                from mutagen.mp3 import MP3
                audio = MP3(self.dj_file.path) 
                total_seconds = int(audio.info.length)
                
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60

                if hours > 0:
                    self.duration = f"{hours}:{minutes:02d}:{seconds:02d}"
                else:
                    self.duration = f"{minutes}:{seconds:02d}"
            except Exception as e:
                print(f"Error extracting duration: {e}")
                self.duration = "0:00"

        super().save(*args, **kwargs)
    
    
class SongView(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_views')
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ('song', 'ip_address')

    def __str__(self):
        return f"{self.song.title} viewed on {self.timestamp}"

    
class MusicComment(models.Model):
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True
    )

    dj = models.ForeignKey(
        DJ, 
        on_delete=models.CASCADE,
        related_name='comments', 
        null=True, 
        blank=True
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
        """Returns all replies flattened under this comment, preserving actual parents."""
        all_replies = []

        def collect(comment):
            for reply in comment.replies.all().order_by('created_at'):
                all_replies.append(reply)
                collect(reply)

        collect(self)
        return all_replies

    @property
    def replying_to(self):
        return self.parent.name if self.parent else None

    def __str__(self):
        return self.content[:30]

    

class Album(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    group = models.CharField(max_length=6, default="Album")
    cover = models.ImageField(upload_to='album_covers/')
    release_date = models.DateField()
    artist = models.ForeignKey(Artist, on_delete=models.PROTECT, null=True, blank=True, related_name='albums')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        
        return self.title