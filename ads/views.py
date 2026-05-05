from django.shortcuts import get_object_or_404, redirect
from .models import Advertisement

def ad_click_view(request, ad_id):
    ad = get_object_or_404(Advertisement, id=ad_id)
    ad.clicks += 1
    ad.save(update_fields=['clicks'])
    return redirect(ad.link_url if ad.link_url else '/')