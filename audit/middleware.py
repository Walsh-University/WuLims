import threading
import uuid

_thread_locals = threading.local()


# =========================
# Helpers
# =========================

def get_current_user():
    return getattr(_thread_locals, "user", None)


def get_request_id():
    return getattr(_thread_locals, "request_id", None)


# =========================
# Middleware: Request ID
# =========================

class RequestIDMiddleware:
    """
    Generates unique request ID for each request
    and stores it in thread local storage.
    Adds it to response headers.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = str(uuid.uuid4())

        _thread_locals.request_id = request_id
        request.request_id = request_id

        try:
            response = self.get_response(request)
        finally:
            if hasattr(_thread_locals, "request_id"):
                delattr(_thread_locals, "request_id")

        response["X-Request-ID"] = request_id
        return response


# =========================
# Middleware: Audit User
# =========================

class AuditUserMiddleware:
    """
    Store current user in thread local storage
    so signals can access it.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = request.user
        try:
            return self.get_response(request)
        finally:
            if hasattr(_thread_locals, "user"):
                delattr(_thread_locals, "user")
