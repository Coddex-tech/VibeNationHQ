import base64
import json
from io import BytesIO

import qrcode

from django.contrib import admin, messages
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.auth import logout
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from django_otp.admin import OTPAdminSite
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice

from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.sites import UnfoldAdminSite

from ads.models import Advertisement
from news.models import News

from music.models import (
    Album,
    AlbumFavorite,
    AlbumRating,
    AlbumTrack,
    Artist,
    ArtistFollow,
    CommunityPost,
    CommunityPostComment,
    CommunityPostCommentLike,
    CommunityPostCommentReport,
    CommunityPostLike,
    CommunityPostReport,
    CommunityPostTarget,
    EditorialArticle,
    EditorialArticleLike,
    EditorialArticleReport,
    EditorialComment,
    EditorialCommentLike,
    EditorialCommentReport,
    Genre,
    Song,
    SongFavorite,
    SongRating,
    UserFollow,
)

# Import the EXISTING Music ModelAdmin classes.
# We reuse them instead of creating duplicate admin definitions.
from music.admin import (
    AlbumAdmin,
    AlbumFavoriteAdmin,
    AlbumRatingAdmin,
    AlbumTrackAdmin,
    ArtistAdmin,
    ArtistFollowAdmin,
    CommunityPostAdmin,
    CommunityPostCommentAdmin,
    CommunityPostCommentLikeAdmin,
    CommunityPostCommentReportAdmin,
    CommunityPostLikeAdmin,
    CommunityPostReportAdmin,
    EditorialArticleAdmin,
    EditorialArticleLikeAdmin,
    EditorialArticleReportAdmin,
    EditorialCommentAdmin,
    EditorialCommentLikeAdmin,
    EditorialCommentReportAdmin,
    GenreAdmin,
    SongAdmin,
    SongFavoriteAdmin,
    SongRatingAdmin,
    UserFollowAdmin,
)


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

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

    # FIX:
    # Previously this was `.count` without parentheses,
    # which returned the method itself instead of the number.
    total_sponsored = News.objects.filter(
        is_sponsored=True
    ).count()

    # --------------------------------------------------------
    # FUTURE COMMENT ANALYTICS
    # --------------------------------------------------------
    # These remain intentionally empty until the final
    # NewsComment / comment moderation architecture is wired.
    #
    # total_comments = ...
    # total_pending_comments = ...

    today = now().date()

    labels = []
    comment_data = []
    upload_data = []

    # --------------------------------------------------------
    # FUTURE 7-DAY ANALYTICS
    # --------------------------------------------------------
    # Keep this structure ready for when you want actual
    # dashboard analytics.
    #
    # for i in range(6, -1, -1):
    #     day = today - timedelta(days=i)
    #
    #     music_comments = MusicComment.objects.filter(
    #         created_at__date=day
    #     ).count()
    #
    #     news_comments = NewsComment.objects.filter(
    #         created_at__date=day
    #     ).count()
    #
    #     total_comments_day = music_comments + news_comments
    #
    #     songs = Song.objects.filter(
    #         published_at__date=day
    #     ).count()
    #
    #     news = News.objects.filter(
    #         date_published__date=day
    #     ).count()
    #
    #     total_uploads_day = songs + news
    #
    #     labels.append(day.strftime("%a"))
    #     comment_data.append(total_comments_day)
    #     upload_data.append(total_uploads_day)

    context.update(
        {
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
                    # "metric": total_comments,
                    "footer": "Total comments",
                    "icon": "comment",
                },
                {
                    "title": "Moderation Queue",
                    # "metric": total_pending_comments,
                    "footer": "Comments awaiting approval",
                    "icon": "rule",
                    "color": "danger" if 12 > 0 else "success",
                },
                {
                    "title": "Ad System",
                    "metric": total_ads,
                    "footer": "Running advertisements",
                    "icon": "campaign",
                },
                {
                    "title": "Active Sponsored Post",
                    "metric": total_sponsored,
                    "footer": "Running Sponsored Content",
                    "icon": "post",
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
                    },
                ],
            },
        }
    )

    return context


