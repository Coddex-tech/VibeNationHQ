from django import template
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import timedelta

register = template.Library()

def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1:'st', 2:'nd', 3:'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

@register.filter
def hybrid_time(date):
    """
    Returns relative time for <24 hours, full date after 24 hours with ordinal.
    Handles None or string values gracefully.
    """
    if not date:
        return ""  # skip if there's no date

    now = timezone.now()

    # Handle if cached data made date a string
    if isinstance(date, str):
        try:
            from django.utils.dateparse import parse_datetime
            date = parse_datetime(date)
            if date is None:
                return ""
        except Exception:
            return ""

    diff = now - date

    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=24):
        from django.utils.timesince import timesince
        return f"{timesince(date)} ago"
    else:
        return f"{ordinal(date.day)}, {date.strftime('%B %Y')}"
