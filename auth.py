from aiohttp.web import middleware, HTTPException

import settings


class Headers:
    """Middleware that adds the Riot API Key to the request."""

    def __init__(self):
        self.required_header = []
        print("Header manager initialized.")

    @middleware
    async def middleware(self, request, handler):
        """Process the request.

        request: Add X-Riot-Token Header with the API Key.
        response: No changes.
        """
        headers = dict(request.headers)
        headers.update({"X-Riot-Token": settings.API_KEY})
        url = str(request.url)
        request = request.clone(headers=headers, rel_url=url.replace("http:", "https:"))
        return await handler(request)


class ServerCheck:
    """Middleware that makes sure the request is aimed at the proper server."""

    def __init__(self):
        self.required_header = []
        print("Server Check initialized.")
        self.legit_server = ["br1", "eun1", "euw1", "jp1", "kr", "la1", "la2", "na1", "oc1", "tr1"]

    @middleware
    async def middleware(self, request, handler):
        """Process the request.

        request: Check if correct server
        response: No changes.
        """
        server = request.rel_url.__str__().split('https://')[0].split('.')[0]
        if server not in self.legit_server:
            raise HTTPException
        return await handler(request)
