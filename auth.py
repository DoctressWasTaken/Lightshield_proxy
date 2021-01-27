import asyncio
from aiohttp.web import middleware, HTTPException
import os
from datetime import datetime
import logging
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
        headers.update({'X-Riot-Token': settings.API_KEY})
        url = str(request.url)
        request = request.clone(headers=headers, rel_url=url.replace("http:", "https:"))
        return await handler(request)


class ServerCheck:
    """Middleware that makes sure the request is aimed at the proper server."""
    def __init__(self):
        self.required_header = []
        print("Server Check initialized.")
        self.required_name = "%s.api.riotgames.com" % settings.SERVER.lower()

    @middleware
    async def middleware(self, request, handler):
        """Process the request.

        request: Check if correct server
        response: No changes.
        """
        if self.required_name not in request.rel_url.__str__().split("/")[2]:
            raise HTTPException
        return await handler(request)
