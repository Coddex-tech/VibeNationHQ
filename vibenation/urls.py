"""
URL configuration for vibenation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import HttpResponseNotFound
from django.contrib.sitemaps.views import sitemap

from music.sitemaps import SongSitemap
from news.sitemaps import NewsSitemap
from vibenation.sitemaps import StaticViewSitemap

from music import views
from .admin_site import admin_site, staff_admin_site

def fake_admin(request):
    return HttpResponseNotFound("Page not found")

sitemaps = {
    'songs': SongSitemap,
    'news': NewsSitemap,
    'static': StaticViewSitemap(),
}

urlpatterns = [
    path('admin/', fake_admin),
    # BOSS PORTAL - We name this 'boss'
    path('vibenation-admin-1999/', admin_site.urls),

    # STAFF PORTAL - We name this 'staff'
    path('vibe-crew-login-2026/', staff_admin_site.urls),

    path('', include(('news.urls', 'news'), namespace='news')),
    path('music/', include(('music.urls', 'music'), namespace='music')),
    path('ads/', include('ads.urls')),
    
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('taggit_autosuggest/', include('taggit_autosuggest.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),

    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("privacy/", views.privacy, name="privacy"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),
    path("service/", views.service, name="service"),
    path("dmca/", views.dmca, name="dmca"),
    path("promote/", views.promote, name="promote"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

urlpatterns += [
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt",
            content_type="text/plain"
        ),
    ),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)