# ============================================================
# CUSTOM USER / GROUP ADMINS
# ============================================================

class MyUserAdmin(BaseUserAdmin, UnfoldModelAdmin):
    """
    Custom User admin shared by the Boss and Staff portals.
    """

    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(
            request,
            obj,
            **kwargs,
        )

        if "password" in form.base_fields:
            form.base_fields["password"].help_text = mark_safe(
                'Raw passwords are not stored. '
                'Change using <a href="../password/" '
                'style="color: #44b8e5; font-weight: bold; '
                'text-decoration: underline;">this form</a>.'
            )

        return form


class MyGroupAdmin(BaseGroupAdmin, UnfoldModelAdmin):
    """
    Custom Group admin shared by the Boss and Staff portals.
    """

    filter_horizontal = (
        "permissions",
    )


# ============================================================
# MASTER / BOSS ADMIN SITE
# ============================================================

class MasterAdminSite(UnfoldAdminSite):
    """
    VibeNationHQ Master/Boss administration portal.

    Accessible only by active superusers.
    """

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
        urls = super().get_urls()

        # Keeping this method allows future custom Boss Portal
        # URLs to be added cleanly.
        return urls

    def has_permission(self, request):
        return (
            request.user.is_active
            and request.user.is_superuser
        )

    def login(self, request, extra_context=None):
        response = super().login(
            request,
            extra_context,
        )

        if request.method == "POST":
            user = request.user

            if user.is_authenticated:

                if not user.is_superuser:
                    logout(request)

                    messages.error(
                        request,
                        "ACCESS DENIED: Boss Portal Only. "
                        "Kindly use the staff page.",
                    )

                    return redirect(
                        "/vibenation-admin-1999/login/"
                    )

                return redirect(
                    "/vibenation-admin-1999/"
                )

        return response


# ============================================================
# STAFF ADMIN SITE
# ============================================================

class StaffAdminSite(UnfoldAdminSite):
    """
    VibeNationHQ Staff administration portal.

    Accessible by active staff users who are NOT superusers.
    """

    site_header = "VibeNationHQ Staff Portal"
    site_title = "Staff Portal"
    enable_nav_sidebar = True
    login_template = "admin/login.html"

    def each_context(self, request):
        context = super().each_context(request)

        context["site_header"] = self.site_header
        context["site_title"] = self.site_title

        return context

    def has_permission(self, request):
        return (
            request.user.is_active
            and request.user.is_staff
            and not request.user.is_superuser
        )

    def login(self, request, extra_context=None):
        response = super().login(
            request,
            extra_context,
        )

        if request.method == "POST":
            user = request.user

            if user.is_authenticated:

                if user.is_superuser:
                    logout(request)

                    messages.warning(
                        request,
                        "Boss! Please use the Master Portal.",
                    )

                    return redirect(
                        "/vibe-crew-login-2026/login/"
                    )

                return redirect(
                    "/vibe-crew-login-2026/"
                )

        return response


# ============================================================
# LOG ENTRY ADMIN
# ============================================================

