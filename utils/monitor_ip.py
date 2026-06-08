from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from news.models import IpBlock

def monitor_and_filter_ip(ip_address, action_type="comment"):
    """
    Tracks requests per IP. If an IP exceeds 5 actions in 1 minute,
    it triggers an automatic 24-hour network block.
    """
    # Define unique cache keys for tracking this IP's footprint
    count_key = f"rate:{action_type}:{ip_address}"
    cooldown_key = f"block_triggered:{ip_address}"

    # If already marked as triggered in cache, skip extra DB writes
    if cache.get(cooldown_key):
        return True

    # Increment the hit counter in memory/cache (defaults to 1 if it doesn't exist)
    try:
        current_hits = cache.get(count_key, 0) + 1
        cache.set(count_key, current_hits, timeout=60)  # 1-minute tracking window
    except Exception:
        return False

    # the threshold
    if current_hits > 5:
        # Prevent double writing to DB by locking their cache state for 24 hours
        cache.set(cooldown_key, True, timeout=86400)

        # Drop the concrete block straight into PostgreSQL
        IpBlock.objects.get_or_create(
            ip_address=ip_address,
            defaults={
                "reason": f"Automated Fire-Wall: Excessive {action_type} submissions (Spam Bot Detection).",
                "expires_at": timezone.now() + timedelta(hours=24)
            }
        )
        return True

    return False