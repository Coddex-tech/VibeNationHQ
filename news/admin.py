import json
from django.contrib import admin
from django import forms
from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import format_html, escape
from django.urls import reverse
from django.utils.safestring import mark_safe
from vibenation.status_condition import get_status_badge

# Models
from .models import News, Category, NewsComment

# Unfold & Third Party
from unfold.admin import ModelAdmin
# Standard filters used to prevent E115 System Check errors
from django_ckeditor_5.widgets import CKEditor5Widget
from vibenation.admin_site import admin_site, staff_admin_site

@admin.register(LogEntry)
class LogEntryAdmin(ModelAdmin):
    date_hierarchy = 'action_time'
    list_filter_submit = True 
    
    # Restored to standard strings to bypass E115 error
    list_filter = [
        'user',
        'content_type',
        'action_flag', 
    ]    
    
    search_fields = ['object_repr', 'change_message']
    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag_',
        'nice_change_message'
    ]

    def has_delete_permission(self, request, obj=None): return True
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_module_permission(self, request): return request.user.is_superuser
    def has_view_permission(self, request, obj=None): return request.user.is_superuser

    def nice_change_message(self, obj):
        if obj.action_flag == 3: return "Item Deleted"
        if not obj.change_message: return "No changes made"
        try:
            change_data = json.loads(obj.change_message)
            messages = []
            for item in change_data:
                if 'added' in item: return "Initial creation"
                if 'changed' in item:
                    fields = item['changed'].get('fields', [])
                    messages.append(f"Edited: {', '.join(fields)}")
            return " | ".join(messages)
        except:
            return obj.change_message
    nice_change_message.short_description = "What was changed"

    def action_flag_(self, obj):
        flags = {1: "Added", 2: "Changed", 3: "Deleted"}
        return flags.get(obj.action_flag)

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            return obj.object_repr
        try:
            ct = obj.content_type
            url = reverse(f'admin:{ct.app_label}_{ct.model}_change', args=[obj.object_id])
            return mark_safe(f'<a href="{url}" class="text-primary-600 font-semibold underline">{escape(obj.object_repr)}</a>')
        except:
            return obj.object_repr
    object_link.short_description = "Object"

class NewsAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget(config_name='default'))
    class Meta:
        model = News
        fields = '__all__'

class NewsAdmin(ModelAdmin):
    form = NewsAdminForm
    list_display = ('go_to_live', 'title', 'get_categories', 'date_published', 'views', 'author', 'thumbnail_preview')
    list_display_links = ('title',)
    search_fields = ('title', 'category__name', 'author')
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
        return ('views',) if not request.user.is_superuser else ()

    class Media:
        js = ('js/site_admin.js',)

class CategoryAdmin(ModelAdmin):
    list_display = ('name',)
    def get_readonly_fields(self, request, obj=None):
        return ('name', 'slug') if not request.user.is_superuser else ()

class NewsCommentAdmin(ModelAdmin):
    list_display = ('name', 'news', 'parent', 'content', 'created_at', 'status_badge')
    list_filter_submit = True
    list_filter = ('news', 'created_at')

    def status_badge(self, obj):
        return get_status_badge(obj.is_approved, true_label="Approved", false_label="Pending")
    

all_portals = [admin.site, admin_site, staff_admin_site]
registrations = [(News, NewsAdmin), (Category, CategoryAdmin), (NewsComment, NewsCommentAdmin)]

for portal in all_portals:
    for model, admin_class in registrations:
        try:
            portal.register(model, admin_class)
        except admin.sites.AlreadyRegistered:
            pass