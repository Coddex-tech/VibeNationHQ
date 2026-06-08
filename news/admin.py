from unfold.admin import ModelAdmin as UnfoldModelAdmin
from django.contrib import admin
from django import forms
from django.utils.html import format_html, escape
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe
from vibenation.status_condition import get_status_badge
import json
# Models
from .models import News, Category, NewsComment, IpBlock
# Standard filters used to prevent E115 System Check errors
from django_ckeditor_5.widgets import CKEditor5Widget
from vibenation.admin_site import admin_site, staff_admin_site

class NewsAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget(config_name='default'))
    class Meta:
        model = News
        fields = '__all__'

class NewsAdmin(UnfoldModelAdmin):
    form = NewsAdminForm
    list_display = ('go_to_live', 'title', 'get_categories', 'date_published', 'views', 'get_author_name', 'thumbnail_preview')
    list_display_links = ('title',)
    search_fields = ('title', 'category__name', 'author__username', 'author__first_name')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('category',)
    date_hierarchy = 'date_published'
    list_filter_submit = True
    list_filter = ('category', 'date_published', 'author')

    def go_to_live(self, obj):
        url = obj.get_absolute_url()
        return format_html(
            '<a href="{}" target="_blank" class='
            '"bg-primary-600 text-white px-3 py-1 rounded-full text-xs font-bold hover:bg-primary-700 transition-colors">'
            'VIEW</a>', url
        )
    go_to_live.short_description = 'Live'

    def get_categories(self, obj):
        return ", ".join([cat.name for cat in obj.category.all()])
    get_categories.short_description = 'Categories'

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" class="w-12 h-12 rounded-md object-cover border border-gray-200" />', obj.thumbnail.url)
        return "-"
    thumbnail_preview.short_description = 'Image'

    def get_readonly_fields(self, request, obj=None):
        return ('views', 'is_sponsored', 'sponsor_name', 'expires_at') if not request.user.is_superuser else ()
    # To disable author
    def get_readonly_fields(self, request, obj=None):
        return ('author', 'views')

    def save_model(self, request, obj, form, change):
        # If the article is new (no author yet), set the current logged-in user
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description='Author')
    def get_author_name(self, obj):
        # Pulls the full name if available, otherwise the username
        if obj.author:
            return obj.author.get_full_name() or obj.author.username
        return "Unknown"

    # ------- ACTION COMMANDS ---------
    actions = ['make_published', 'make_draft', 'set_as_featured']

    def get_actions(self, request):
        actions = super().get_actions(request)
        # This ONLY removes the delete option for staff
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    @admin.action(description="🚀 Publish selected articles")
    def make_published(self, request, queryset):
        queryset.update(is_published=True)
        self.message_user(request, "Selected articles are now live on VibeNation.")

    @admin.action(description="📁 Move to Drafts")
    def make_draft(self, request, queryset):
        queryset.update(is_published=False)
        self.message_user(request, "Selected articles have been hidden.")

    @admin.action(description="🌟 Set as Featured")
    def set_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, "Articles moved to Featured section.")

    # ============== FOR DYNAMIC NEWS AND SPONSORED POST =================
    def changelist_view(self, request, extra_context=None):
        """
        Runs quietly in the background only when staff views the admin list.
        Permanently turns off expired campaigns at the database layer.
        """
        now = timezone.now()
        expired_count = News.objects.filter(is_sponsored=True, expires_at__lte=now).update(is_sponsored=False)
        
        if expired_count > 0:
            self.message_user(request, f"🧹 System Cleaned: {expired_count} expired campaign(s) converted to regular news columns.")
            
        return super().changelist_view(request, extra_context=extra_context)

    

    fieldsets = (
        ("Main Content", {
            "fields": ("title", "slug", "author", "category", "tags", "content"),
        }),
        ("Media & SEO", {
            "fields": ("thumbnail", "image_caption"),
        }),
        ("Status & Visibility", {
            "fields": ("is_featured", "date_published", "views", "is_published"),
        }),
        ("Sponsorship Details", {
            "classes": ("tab-sponsored",),
            "fields": ("is_sponsored", "sponsor_name", "expires_at"),
        }),
    )

    class Media:
        js = ("js/admin_custom_style.js",)
        css = {
            "all": ("css/admin_custom_style.css",)
        }

class CategoryAdmin(UnfoldModelAdmin):
    list_display = ('name',)
    def get_readonly_fields(self, request, obj=None):
        return ('name', 'slug') if not request.user.is_superuser else ()

class NewsCommentAdmin(UnfoldModelAdmin):
    list_display = ('author_identity', 'news', 'parent', 'content', 'created_at', 'status_badge', 'is_approved')
    list_filter_submit = True
    list_filter = ('news', 'created_at')
    # list_display_links = ('title',)
    ordering = ('-created_at',)
    list_editable = ('is_approved',)

    def get_readonly_fields(self, request, obj=None):
        return ('news', 'user', 'name', 'content', 'parent') if not request.user.is_superuser else ()

    def author_identity(self, obj):
        """
        Dynamically builds a premium display handle inside your Unfold dashboard grid table view.
        """
        if obj.is_verified_staff:
            return f"🛡️ {obj.display_name} (Staff)"
        return obj.display_name or "Anonymous Fan"
    author_identity.short_description = "Commenter"

    def status_badge(self, obj):
        return get_status_badge(obj.is_approved, true_label="Approved", false_label="Pending")

    # ------- ACTION COMMANDS ---------

    actions = ['approve', 'pending']

    def get_actions(self, request):
        actions = super().get_actions(request)
        # This ONLY removes the delete option for staff
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    @admin.action(description="🚀 Approve selected comments")
    def approve(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected comments are now approved on VibeNation.")

    @admin.action(description="📁 Move selected comments to draft")
    def pending(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, "Selected comments have been hidden.")

class IpAdmin(UnfoldModelAdmin):
    list_display = ('ip_address', 'blocked_at', 'expires_at', 'reason')
    list_filter_submit = True
    ordering = ('-blocked_at',)
    

all_portals = [admin.site, admin_site, staff_admin_site]
registrations = [(News, NewsAdmin), (Category, CategoryAdmin), (NewsComment, NewsCommentAdmin), (IpBlock, IpAdmin)]

for portal in all_portals:
    for model, admin_class in registrations:
        try:
            portal.register(model, admin_class)
        except admin.sites.AlreadyRegistered:
            pass