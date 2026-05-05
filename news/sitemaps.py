# news/sitemaps.py
from django.contrib.sitemaps import Sitemap
from .models import News
from django.urls import reverse

class NewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return News.objects.all()

    def location(self, obj):
        return f"/news/{obj.slug}/"

    def lastmod(self, obj):
        return obj.updated_at
