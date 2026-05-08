import logging
import time


request_logger = logging.getLogger('api.requests')


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started_at = time.monotonic()
        response = self.get_response(request)
        duration_ms = int((time.monotonic() - started_at) * 1000)

        if request.path.startswith('/api/'):
            user = getattr(request, 'user', None)
            username = user.username if user and user.is_authenticated else 'anonymous'
            request_logger.info(
                '%s %s %s %sms user=%s',
                request.method,
                request.path,
                response.status_code,
                duration_ms,
                username,
            )

        return response
