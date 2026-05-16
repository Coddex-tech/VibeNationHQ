from unfold.admin import ModelAdmin as UnfoldModelAdmin
from django.contrib import admin
from .models import AdZone, Advertisement
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter
from vibenation.status_condition import get_status_badge

# Import your custom portals
from vibenation.admin_site import admin_site, staff_admin_site
from vibenation.status_condition import get_status_badge

class AdZoneAdmin(UnfoldModelAdmin):
    list_display = ("name",)

class AdvertisementAdmin(UnfoldModelAdmin):
    list_display = ("title", "zone", "status_badge", "clicks", "impressions")
    search_fields = ("title", "client_name", "zone__name")
    list_filter = (
        ('zone', RelatedDropdownFilter), 
        ('is_active', DropdownFilter)
    )

    def status_badge(self, obj):
        return get_status_badge(obj.is_active)

    # ------ ACTION COMMANDS --------
    actions = ['approve', 'pending']

    @admin.action(description="🚀 Approve selected Advert")
    def approve(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Selected adverts are now approved on VibeNation.")

    @admin.action(description="📁 Move to draft")
    def pending(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Selected adverts have been hidden.")

    fieldsets = (
        ("General Info", {
            "fields": ("title", "zone", "client_name"),
        }),
        ("Content (Choose One)", {
            "fields": ("image", "link_url", "video", "html_code"),
            "description": "Provide either an image/link, a video, or custom HTML code.",
        }),
    )

all_portals = [admin.site, admin_site, staff_admin_site]

for portal in all_portals:
    try:
        portal.register(AdZone, AdZoneAdmin)
        portal.register(Advertisement, AdvertisementAdmin)
    except admin.sites.AlreadyRegistered:
        pass