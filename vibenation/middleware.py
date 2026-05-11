from django.utils.deprecation import MiddlewareMixin

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