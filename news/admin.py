import json
from django.contrib import admin
from .models import News, Category, NewsComment
from django import forms
# for tracking activity
from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import format_html, escape
from django.urls import reverse
from django.utils.safestring import mark_safe

from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter
from django_ckeditor_5.widgets import CKEditor5Widget
from vibenation.admin_site import admin_site, staff_admin_site

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'
    
    list_filter = [
        ('user', RelatedDropdownFilter),
        ('content_type', RelatedDropdownFilter),
        ('action_flag', ChoiceDropdownFilter),
    ]    
    search_fields = ['object_repr', 'change_message',]
    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag_',
        'nice_change_message'
        ]
    
    # Delete logs
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' not in actions:
            actions['delete_selected'] = self.get_action('delete_selected')
        return actions

    # ONLY ONE of these, and it must be True
    def has_delete_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser
    
    # Disable adding and changing (keeps logs authentic)
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False

    def nice_change_message(self, obj):
        if obj.action_flag == 3: # Deletion
            return "Item Deleted"
        
        if not obj.change_message:
            return "No changes made"
            
        try:
            # Try to parse the Django JSON message
            change_data = json.loads(obj.change_message)
            messages = []
            
            for item in change_data:
                if 'added' in item:
                    return "Initial creation"
                if 'changed' in item:
                    fields = item['changed'].get('fields', [])
                    # Turn ['is_sponsored', 'sponsor_name'] into "is_sponsored, sponsor_name"
                    messages.append(f"Edited: {', '.join(fields)}")
            
            return " | ".join(messages)
        except:
            # Fallback if it's not JSON (older entries)
            return obj.change_message
            
    nice_change_message.short_description = "What was changed"

    def action_flag_(self, obj):
        flags = {1: "Added", 2: "Changed", 3: "Deleted"}
        return flags.get(obj.action_flag)

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            return obj.object_repr
        else:
            ct = obj.content_type
            try:
                url = reverse(f'admin:{ct.app_label}_{ct.model}_change', args=[obj.object_id])
                return mark_safe(f'<a href="{url}">{escape(obj.object_repr)}</a>')
            except:
                return obj.object_repr
    object_link.short_description = "Object"

# ------------------------------
# Custom form for CKEditor5
# ------------------------------
class StyledCKEditor5Widget(CKEditor5Widget):
    class Media:
        class_name = 'ckeditor-admin'
        css = {
            'all': ('css/ckeditor_content_admin.css',)
        }

class NewsAdminForm(forms.ModelForm):
    content = forms.CharField(widget=StyledCKEditor5Widget(config_name='default'))

    class Meta:
        model = News
        fields = '__all__'

class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    list_display = ('go_to_live', 'title', 'get_categories', 'date_published', 'views', 'author', 'thumbnail_preview')
    list_display_links = ('title',)
    search_fields = ('title', 'category__name', 'author')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('category',)
    date_hierarchy = 'date_published'  
    list_filter = (
        ('category', RelatedDropdownFilter), 
        ('date_published', DropdownFilter),
        ('author', DropdownFilter),
    )

    def go_to_live(self, obj):
        url = obj.get_absolute_url()
        return format_html(
            '<a href="{}" target="_blank" title="View on Site" style="'
            'display: inline-block; width: 30px; height: 30px; line-height: 30px;'
            'text-align: center; background-color: #008080; color: white;'
            'border-radius: 50%; text-decoration: none; font-size: 14px;'
            'transition: 0.3s; font-weight: bold;">&#128065;</a>',
            url
        )
    go_to_live.short_description = 'Live'

    actions = ['make_published', 'make_draft']
    @admin.action(description='Publish selected stories')
    def make_published(self, request, queryset):
        queryset.update(is_published=True)

    @admin.action(description='Move selected to Draft')
    def make_draft(self, request, queryset):
        queryset.update(is_published=False)

    def get_categories(self, obj):
        return ", ".join([cat.name for cat in obj.category.all()])
    get_categories.short_description = 'Categories'

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img loading="lazy" src="{}" style="width:60px; height:60px; border-radius:6px;" />',
                obj.thumbnail.url
            )
        return "-"
    thumbnail_preview.short_description = 'Image Preview'

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('views',) # Staff can see, but can't edit
        return ()

    class Media:
        js = ('js/site_admin.js',)
        css = {
            'all': ('css/admin_custom.css',)
        }

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('name', 'slug',)
        return ()

class NewsCommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'news', 'parent', 'content', 'created_at')
    search_fields = ('name', 'news__title', 'content')
    list_filter = (
        ('news', RelatedDropdownFilter),
        ('created_at', DropdownFilter),
    )
    def get_readonly_fields(self, request, obj=None):
        return ('news', 'parent', 'name', 'content',)


all_portals = [admin.site, admin_site, staff_admin_site]

registrations = [
    (News, NewsAdmin),
    (Category, CategoryAdmin),
    (NewsComment, NewsCommentAdmin),
]

for portal in all_portals:
    for model, admin_class in registrations:
        try:
            portal.register(model, admin_class)
        except admin.sites.AlreadyRegistered:
            pass