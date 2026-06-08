def get_cloudflare_ip(group, request):
    """
    Safely extracts the visitor's real IP address passed by Cloudflare.
    Falls back to REMOTE_ADDR if testing locally without Cloudflare proxy.
    """
    return request.META.get('HTTP_CF_CONNECTING_IP', request.META.get('REMOTE_ADDR'))