class LogEntryAdmin(UnfoldModelAdmin):
    """
    System audit log.

    The same admin class is registered on:
        - default Django admin
        - Boss Portal
        - Staff Portal

    The object link dynamically uses the current admin site's
    namespace so Boss links stay inside boss_admin and Staff
    links stay inside staff_admin.
    """

    date_hierarchy = "action_time"

    list_filter_submit = True

    list_select_related = [
        "user",
        "content_type",
    ]

    list_filter = [
        "user",
        "content_type",
        "action_flag",
    ]

    search_fields = [
        "object_repr",
        "change_message",
    ]

    list_display = [
        "content_type",
        "user",
        "action_time",
        "object_link",
        "action_flag_styled",
        "nice_change_message",
    ]

    # --------------------------------------------------------
    # PERMISSIONS
    # --------------------------------------------------------

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    # --------------------------------------------------------
    # ACTION TYPE BADGE
    # --------------------------------------------------------

    @admin.display(description="Type")
    def action_flag_styled(self, obj):
        """
        Creates a styled badge for the action type.
        """

        if obj.action_flag == 1:
            return format_html(
                '<span class="bg-green-600 text-white '
                'px-2 py-0.5 rounded-md text-[10px] '
                'font-bold uppercase">{}</span>',
                "Add",
            )

        if obj.action_flag == 2:
            return format_html(
                '<span class="bg-blue-600 text-white '
                'px-2 py-0.5 rounded-md text-[10px] '
                'font-bold uppercase">{}</span>',
                "Mod",
            )

        if obj.action_flag == 3:
            return format_html(
                '<span class="bg-red-600 text-white '
                'px-2 py-0.5 rounded-md text-[10px] '
                'font-bold uppercase">{}</span>',
                "Del",
            )

        return format_html(
            '<span class="bg-gray-600 text-white '
            'px-2 py-0.5 rounded-md text-[10px] '
            'font-bold uppercase">{}</span>',
            "???",
        )

    # --------------------------------------------------------
    # OBJECT LINK
    # --------------------------------------------------------

    @admin.display(description="Item")
    def object_link(self, obj):
        """
        Creates a link to the object affected by the log.

        IMPORTANT:
        Uses self.admin_site.name instead of the hard-coded
        "admin:" namespace.

        Therefore:

            Boss Portal -> boss_admin:...
            Staff Portal -> staff_admin:...
            Default Admin -> admin:...
        """

        if obj.action_flag == DELETION:
            return obj.object_repr

        try:
            ct = obj.content_type

            app_label = ct.app_label
            model_name = ct.model

            # This is the important fix.
            namespace = self.admin_site.name

            url = reverse(
                f"{namespace}:{app_label}_{model_name}_change",
                args=[obj.object_id],
            )

            return format_html(
                '<a href="{}" '
                'class="font-bold text-primary-600 '
                'hover:text-primary-700">{}</a>',
                url,
                escape(obj.object_repr),
            )

        except Exception:
            return obj.object_repr

    # --------------------------------------------------------
    # SILENT LOG DELETION
    # --------------------------------------------------------

    def log_deletion(
        self,
        request,
        object,
        object_repr,
    ):
        """
        Prevents deletion of LogEntry rows from creating
        another "Deleted LogEntry" row.
        """
        return None

    def log_addition(
        self,
        request,
        object,
        message,
    ):
        return None

    def log_change(
        self,
        request,
        object,
        message,
    ):
        return None

    # --------------------------------------------------------
    # ACTION COMMANDS
    # --------------------------------------------------------

    actions = [
        "clear_all_logs",
        "silent_delete_selected",
    ]

    @admin.action(
        description="☢️ Emergency: Clear ALL System Logs"
    )
    def clear_all_logs(
        self,
        request,
        queryset,
    ):
        if not request.user.is_superuser:
            return

        LogEntry.objects.all().delete()

        self.message_user(
            request,
            "System logs have been completely purged.",
        )

    @admin.action(
        description="🗑️ Delete selected logs (Silent)"
    )
    def silent_delete_selected(
        self,
        request,
        queryset,
    ):
        rows_deleted = queryset.delete()

        self.message_user(
            request,
            f"Successfully purged "
            f"{rows_deleted[0]} log entries.",
        )

    # --------------------------------------------------------
    # REMOVE DEFAULT DELETE ACTION
    # --------------------------------------------------------

    def get_actions(self, request):
        actions = super().get_actions(request)

        if "delete_selected" in actions:
            del actions["delete_selected"]

        return actions

    # --------------------------------------------------------
    # CHANGE MESSAGE DISPLAY
    # --------------------------------------------------------

    @admin.display(description="Change Log")
    def nice_change_message(self, obj):
        """
        Converts Django's raw JSON change message into
        something readable in the admin.
        """

        if obj.action_flag == DELETION:
            return mark_safe(
                '<span class="text-red-500 font-semibold">'
                "Purged from database"
                "</span>"
            )

        if not obj.change_message:
            return mark_safe(
                '<span class="opacity-50 italic '
                'text-slate-500">'
                "Direct edit (No metadata)"
                "</span>"
            )

        try:
            change_data = json.loads(
                obj.change_message
            )

            messages_list = []

            for item in change_data:

                # Addition
                if "added" in item:
                    return mark_safe(
                        '<span class="text-green-500 '
                        'font-medium">'
                        "Initial Entry"
                        "</span>"
                    )

                # Modification
                if "changed" in item:
                    fields = item["changed"].get(
                        "fields",
                        [],
                    )

                    clean_fields = [
                        field.replace(
                            "_",
                            " ",
                        ).title()
                        for field in fields
                    ]

                    if clean_fields:
                        messages_list.append(
                            "Updated: "
                            + ", ".join(clean_fields)
                        )

                # Deletion
                if "deleted" in item:
                    messages_list.append(
                        "Deleted: "
                        + item["deleted"].get(
                            "name",
                            "item",
                        )
                    )

            if not messages_list:
                return "Modified"

            joined_message = " | ".join(
                messages_list
            )

            return format_html(
                '<span class="text-xs font-medium '
                'text-slate-300">{}</span>',
                joined_message,
            )

        except Exception:
            raw_message = (
                obj.change_message
                .replace("[", "")
                .replace("]", "")
                .replace("{", "")
                .replace("}", "")
                .replace('"', "")
                .replace(
                    "changed: fields:",
                    "Updated: ",
                )
            )

            return format_html(
                '<span class="text-xs text-slate-400">'
                '{}</span>',
                raw_message,
            )


