from django.utils import timezone
from datetime import timedelta
from django.utils.timesince import timesince

def format_hybrid_time(date_obj):
    if not date_obj:
        return ""
        
    now = timezone.now()
    diff = now - date_obj

    if diff < timedelta(minutes=1):
        return "Just now"
    elif diff < timedelta(hours=24):
        # returns "1 hour" or "45 minutes" etc.
        first_chunk = timesince(date_obj).split(',')[0]
        return f"{first_chunk} ago"
    else:
        # Ordinal suffix calculator
        day = date_obj.day
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
            
        return f"{day}{suffix}, {date_obj.strftime('%B %Y')}"