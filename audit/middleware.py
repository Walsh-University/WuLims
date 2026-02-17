import threading

_thread_locals = threading.local()


def get_current_user():
    return getattr(_thread_locals, "user", None)


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
