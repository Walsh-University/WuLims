import logging

from audit.middleware import get_request_id


class RequestIDFilter(logging.Filter):
    """
    Adds request_id to log records.
    """

    def filter(self, record):
        record.request_id = get_request_id()
        return True