# ============================================================
# TOTP DEVICE ADMIN
# ============================================================

class TOTPDeviceAdmin(UnfoldModelAdmin):
    """
    TOTP authenticator device administration.

    Displays the QR code needed to connect an authenticator app.
    """

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
        (
            "Device Information",
            {
                "fields": (
                    "user",
                    "name",
                    "confirmed",
                )
            },
        ),
        (
            "Authenticator QR Code",
            {
                "fields": (
                    "display_qr_code",
                )
            },
        ),
    )

    @admin.display(
        description="Authenticator QR Code"
    )
    def display_qr_code(self, obj):
        """
        Generates a QR code from the TOTP configuration URL.
        """

        if obj.pk:

            img = qrcode.make(
                obj.config_url
            )

            buffer = BytesIO()

            img.save(
                buffer,
                format="PNG",
            )

            img_str = base64.b64encode(
                buffer.getvalue()
            ).decode()

            return mark_safe(
                f"""
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
                        alt="TOTP QR Code"
                    />
                </div>
                """
            )

        return "Save first."


# ============================================================
# STATIC DEVICE ADMIN
# ============================================================

class StaticDeviceAdmin(UnfoldModelAdmin):
    """
    Static OTP backup-code device administration.
    """

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


# ============================================================
# INITIALIZE CUSTOM ADMIN SITES
# ============================================================

admin_site = MasterAdminSite(
    name="boss_admin"
)

staff_admin_site = StaffAdminSite(
    name="staff_admin"
)


# ============================================================
# REGISTRATION HELPER
# ============================================================

def safe_register(
    sites,
    model,
    admin_class=None,
):
    """
    Safely registers a model with one or multiple admin sites.

    If the model is already registered, it is first unregistered
    so the desired ModelAdmin class can be applied cleanly.
    """

    if not isinstance(sites, (list, tuple)):
        sites = [sites]

    for site in sites:

        try:
            if site.is_registered(model):
                site.unregister(model)

            if admin_class is not None:
                site.register(
                    model,
                    admin_class,
                )
            else:
                site.register(model)

        except Exception as exc:
            # Registration should not silently destroy the
            # entire admin startup.
            #
            # We deliberately don't re-raise here because this
            # helper is intended to safely handle duplicate
            # registrations.
            #
            # You can inspect Django's system checks if a real
            # registration problem occurs.
            continue


# ============================================================
# CORE AUTH REGISTRATION
# ============================================================

