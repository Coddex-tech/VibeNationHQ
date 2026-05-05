from django.contrib import admin
from .models import AdZone, Advertisement
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter
# Import your custom portals
from vibenation.admin_site import admin_site, staff_admin_site

class AdZoneAdmin(admin.ModelAdmin):
    list_display = ("name",)

class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ("title", "zone", "is_active", "clicks", "impressions")
    search_fields = ("title", "client_name", "zone__name")
    list_filter = (
        ('zone', RelatedDropdownFilter), 
        ('is_active', DropdownFilter)
    )

all_portals = [admin.site, admin_site, staff_admin_site]

for portal in all_portals:
    try:
        portal.register(AdZone, AdZoneAdmin)
        portal.register(Advertisement, AdvertisementAdmin)
    except admin.sites.AlreadyRegistered:
        pass