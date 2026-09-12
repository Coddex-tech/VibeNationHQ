from rest_framework.throttling import SimpleRateThrottle


class ResendVerificationThrottle(SimpleRateThrottle):
    """
    Limits how frequently an IP address can request
    email-verification resends.
    """

    scope = "resend_verification"

    def get_cache_key(self, request, view):
        if not request.META.get("REMOTE_ADDR"):
            return None

        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }