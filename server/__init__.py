# -*- coding: utf-8 -*-
"""Proxy Module.

Routes and ratelimits all calls to the API.
"""
import asyncio  # noqa: F401
from aiohttp import web
from aiohttp.web import HTTPInternalServerError
import aiohttp
import sys
import os

sys.path.append(os.getcwd())

from datetime import timezone, datetime, timedelta
import pytz
import json
import logging
# Middleware
from auth import Headers
from rate_limiting.app_limiter import AppLimiter
from rate_limiting.method_limiter import MethodLimiter
import settings

MIDDLEWARES = [
    AppLimiter,
    MethodLimiter,
    Headers,
    # Logging
]


class Proxy:
    from .match import match_v4_matches
    from .summoner import summoner_v4_summoners_by_name

    def __init__(self):
        self.middlewares = [cls() for cls in MIDDLEWARES]
        self.required_header = []
        for middleware in self.middlewares:
            self.required_header += middleware.required_header

    async def make_app(self):
        self.app = web.Application(middlewares=[cls.middleware for cls in self.middlewares])
        self.session = aiohttp.ClientSession()
        self.app.add_routes([
            web.get('/lol/match/v4/matches/{tail:.*}', self.match_v4_matches),
            web.get('/lol/summoner/v4/summoners/by-name/{tail:.*}', self.summoner_v4_summoners_by_name),
        ])
        return self.app