all_sites = [
    admin_site,
    staff_admin_site,
]

all_portals = [
    admin.site,
    admin_site,
    staff_admin_site,
]

safe_register(
    all_sites,
    User,
    MyUserAdmin,
)

safe_register(
    all_sites,
    Group,
    MyGroupAdmin,
)


# ============================================================
# OTP / SECURITY REGISTRATION
# ============================================================

safe_register(
    all_sites,
    StaticDevice,
    StaticDeviceAdmin,
)

safe_register(
    all_sites,
    TOTPDevice,
    TOTPDeviceAdmin,
)


# ============================================================
# MUSIC ADMIN REGISTRATION
# ============================================================
#
# THIS IS THE IMPORTANT PART.
#
# music.admin.py uses @admin.register(...), which registers
# models on Django's DEFAULT admin.site.
#
# Your Boss Portal is NOT the default admin site.
#
# Therefore the music models must explicitly be registered
# on boss_admin and staff_admin.
#
# We reuse the exact ModelAdmin classes already defined in
# music/admin.py.
# ============================================================

music_admins = [
    # --------------------------------------------------------
    # MUSIC CATALOG
    # --------------------------------------------------------

    (Genre, GenreAdmin),
    (Artist, ArtistAdmin),
    (Album, AlbumAdmin),
    (AlbumTrack, AlbumTrackAdmin),
    (Song, SongAdmin),

    # --------------------------------------------------------
    # RATINGS
    # --------------------------------------------------------

    (SongRating, SongRatingAdmin),
    (AlbumRating, AlbumRatingAdmin),

    # --------------------------------------------------------
    # EDITORIAL
    # --------------------------------------------------------

    (
        EditorialArticle,
        EditorialArticleAdmin,
    ),

    (
        EditorialArticleLike,
        EditorialArticleLikeAdmin,
    ),

    (
        EditorialComment,
        EditorialCommentAdmin,
    ),

    (
        EditorialCommentLike,
        EditorialCommentLikeAdmin,
    ),

    # --------------------------------------------------------
    # COMMUNITY
    # --------------------------------------------------------

    (
        CommunityPost,
        CommunityPostAdmin,
    ),

    (
        CommunityPostLike,
        CommunityPostLikeAdmin,
    ),

    (
        CommunityPostComment,
        CommunityPostCommentAdmin,
    ),

    (
        CommunityPostCommentLike,
        CommunityPostCommentLikeAdmin,
    ),

    # --------------------------------------------------------
    # FAVORITES / FOLLOWING / SOCIAL
    # --------------------------------------------------------

    (
        SongFavorite,
        SongFavoriteAdmin,
    ),

    (
        AlbumFavorite,
        AlbumFavoriteAdmin,
    ),

    (
        ArtistFollow,
        ArtistFollowAdmin,
    ),

    (
        UserFollow,
        UserFollowAdmin,
    ),

    # --------------------------------------------------------
    # MODERATION / REPORTS
    # --------------------------------------------------------

    (
        EditorialArticleReport,
        EditorialArticleReportAdmin,
    ),

    (
        EditorialCommentReport,
        EditorialCommentReportAdmin,
    ),

    (
        CommunityPostReport,
        CommunityPostReportAdmin,
    ),

    (
        CommunityPostCommentReport,
        CommunityPostCommentReportAdmin,
    ),
]


# Register every music model on both custom portals.
#
# NOTE:
# CommunityPostTarget is intentionally NOT registered as a
# standalone admin model because it is a OneToOne inline under
# CommunityPostAdmin.
for model, admin_class in music_admins:
    safe_register(
        all_sites,
        model,
        admin_class,
    )


# ============================================================
# LOG ENTRY REGISTRATION
# ============================================================
#
# LogEntry is registered last so that our custom LogEntryAdmin
# replaces any existing registration on every portal.
# ============================================================

for portal in all_portals:

    try:
        portal.unregister(LogEntry)

    except admin.sites.NotRegistered:
        pass

    portal.register(
        LogEntry,
        LogEntryAdmin,
    )