# -*- coding: utf-8 -*-
"""Proxy Module.

Routes and ratelimits all calls to the API.
"""
import asyncio  # noqa: F401
import json
import logging
import os
import sys
from datetime import datetime, timezone
import settings
import aiohttp
import pytz
from aiohttp import web

sys.path.append(os.getcwd())

from middleware.auth import Headers, ServerCheck
from middleware.ratelimit import Limiter

MIDDLEWARES = [ServerCheck, Limiter, Headers]


class Proxy:
    def __init__(self):
        self.middlewares = [cls() for cls in MIDDLEWARES]
        self.required_header = []
        for middleware in self.middlewares:
            self.required_header += middleware.required_header

        self.logging = logging.getLogger("Proxy")
        self.logging.propagate = False
        self.logging.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        self.logging.addHandler(handler)
        self.logging.info("Initializing Proxy.")

    async def make_app(self):
        self.app = web.Application(
            middlewares=[cls.middleware for cls in self.middlewares]
        )
        self.session = aiohttp.ClientSession()
        self.app.add_routes(
            [
                web.get("/{tail:.*}", self.default),
            ]
        )
        self.logging.info("Returning web server to run handler.")
        return self.app

    async def default(self, request):
        """Query handler for all endpoints."""
        target = request.rel_url
        async with self.session.get(target, headers=dict(request.headers)) as response:
            self.logging.debug("Query to %s", target)
            returned_headers = {}
            for header in response.headers:
                if header in self.required_header:
                    returned_headers[header] = response.headers[header]
            if response.status == 429:
                self.logging.critical("429")
                self.logging.critical(returned_headers)
            res = web.Response(
                text=json.dumps(await response.json()),
                headers=returned_headers,
                status=response.status,
            )
        return res
