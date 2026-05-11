import random
import qrcode
import base64
from io import BytesIO
from django.contrib import admin
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum
from news.models import News, NewsComment
from music.models import Song, DJ, MusicComment
from ads.models import Advertisement
from django.utils.timezone import now, timedelta
from django.utils import timezone
from datetime import timedelta

# Standard Admins
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin

# Unfold Mixin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.sites import UnfoldAdminSite
from django_otp.admin import OTPAdminSite

# Security
from django.contrib.admin.models import LogEntry
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice
from security.otp import verify_backup_code

def dashboard_stats_callback(request, context):
    """
    Gathers data for the Boss Portal Dashboard.
    """
    if not request.user.is_superuser:
        return context

    total_news = News.objects.count()
    total_songs = Song.objects.count()
    total_uploads = total_news + total_songs
    total_ads = Advertisement.objects.count()
    total_comments = MusicComment.objects.count() + NewsComment.objects.count()
    total_pending_comments = (
        MusicComment.objects.filter(is_approved=False).count() 
        + NewsComment.objects.filter(is_approved=False).count()
    )

    # DATA CHART ANALYTICS
    today = now().date()

    labels = []
    comment_data = []
    upload_data = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)

        music_comments = MusicComment.objects.filter(created_at__date=day).count()
        news_comments = NewsComment.objects.filter(created_at__date=day).count()

        total_comments_day = music_comments + news_comments

        songs = Song.objects.filter(release_date__date=day).count()
        news = News.objects.filter(date_published__date=day).count()
        djs = DJ.objects.filter(created_at__date=day).count()

        total_uploads_day = songs + news + djs

        labels.append(day.strftime("%a"))  # Mon, Tue, etc.
        comment_data.append(total_comments_day)
        upload_data.append(total_uploads_day)

    context.update({
        "dashboard_stats": [
            {
            "title": "News Room",
            "metric": total_news,
            "footer": "Published news articles",
            "icon": "article",
            },
            {
                "title": "Music Catalog",
                "metric": total_songs,
                "footer": "Total Songs Uploaded",
                "icon": "music_note",
            },
            {
            "title": "Total Comment",
            "metric": total_comments,
            "footer": "Total comments",
            "icon": "comment",
            },
            {
                "title": "Moderation Queue",
                "metric": total_pending_comments, # Replace with pending_comments variable
                "footer": "Comments awaiting approval",
                "icon": "rule",
                "color": "danger" if 12 > 0 else "success", # Dynamic coloring!
            },
            # {
            #     "title": "Portal Security",
            #     "metric": "Active",
            #     "footer": "OTP Protection Enabled",
            #     "icon": "verified_user",
            #     "color": "success",
            # },
            {
            "title": "Ad System",
            "metric": total_ads,
            "footer": "Running advertisements",
            "icon": "campaign",
            },
        ],

        "chart_data": {
            "labels": labels,

            "datasets": [
                {
                    "label": "Total Comments",
                    "data": comment_data,
                },
                {
                    "label": "Uploads",
                    "data": upload_data,
                }
            ]
        }
    })

    return context

# --- CUSTOM USER/GROUP ADMINS ---
class MyUserAdmin(BaseUserAdmin, UnfoldModelAdmin):
    filter_horizontal = ("groups", "user_permissions")
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'password' in form.base_fields:
            form.base_fields['password'].help_text = mark_safe(
                'Raw passwords are not stored. '
                'Change using <a href="../password/" '
                'style="color: #44b8e5; font-weight: bold; text-decoration: underline;">this form</a>.'
            )
        return form

class MyGroupAdmin(BaseGroupAdmin, UnfoldModelAdmin):
    filter_horizontal = ("permissions",)

