from aiohttp.web import middleware, HTTPException
import json
from rate_limiting.limiter import LimitBlocked, LimitHandler



class MethodLimiter:
    """Middleware that checks method wide limits."""

    def __init__(self):
        self.required_header = ['Date', 'X-Method-Rate-Limit-Count']
        limits = json.loads(open("configs/limits.json", "r").read())['METHODS']
        self.limits = {}
        for method in limits:
            self.limits[method] = [
                LimitHandler(meth.split(":")) for meth in limits[method]]

    @middleware
    async def middleware(self, request, handler):
        """Process the request.

        request: Add X-Riot-Token Header with the API Key.
        response: No changes.
        """
        url = str(request.url)
        method = "/".join(url.split("/lol/")[1].split("/")[0:3])

        try:
            for limit in self.limits[method]:
                limit.add
        except LimitBlocked as err:
            raise HTTPTooManyRequestsLocal(headers={"Retry-After": str(err.retry_after)})
        except KeyError:
            raise HTTPException("Request target was not recognized")
        response = await handler(request)
        if 'X-Method-Rate-Limit-Count' not in response.headers:
            raise HTTPException
        if 'Date' not in response.headers:
            raise HTTPException
        for limit in self.limits[method]:
            await limit.update(
                response.headers['Date'],
                response.headers['X-Method-Rate-Limit-Count'].split(","))
        return response
