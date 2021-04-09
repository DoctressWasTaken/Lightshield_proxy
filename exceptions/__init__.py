from aiohttp.web import HTTPException


class HTTPTooManyRequestsLocal(HTTPException):
    """Local 429 Exception. Separated from the server side exception for logging purposes."""

    status_code = 430


class LimitBlocked(Exception):
    def __init__(self, retry_at):
        self.retry_at = retry_at
