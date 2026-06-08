from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden

class AdminURLFixerMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # We only care about HTML pages in the Boss Portal
        if request.path.startswith('/vibenation-admin-1999/') and "text/html" in response.get("Content-Type", ""):
            content = response.content.decode("utf-8")
            # We do this on the final HTML output so Unfold can't stop us
            new_content = content.replace('/vibe-crew-login-2026/', '/vibenation-admin-1999/')
            
            response.content = new_content.encode("utf-8")
            response["Content-Length"] = len(response.content)
            
        return response

# ============ IpBlockMiddleware =================
class IpBlockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Capture the true client IP (accounting for Cloudflare / Proxy layers)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Query check for active blocks matching client footprint
        from news.models import IpBlock
        active_block = IpBlock.objects.filter(
            ip_address=ip, 
            expires_at__gt=timezone.now()
        ).first()

        if active_block:
            err_msg = f"🚫 Access Denied. Your IP address [{ip}] is restricted. Reason: {active_block.reason or 'Terms violation.'}"
            
            # Intercept async AJAX comment posts cleanly
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "status": "error",
                    "message": err_msg
                }, status=403)
            
            # Intercept standard page document views
            return HttpResponseForbidden(f"<h1>403 Forbidden</h1><p>{err_msg}</p>")

        return self.get_response(request)