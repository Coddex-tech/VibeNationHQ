from django.db import models
from music.compress_image import handle_webp_compression
from django.utils.text import slugify

class AdZone(models.Model):
    """Defines WHERE the ad goes (e.g., 'Sidebar', 'Header', 'Post Middle')"""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Advertisement(models.Model):
    zone = models.ForeignKey(AdZone, on_delete=models.CASCADE, related_name="ads", null=True, blank=False)
    title = models.CharField(max_length=200, null=True, blank=False)
    
    # For Direct Deals
    image = models.ImageField(upload_to='ads/', blank=True, null=True)
    link_url = models.URLField(blank=True, null=True)
    video = models.FileField(upload_to="ads/", blank=True, null=True)
    client_name = models.CharField(max_length=100, null=True, blank=True)
    
    # For Google AdSense or script-based ads
    html_code = models.TextField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    clicks = models.PositiveIntegerField(default=0)
    impressions = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"{self.title} ({self.zone.name if self.zone else 'No Zone'})"
    
    def save(self, *args, **kwargs):
        if self.image:
            is_new_image = False
            
            if not self.pk:
                # Brand new Ad
                is_new_image = True
            else:
                try:
                    # Make sure to use the correct class name: Advertisement
                    old_ad = Advertisement.objects.get(pk=self.pk)
                    if old_ad.image and old_ad.image.name != self.image.name:
                        is_new_image = True
                except Advertisement.DoesNotExist:
                    is_new_image = True

            # Compress if it's new OR if it's not webp yet
            if is_new_image or not str(self.image.name).lower().endswith('.webp'):
                # Use slugify(self.title) instead of self.id to avoid "None" filenames
                new_filename = slugify(self.title) if self.title else "ad-image"
                compressed_file = handle_webp_compression(self.image, new_filename)
                if compressed_file:
                    self.image = compressed_file

        super().save(*args, **kwargs)