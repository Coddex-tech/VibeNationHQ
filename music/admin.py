from unfold.admin import ModelAdmin as UnfoldModelAdmin
from django.contrib import admin
from django.utils.html import format_html
from .models import Artist, Song, DJ, Genre, Album, MusicComment
from unfold.admin import ModelAdmin
from vibenation.admin_site import admin_site, staff_admin_site
from vibenation.status_condition import get_status_badge
from django.utils.safestring import mark_safe


class ArtistAdmin(UnfoldModelAdmin):
    list_display = ('name', 'created_at', 'song_count')
    search_fields = ('name',)
    ordering = ('-created_at',)

    def song_count(self, obj):
        return obj.songs.count()
    song_count.short_description = "Songs"

class SongAdmin(UnfoldModelAdmin):
    list_display = ('title', 'get_artists', 'views', 'release_date', 'get_genres', 'download_status', 'cover_preview')
    
    list_display_links = ('title',)
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ('artists', 'genres')
    search_fields = ('title', 'artists__name', 'album__title')
    list_filter_submit = True
    list_filter = ('category', 'genres', 'release_date')

    @admin.display(description="Artists")
    def get_artists(self, obj):
        # The 'if obj.pk' check is vital for SortedManyToManyField in Unfold
        if obj.pk:
            return ", ".join([artist.name for artist in obj.artists.all()])
        return "-"

    @admin.display(description="Genres")
    def get_genres(self, obj):
        if obj.pk:
            return ", ".join([genres.name for genres in obj.genres.all()])
        return "-"

    @admin.display(description="Category", ordering="category")
    def display_category(self, obj):
        return obj.category.name if obj.category else "-"

    def get_actions(self, request):
        actions = super().get_actions(request)
        # This ONLY removes the delete option for staff
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    @admin.display(description="Cover")
    def cover_preview(self, obj):
        if obj.original_cover:
            img_url = obj.original_cover.url
        elif obj.cover_image:
            img_url = obj.cover_image.url
        else:
            # 3. Final Fallback: Styled text badge
            return format_html(
                '<span class="flex items-center justify-center w-12 h-12 rounded bg-gray-100 text-gray-400 text-[10px] font-bold uppercase border border-gray-200">No Cover</span>'
            )

        # Render the image preview if found
        return format_html(
            '<img src="{}" class="w-12 h-12 object-cover rounded border border-gray-200 shadow-sm" alt="Cover" />',
            img_url
        )

    cover_preview.short_description = "Preview"

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
class DJAdmin(UnfoldModelAdmin):
    list_display = ('dj_name', 'get_artists', 'created_at', 'dj_cover_preview')
    list_display_links = ('dj_name',)
    prepopulated_fields = {"slug": ("dj_name",)}
    filter_horizontal = ('artists',)
    
    @admin.display(description="Artists")
    def get_artists(self, obj):
        if obj.pk:
            return ", ".join([artist.name for artist in obj.artists.all()])
        return "-"

    def get_actions(self, request):
        actions = super().get_actions(request)
        # This ONLY removes the delete option for staff
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    @admin.display(description="Cover")
    def dj_cover_preview(self, obj):
        if obj.dj_cover:
            return format_html('<img src="{}" class="w-10 h-10 rounded-md object-cover border border-white/10" />', obj.dj_cover.url)
        return "-"

class AlbumAdmin(UnfoldModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('title', 'artist', 'release_date')
    search_fields = ('title', 'artist__name')

    def get_actions(self, request):
        actions = super().get_actions(request)
        # This ONLY removes the delete option for staff
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

class MusicCommentAdmin(UnfoldModelAdmin):
    list_display = ('author_identity', 'song__title', 'parent', 'content', 'created_at', 'status_badge', 'is_approved')
    list_display_links = ('author_identity',)
    list_filter_submit = True
    list_filter = ('is_approved', 'created_at')
    search_fields = ('name', 'content', 'song__title')
    ordering = ('-created_at',)
    # Allows quick checking/unchecking right from the table grid row
    list_editable = ('is_approved',)

    def get_readonly_fields(self, request, obj=None):
        return ('song', 'dj', 'user', 'parent', 'name', 'content') if not request.user.is_superuser else ()

    def author_identity(self, obj):
        if obj.is_verified_staff:
            return f"🛡️ {obj.display_name} (Staff)"
        return obj.display_name or "Anonymous Fan"
    author_identity.short_description = "Commenter"

    def status_badge(self, obj):
        return get_status_badge(obj.is_approved, true_label="Approved", false_label="Pending")
    status_badge.short_description = "Status"

    # ------ ACTION COMMANDS --------
    actions = ['approve', 'pending']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    @admin.action(description="🚀 Approve selected comments")
    def approve(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected comments are now approved on VibeNation.")

    @admin.action(description="📁 Pend selected comments")
    def pending(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, "Selected comments have been hidden.")
    
all_portals = [admin.site, admin_site, staff_admin_site]
registrations = [
    (Artist, ArtistAdmin), 
    (Song, SongAdmin), 
    (DJ, DJAdmin),
    (Genre, ModelAdmin), 
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