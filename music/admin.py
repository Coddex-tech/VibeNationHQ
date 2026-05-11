from django.contrib import admin
from django.utils.html import format_html
from .models import Artist, Song, DJ, Category, Album, MusicComment
from unfold.admin import ModelAdmin
from vibenation.admin_site import admin_site, staff_admin_site
from vibenation.status_condition import get_status_badge
from django.utils.safestring import mark_safe

class ArtistAdmin(ModelAdmin):
    list_display = ('name', 'created_at', 'song_count')
    search_fields = ('name',)
    ordering = ('-created_at',)

    def song_count(self, obj):
        return obj.songs.count()
    song_count.short_description = "Songs"

class SongAdmin(ModelAdmin):
    list_display = ('title', 'get_artists', 'views', 'release_date', 'display_category', 'download_status', 'cover_preview')
    
    list_display_links = ('title',)
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ('artists',)
    search_fields = ('title', 'artists__name', 'album__title')
    list_filter_submit = True
    list_filter = ('category', 'genre', 'release_date')

    @admin.display(description="Artists")
    def get_artists(self, obj):
        # The 'if obj.pk' check is vital for SortedManyToManyField in Unfold
        if obj.pk:
            return ", ".join([artist.name for artist in obj.artists.all()])
        return "-"

    @admin.display(description="Category", ordering="category")
    def display_category(self, obj):
        return obj.category.name if obj.category else "-"

    @admin.display(description="Cover")
    def cover_preview(self, obj):
        if not obj.cover_image:
            return mark_safe('<span style="color:#6b7280; font-size:11px; font-style:italic;">No Cover</span>')
            
        try:
            image_url = obj.cover_image.url
            return mark_safe(f'''
                <img src="{image_url}" 
                     style="width:64px; height:64px; border-radius:8px; object-fit:cover; 
                            border: 2px solid rgba(255,255,255,0.1); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);" />
            ''')
        except Exception:
            return mark_safe('<span style="color:#ef4444; font-size:11px;">Link Error</span>')

    @admin.display(description="Download Status", ordering="download")
    def download_status(self, obj):        
        count = f"{obj.download:,}" 
        
        if obj.download > 0:
            return mark_safe(f'''
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="background-color:rgba(34,197,94,0.1); color:#22c55e; 
                                 padding:4px 10px; border-radius:6px; font-size:11px; 
                                 font-weight:700; border:1px solid rgba(34,197,94,0.2); 
                                 letter-spacing: 0.5px;">FILE</span>
                    <span style="color: #ffffff; font-size: 12px; font-weight: 500;">{count}</span>
                </div>
            ''')
            
        return mark_safe(f'''
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="background-color:rgba(255,255,255,0.05); color:#9ca3af; 
                             padding:4px 10px; border-radius:6px; font-size:11px; 
                             font-weight:700; border:1px solid rgba(255,255,255,0.1); 
                             letter-spacing: 0.5px;">EMPTY</span>
                <span style="color: #6b7280; font-size: 12px;">{count}</span>
            </div>
        ''')

# Apply similar logic to DJAdmin to keep it safe
class DJAdmin(ModelAdmin):
    list_display = ('dj_name', 'get_artists', 'created_at', 'dj_cover_preview')
    list_display_links = ('dj_name',)
    prepopulated_fields = {"slug": ("dj_name",)}
    filter_horizontal = ('artists',)
    
    @admin.display(description="Artists")
    def get_artists(self, obj):
        if obj.pk:
            return ", ".join([artist.name for artist in obj.artists.all()])
        return "-"

    @admin.display(description="Cover")
    def dj_cover_preview(self, obj):
        if obj.dj_cover:
            return format_html('<img src="{}" class="w-10 h-10 rounded-md object-cover border border-white/10" />', obj.dj_cover.url)
        return "-"

class AlbumAdmin(ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('title', 'artist', 'release_date')
    search_fields = ('title', 'artist__name')

class MusicCommentAdmin(ModelAdmin):
    list_display = ('name', 'song', 'parent', 'created_at', 'status_badge')
    list_filter_submit = True
    list_filter = ('is_approved', 'created_at')
    search_fields = ('name', 'content', 'song__title')

    def status_badge(self, obj):
        return get_status_badge(obj.is_approved, true_label="Approved", false_label="Pending")

    status_badge.short_description = "Approval Status"

    # This makes the column name look nice in the table header
    status_badge.short_description = "Status"
    
all_portals = [admin.site, admin_site, staff_admin_site]
registrations = [
    (Artist, ArtistAdmin), 
    (Song, SongAdmin), 
    (DJ, DJAdmin),
    (Category, ModelAdmin), 
    (Album, ModelAdmin), 
    (MusicComment, MusicCommentAdmin)
]

for portal in all_portals:
    for model, admin_class in registrations:
        try:
            if portal.is_registered(model):
                portal.unregister(model)
            portal.register(model, admin_class)
        except:
            pass