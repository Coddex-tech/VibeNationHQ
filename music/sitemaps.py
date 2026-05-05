# music/sitemaps.py
from django.contrib.sitemaps import Sitemap
from .models import Song
from django.urls import reverse

class SongSitemap(Sitemap):
    changefreq = "daily" # How often content changes
    priority = 0.9 # SEO importance (0.0 - 1.0)

    def items(self):
        return Song.objects.all()

    def location(self, obj):
        return f"/music/{obj.slug}/"
    
    def lastmod(self, obj):
        return obj.updated_at

