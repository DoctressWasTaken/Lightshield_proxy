import asyncio
from aiohttp.web import middleware
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
