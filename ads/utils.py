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
    
    # BUMPED THRESHOLD: Require at least 750 characters of real text before allowing another ad
    characters_since_last_ad = 0
    ad_position = 0

    for i, paragraph in enumerate(paragraphs):
        new_content += paragraph + "</p>"
        
        # Strip internal HTML tags to count actual reading characters
        clean_text = paragraph.replace("<p>", "").strip()
        characters_since_last_ad += len(clean_text)
        
        is_not_the_absolute_last = i < (total_paragraphs - 1)
        
        # Check if we've met the higher reading distance requirement
        if is_not_the_absolute_last and characters_since_last_ad >= 750:
            ad_position += 1
            
            if active_ads:
                ad = random.choice(active_ads)
                ad.impressions += 1
                ad.save(update_fields=['impressions'])
                ad_html = render_to_string('ads/render_ads.html', {'ad': ad, 'zone_name': 'In-Article'})
            else:
                ad_html = render_to_string('ads/render_ads.html', {'ad': None, 'zone_name': 'In-Article'})
            
            # Styled wrapper with a clean, low-key "ADVERTISEMENT" label above the slot
            wrapped_ad = (
                f'<div class="article-ad" data-ad-num="{ad_position}" style="margin: 25px 0; text-align: center;">'
                f'{ad_html}'
                f'</div>'
            )
            new_content += wrapped_ad
            
            # RESET character counter right after injection
            characters_since_last_ad = 0

    return mark_safe(new_content)