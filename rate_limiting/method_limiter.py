import logging
import traceback

from aiohttp.web import middleware, HTTPException

from rate_limiting.limiter import LimitBlocked, LimitHandler

logger = logging.getLogger("MethodLimiter")
logger.propagate = False
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(
    logging.Formatter('%(asctime)s [MethodLimiter] %(message)s'))
logger.addHandler(handler)


class HTTPTooManyRequestsLocal(HTTPException):
    """Local 429 Exception. Separated from the server side exception for logging purposes."""
    status_code = 430


class MethodLimiter:
    """Middleware that checks method wide limits."""

    def __init__(self):
        self.required_header = ['Date', 'X-Method-Rate-Limit-Count', 'X-Method-Rate-Limit']
        self.limits = {}

    @middleware
    async def middleware(self, request, handler):
        """Process the request.

        request: Add X-Riot-Token Header with the API Key.
        response: No changes.
        """
        method = "-".join(request.path.split("/")[1:5])
        try:
            for limit in self.limits[method].values():
                await limit.add()
        except LimitBlocked as err:
            raise HTTPTooManyRequestsLocal(headers={"Retry-After": str(err.retry_after)})
        except KeyError:
            self.limits[method] = {}

        response = await handler(request)
        try:
            for limit in response.headers['X-Method-Rate-Limit'].split(","):
                max_, span = limit.split(":")
                max_ = int(max_)
                if span not in self.limits[method]:
                    self.limits[method][span] = LimitHandler(span=int(span), max_=max_, method=method, logging=logger)
                await self.limits[method][span].update(
                    response.headers['Date'],
                    response.headers['X-Method-Rate-Limit-Count'])
        except Exception as err:
            traceback.print_tb(err.__traceback__)
            logger.error("Failed to apply response data to query. [Code: %s]", err)
            raise HTTPException
        return response
