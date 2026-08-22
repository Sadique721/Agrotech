class RealIPMiddleware:
    """
    Middleware to set request.META['REMOTE_ADDR'] from HTTP_X_FORWARDED_FOR
    when running behind a reverse proxy (like Render, Cloudflare, etc.).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # The first IP in X-Forwarded-For list is the client's actual IP
            ip = x_forwarded_for.split(',')[0].strip()
            request.META['REMOTE_ADDR'] = ip
        return self.get_response(request)
