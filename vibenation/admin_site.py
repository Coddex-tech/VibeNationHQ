import random
import qrcode
import base64
from io import BytesIO
from django.contrib import admin
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.utils.html import format_html, escape
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
from django.contrib.admin.models import LogEntry, DELETION
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice

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

class MasterAdminSite(UnfoldAdminSite, OTPAdminSite):
    site_header = "VibeNationHQ Boss Portal"
    site_title = "Master Portal"
    login_template = "admin/login.html"
    enable_nav_sidebar = True

    def each_context(self, request):
        context = super().each_context(request)
        context["site_header"] = self.site_header
        context["site_title"] = self.site_title
        return context

    def get_urls(self):
        from django.urls import path, include
        urls = super().get_urls()
        # This "injects" the standard auth URLs into your custom namespace
        # so that 'auth_user_changelist' becomes valid within the Boss Portal
        return urls

    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def login(self, request, extra_context=None):
        response = super().login(request, extra_context)
        if request.method == "POST":
            user = request.user
            if user.is_authenticated:
                if not user.is_superuser:
                    logout(request)
                    messages.error(request, "ACCESS DENIED: Boss Portal Only. Kindly use the staff page")
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

@admin.register(LogEntry)
class LogEntryAdmin(UnfoldModelAdmin):
    date_hierarchy = 'action_time'
    list_filter_submit = True 
    
    # Prevents N+1 database queries
    list_select_related = ["user", "content_type"]
    
    list_filter = ['user', 'content_type', 'action_flag']    
    search_fields = ['object_repr', 'change_message']
    
    list_display = [
        'content_type',
        'user',
        'action_time',
        'object_link',
        'action_flag_styled', 
        'nice_change_message'
    ]

    # Permission Overrides
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return request.user.is_superuser
    
    def action_flag_styled(self, obj):
        """Creates a colored badge for the action type"""
        if obj.action_flag == 1: # Added
            return format_html('<span class="bg-green-600 text-white px-2 py-0.5 rounded-md text-[10px] font-bold uppercase">{}</span>', "Add")
        
        if obj.action_flag == 2: # Changed
            return format_html('<span class="bg-blue-600 text-white px-2 py-0.5 rounded-md text-[10px] font-bold uppercase">{}</span>', "Mod")
        
        if obj.action_flag == 3: # Deleted
            return format_html('<span class="bg-red-600 text-white px-2 py-0.5 rounded-md text-[10px] font-bold uppercase">{}</span>', "Del")
            
        return format_html('<span class="bg-gray-600 text-white px-2 py-0.5 rounded-md text-[10px] font-bold uppercase">{}</span>', "???")
        
    action_flag_styled.short_description = "Type"

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            return obj.object_repr
        try:
            ct = obj.content_type
            # DYNAMIC NAMESPACE: This ensures the link stays in the portal the Boss is using
            app_label = ct.app_label
            model_name = ct.model
            
            # We try to reverse the URL based on the current admin namespace
            url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.object_id])
            return mark_safe(f'<a href="{url}" class="font-bold text-primary-600 hover:text-primary-700">{escape(obj.object_repr)}</a>')
        except Exception:
            return obj.object_repr
    object_link.short_description = "Item"

    def log_deletion(self, request, object, object_repr):
        """
        CRITICAL: This stops the loop. 
        When you delete logs, it will NOT create new 'Deleted LogEntry' rows.
        """
        return None

    # ----- ACTION COMMANDS -------
    actions = ['clear_all_logs', 'silent_delete_selected']

    @admin.action(description="☢️ Emergency: Clear ALL System Logs")
    def clear_all_logs(self, request, queryset):
        if not request.user.is_superuser:
            return
        # This deletes them without triggering individual signals
        LogEntry.objects.all().delete()
        self.message_user(request, "System logs have been completely purged.")

    @admin.action(description="🗑️ Delete selected logs (Silent)")
    def silent_delete_selected(self, request, queryset):
        rows_deleted = queryset.delete()
        self.message_user(request, f"Successfully purged {rows_deleted[0]} log entries.")

    # REMOVE the standard Django delete action
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # Keep these just in case of single-item deletes
    def log_deletion(self, request, object, object_repr):
        return None
    def log_addition(self, request, object, message):
        return None
    def log_change(self, request, object, message):
        return None

    def nice_change_message(self, obj):
        if obj.action_flag == 3: 
            return mark_safe('<span class="text-red-500 font-semibold">Purged from database</span>')
        
        if not obj.change_message: 
            return mark_safe('<span class="opacity-50 italic text-slate-500">Direct edit (No metadata)</span>')
        
        try:
            # Parse the JSON log data
            change_data = json.loads(obj.change_message)
            messages = []
            
            for item in change_data:
                # Check for Additions
                if 'added' in item:
                    return mark_safe('<span class="text-green-500 font-medium">Initial Entry</span>')
                
                # Check for Changes
                if 'changed' in item:
                    fields = item['changed'].get('fields', [])
                    clean_fields = [f.replace('_', ' ').title() for f in fields]
                    if clean_fields:
                        messages.append(f"Updated: {', '.join(clean_fields)}")
                
                if 'deleted' in item:
                    messages.append(f"Deleted: {item['deleted'].get('name', 'item')}")

            # If parsed but found no specific fields
            if not messages:
                return "Modified"

            joined_msg = " | ".join(messages)
            return mark_safe(f'<span class="text-xs font-medium text-slate-300">{joined_msg}</span>')
            
        except Exception:
            raw_msg = obj.change_message.replace('[', '').replace(']', '').replace('{', '').replace('}', '').replace('"', '').replace('changed: fields:', 'Updated: ')
            return mark_safe(f'<span class="text-xs text-slate-400">{raw_msg}</span>')

    nice_change_message.short_description = "Change Log"

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
all_portals = [admin.site, admin_site, staff_admin_site] # Include default admin

safe_register(all_sites, User, MyUserAdmin)
safe_register(all_sites, Group, MyGroupAdmin)

# --- REGISTER OTP & OTHER MODELS ---
safe_register(all_sites, StaticDevice, StaticDeviceAdmin)
safe_register(all_sites, TOTPDevice, TOTPDeviceAdmin)

# --- REGISTER LOGENTRY LAST ---
for portal in all_portals:
    try:
        portal.unregister(LogEntry)
    except admin.sites.NotRegistered:
        pass
    portal.register(LogEntry, LogEntryAdmin)