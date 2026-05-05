from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ['about', 'privacy', 'contact', 'disclaimer', 'service', 'dmca', 'promote']

    def location(self, item):
        return reverse(item)