class MasterAdminSite(UnfoldAdminSite):
    site_header = "VibeNationHQ Boss Portal"
    site_title = "Master Portal"
    login_template = "admin/login.html"
    enable_nav_sidebar = True

    def each_context(self, request):
        context = super().each_context(request)
        context["site_header"] = self.site_header
        context["site_title"] = self.site_title
        return context

    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def login(self, request, extra_context=None):
        response = super().login(request, extra_context)
        if request.method == "POST":
            user = request.user
            if user.is_authenticated:
                if not user.is_superuser:
                    logout(request)
                    messages.error(request, "ACCESS DENIED: Boss Portal Only.")
                    return redirect("/vibenation-admin-1999/login/")
                return redirect("/vibenation-admin-1999/")
        return response


class StaffAdminSite(UnfoldAdminSite):
    site_header = "VibeNationHQ Staff Portal"
    site_title = "Staff Portal"
    enable_nav_sidebar = True
    login_template= "admin/login.html"

    def each_context(self, request):
        context = super().each_context(request)
        context["site_header"] = self.site_header
        context["site_title"] = self.site_title
        return context
    
    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff and not request.user.is_superuser

    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff and not request.user.is_superuser

    def login(self, request, extra_context=None):
        response = super().login(request, extra_context)
        if request.method == "POST":
            user = request.user
            if user.is_authenticated:
                if user.is_superuser:
                    logout(request)
                    messages.warning(request, "Boss! Please use the Master Portal.")
                    return redirect("/vibe-crew-login-2026/login/")
                return redirect("/vibe-crew-login-2026/")
        return response

# TOTP Devices with QR Code
class TOTPDeviceAdmin(UnfoldModelAdmin):

    list_display = (
        "user",
        "name",
        "confirmed",
        "last_used_at",
    )

    search_fields = (
        "user__username",
        "name",
    )

    list_filter = (
        "confirmed",
    )

    readonly_fields = (
        "display_qr_code",
    )

    fieldsets = (
        ("Device Information", {
            "fields": (
                "user",
                "name",
                "confirmed",
            )
        }),

        ("Authenticator QR Code", {
            "fields": (
                "display_qr_code",
            )
        }),
    )

    def display_qr_code(self, obj):

        if obj.pk:
            img = qrcode.make(obj.config_url)

            buffer = BytesIO()
            img.save(buffer, format="PNG")

            img_str = base64.b64encode(
                buffer.getvalue()
            ).decode()

            return mark_safe(
                f'''
                <div style="
                    padding:20px;
                    background:#121A2D;
                    border-radius:16px;
                    display:inline-block;
                ">
                    <img
                        src="data:image/png;base64,{img_str}"
                        width="200"
                        height="200"
                        style="border-radius:12px;"
                    />
                </div>
                '''
            )

        return "Save first."

class StaticDeviceAdmin(UnfoldModelAdmin):

    list_display = (
        "user",
        "name",
        "confirmed",
        "last_used_at",
    )

    search_fields = (
        "user__username",
        "name",
    )

    list_filter = (
        "confirmed",
    )

# Initialize Sites
admin_site = MasterAdminSite(name='boss_admin')
staff_admin_site = StaffAdminSite(name='staff_admin')


# --- REGISTRATION HELPER ---
def safe_register(sites, model, admin_class=None):

    if not isinstance(sites, list):
        sites = [sites]

    for site in sites:
        try:
            if site.is_registered(model):
                site.unregister(model)

            if admin_class:
                site.register(model, admin_class)
            else:
                site.register(model)

        except Exception:
            pass


# --- APPLY REGISTRATIONS ---

all_sites = [admin_site, staff_admin_site]

# AUTH MODELS
safe_register(all_sites, User, MyUserAdmin)
safe_register(all_sites, Group, MyGroupAdmin)
safe_register(all_sites, LogEntry)

# OTP MODELS (IMPORTANT: MUST BE IN BOTH SITES)
safe_register(all_sites, StaticDevice, StaticDeviceAdmin)
safe_register(all_sites, TOTPDevice, TOTPDeviceAdmin)