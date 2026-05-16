from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from ads.models import Advertisement
import random

def insert_dynamic_ads(content):
    if not content:
        return ""

    # Split content by paragraph tags and filter out empty strings
    paragraphs = [p for p in content.split("</p>") if p.strip()]
    total_paragraphs = len(paragraphs)
    new_content = ""
    
    # Get all active in-article ads
    active_ads = list(Advertisement.objects.filter(zone__name="In-Article", is_active=True))
    
    for i, paragraph in enumerate(paragraphs):
        # Always add the paragraph text back with its closing tag
        new_content += paragraph + "</p>"
        
        is_ad_spot = (i == 1) or (i > 1 and (i - 1) % 4 == 0)

        if is_ad_spot and (i < total_paragraphs - 1):
            
            if active_ads:
                # Pick a random direct ad
                ad = random.choice(active_ads)
                
                # Increment impression count silently
                ad.impressions += 1
                ad.save(update_fields=['impressions'])
                
                # Render direct ad
                ad_html = render_to_string('ads/render_ads.html', {'ad': ad, 'zone_name': 'In-Article'})
                wrapped_ad = f'<div class="article-ad" style="margin: 20px 0;">{ad_html}</div>'
                new_content += wrapped_ad
            else:
                # If no direct ads, fallback to AdSense/Default
                ad_html = render_to_string('ads/render_ads.html', {'ad': None, 'zone_name': 'In-Article'})
                wrapped_ad = f'<div class="article-ad" style="margin: 20px 0;">{ad_html}</div>'
                new_content += wrapped_ad

    return mark_safe(new_content)