from django.contrib import admin
from django.utils.html import format_html
from .models import Artist, Song, DJ, Category, Album, MusicComment
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter
from vibenation.admin_site import admin_site, staff_admin_site

# ------------------------------
# ARTIST ADMIN
# ------------------------------
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'song_count')
    search_fields = ('name',)
    ordering = ('-created_at',)

    def song_count(self, obj):
        return obj.songs.count()
    song_count.short_description = "Number of Songs"

# ------------------------------
# SONG ADMIN
# ------------------------------
class SongAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'get_artists',
        'views',
        'release_date',
        'category',
        'download',
        'cover_preview',
    )
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ('artists',)
    search_fields = ('title', 'artists__name', 'album',)
    
    # We use Choice for genre (if CharField) and Related for Category (since it's a Model)
    list_filter = (
        ('genre', DropdownFilter), 
        ('category', RelatedDropdownFilter),
        ('release_date', DropdownFilter),
    )

    def get_artists(self, obj):
        return ", ".join([artist.name for artist in obj.artists.all()])
    get_artists.short_description = "Artists"

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img loading="lazy" src="{}" style="width:50px; height:50px; border-radius:5px;" />',
                obj.cover_image.url
            )
        return "No Cover"
    cover_preview.short_description = "Cover"

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }

# ------------------------------
# DJ ADMIN
# ------------------------------
class DJAdmin(admin.ModelAdmin):
    list_display = ('dj_name', 'get_artists', 'created_at', 'dj_cover')
    prepopulated_fields = {"slug": ("dj_name",)}
    filter_horizontal = ('artists',)
    search_fields = ('dj_name',)
    list_filter = (('created_at', DropdownFilter),)

    def get_artists(self, obj):
        return ", ".join([artist.name for artist in obj.artists.all()])
    get_artists.short_description = "Artists"

    def dj_cover(self, obj):
        if obj.dj_cover:
            return format_html(
                '<img loading="lazy" src="{}" style="width:50px; height:50px; border-radius:5px;" />',
                obj.dj_cover.url
            )
        return "No Cover"
    dj_cover.short_description = "Cover"

# ------------------------------
# OTHER ADMINS
# ------------------------------
class AlbumAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('title', 'artist', 'release_date')
    search_fields = ('title', 'artist__name')

class MusicCommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'song', 'parent', 'created_at', 'is_approved')
    list_filter = ('is_approved', ('created_at', DropdownFilter))
    search_fields = ('name', 'content', 'song__title')

# FINAL REGISTRATION
all_portals = [admin.site, admin_site, staff_admin_site]
registrations = [
    (Artist, ArtistAdmin),
    (Song, SongAdmin),
    (DJ, DJAdmin),
    (Category, None), 
    (Album, AlbumAdmin),
    (MusicComment, MusicCommentAdmin),
]

for portal in all_portals:
    for model, admin_class in registrations:
        try:
            if admin_class:
                portal.register(model, admin_class)
            else:
                portal.register(model)
        except admin.sites.AlreadyRegistered:
            # This prevents the crash if the model is already registered
            pass