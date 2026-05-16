from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ['about', 'privacy', 'contact', 'service', 'dmca', 'advertise']

    def location(self, item):
        return reverse(item)
