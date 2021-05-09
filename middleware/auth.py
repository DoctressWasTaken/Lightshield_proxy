import logging

from aiohttp.web import middleware, HTTPException

import settings


class Headers:
    """Middleware that adds the Riot API Key to the request."""

    def __init__(self):
        self.required_header = []
        self.logging = logging.getLogger("HeaderManager")
        self.logging.propagate = False
        level = logging.INFO
        if settings.DEBUG:
            level = logging.DEBUG
        self.logging.setLevel(level)
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(
            logging.Formatter("%(asctime)s [HeaderManager] %(message)s")
        )
        self.logging.addHandler(handler)
        self.logging.info("Initiated middleware.")

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
        self.legit_server = [
            "br1",
            "eun1",
            "euw1",
            "jp1",
            "kr",
            "la1",
            "la2",
            "na1",
            "oc1",
            "tr1",
            "ru",
            "americas",
            "asia",
            "europe",
        ]
        self.logging = logging.getLogger("ServerCheck")
        self.logging.propagate = False
        level = logging.INFO
        if settings.DEBUG:
            level = logging.DEBUG
        self.logging.setLevel(level)
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter("%(asctime)s [ServerCheck] %(message)s"))
        self.logging.addHandler(handler)
        self.logging.info("Initiated middleware.")

    @middleware
    async def middleware(self, request, handler):
        """Process the request.

        request: Check if correct server
        response: No changes.
        """
        server = request.rel_url.__str__().split("http://")[1].split(".")[0]
        if server not in self.legit_server:
            self.logging.info("Illegal Server.")
            raise HTTPException
        return await handler(request)
