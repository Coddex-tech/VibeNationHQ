from django import template
from ads.models import Advertisement

register = template.Library()

@register.inclusion_tag('ads/render_ads.html')
def show_ad(zone_name):
    # Get one random ad for the requested zone
    ad = Advertisement.objects.filter(zone__name=zone_name, is_active=True).order_by('?').first()
    
    # Increment impressions if ad exists
    if ad:
        ad.impressions += 1
        ad.save(update_fields=['impressions'])
        
    return {'ad': ad, 'zone_name': zone_name}