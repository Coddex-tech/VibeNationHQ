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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseNotFound
from django_otp.admin import OTPAdminSite
from django.contrib.sitemaps.views import sitemap
from music import views
from music.sitemaps import SongSitemap
from news.sitemaps import NewsSitemap
from vibenation.sitemaps import StaticViewSitemap
from django.views.generic import TemplateView
from .admin_site import staff_admin_site
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from vibenation.admin_site import admin_site, staff_admin_site

# Fake admin to confuse bots
def fake_admin(request):
    return HttpResponseNotFound("Page not found")

# Auto-copy everything to the staff portal too
for model, model_admin in admin.site._registry.items():
    if not admin_site.is_registered(model):
        admin_site.register(model, type(model_admin))

# For staffs
for model, model_admin in admin.site._registry.items():
    if not staff_admin_site.is_registered(model):
        staff_admin_site.register(model, type(model_admin))

sitemaps = {
    'songs': SongSitemap,
    'news': NewsSitemap,
    'static': StaticViewSitemap(),
}

urlpatterns = [
    # Fake admin
    path('admin/', fake_admin),

    # 2FA-protected hidden admin
    path('vibenation-admin-1999/', include('admin_two_factor.urls')),
    path('vibenation-admin-1999/', admin_site.urls),

    path('vibe-crew-login-2026/', staff_admin_site.urls),

    #Apps
    path('', include(('news.urls', 'news'), namespace='news')),
    path('music/', include(('music.urls', 'music'), namespace='music')),
    
    path('ads/', include('ads.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('taggit_autosuggest/', include('taggit_autosuggest.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),

    # Global page URLS
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("privacy/", views.privacy, name="privacy"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),
    path("service/", views.service, name="service"),
    path("dmca/", views.dmca, name="dmca"),
    path("promote/", views.promote, name="promote"),
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