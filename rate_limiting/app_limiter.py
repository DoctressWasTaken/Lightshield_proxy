from aiohttp.web import middleware, HTTPException
from rate_limiting.limiter import LimitBlocked, LimitHandler
import logging
import traceback

logger = logging.getLogger("AppLimiter")
logger.propagate = False
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(
    logging.Formatter('%(asctime)s [AppLimiter] %(message)s'))
logger.addHandler(handler)


class HTTPTooManyRequestsLocal(HTTPException):
    """Local 429 Exception. Separated from the server side exception for logging purposes."""
    status_code = 430


class AppLimiter:
    """Middleware that checks app wide limits."""

    def __init__(self):
        self.required_header = ['Date', 'X-App-Rate-Limit-Count', 'X-App-Rate-Limit', 'Content-Type']
        self.limits = {}
        print("App limiter initialized.")

    @middleware
    async def middleware(self, request, handler):
        """Process the request.

        request: Add X-Riot-Token Header with the API Key.
        response: No changes.
        """
        for limit in self.limits.values():
            try:
                await limit.add()
            except LimitBlocked as err:
                raise HTTPTooManyRequestsLocal(headers={"Retry-After": str(err.retry_after)})

        response = await handler(request)
        if response.status == 429 and 'X-App-Rate-Limit' in response.headers:
            logger.warning('Limit breached (Bad).')
        elif response.status == 429:
            logger.warning('Limit breached (Care).')

        try:
            for limit in response.headers['X-App-Rate-Limit'].split(","):
                max_, span = [int(i) for i in limit.split(":")]
                if str(span) not in self.limits:
                    self.limits[str(span)] = LimitHandler(span=span, max_=max_)
                await self.limits[str(span)].update(
                    response.headers['Date'],
                    response.headers['X-App-Rate-Limit-Count'])
        except Exception as err:
            traceback.print_tb(err.__traceback__)
            logger.error("Failed to apply response data to query. [Code: %s]", err)
            raise HTTPException

        return response
