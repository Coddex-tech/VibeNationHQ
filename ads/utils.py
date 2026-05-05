from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from ads.models import Advertisement
import random

def insert_dynamic_ads(content):
    if not content:
        return ""

    # Split content by paragraph tags
    paragraphs = content.split("</p>")
    new_content = ""
    
    # Get all active in-article ads
    active_ads = list(Advertisement.objects.filter(zone__name="In-Article", is_active=True))
    
    for i, paragraph in enumerate(paragraphs):
        # Always add the paragraph text back
        if paragraph.strip():
            new_content += paragraph + "</p>"
        
        # Inject ads after the 2nd and 5th
        if i in [1, 4]: 
            if active_ads:
                # Pick a random ad
                ad = random.choice(active_ads)
                
                # Increment impression count
                ad.impressions += 1
                ad.save(update_fields=['impressions'])
                
                # Render using your template
                ad_html = render_to_string('ads/render_ads.html', {'ad': ad, 'zone_name': 'In-Article'})
                wrapped_ad = f'<div class="article-ad">{ad_html}</div>'
                new_content += wrapped_ad
            else:
                # If no direct ads, render google ads
                ad_html = render_to_string('ads/render_ads.html', {'ad': None, 'zone_name': 'In-Article'})
                new_content += ad_html

    return mark_safe(new_content)