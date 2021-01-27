from aiohttp.web import middleware, HTTPException
from rate_limiting.limiter import LimitBlocked, LimitHandler
import logging

logger = logging.getLogger("MethodLimiter-V4")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(
    logging.Formatter('%(asctime)s [MethodLimiter-V4] %(message)s'))
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
        print(request.path)
        method = "-".join(request.path.split("/")[1:5])
        print(method)
        try:
            for limit in self.limits[method].values():
                limit.add
        except LimitBlocked as err:
            logger.error("Limit reached")
            raise HTTPTooManyRequestsLocal(headers={"Retry-After": str(err.retry_after)})
        except KeyError:
            self.limits[method] = {}

        response = await handler(request)
        try:
            for limit in response.headers['X-Method-Rate-Limit'].split(","):
                max_, span = [int(i) for i in limit.split(":")]
                if str(span) not in self.limits[method]:
                    self.limits[method][str(span)] = LimitHandler(span=span, max_=max_)
                await self.limits[method][str(span)].update(
                    response.headers['Date'],
                    response.headers['X-App-Rate-Limit-Count'])
        except Exception as err:
            logger.error("Failed to apply response data to query. [Code: %s]", err)
            raise HTTPException
        return response
