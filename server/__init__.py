# -*- coding: utf-8 -*-
"""Proxy Module.

Routes and ratelimits all calls to the API.
"""
import asyncio  # noqa: F401
import os
import sys

import aiohttp
from aiohttp import web

sys.path.append(os.getcwd())

from auth import Headers
from rate_limiting.app_limiter import AppLimiter
from rate_limiting.method_limiter import MethodLimiter

MIDDLEWARES = [AppLimiter, MethodLimiter, Headers]


class Proxy:
    from .match import match_v4_matches, match_v4_matchlists, match_v4_timelines
    from .summoner import summoner_v4_summoners
    from .league import league_v4_entries
    from .league_exp import league_exp_v4_entries
    from .spectator import spectator_v4_active_games

    def __init__(self):
        self.middlewares = [cls() for cls in MIDDLEWARES]
        self.required_header = []
        for middleware in self.middlewares:
            self.required_header += middleware.required_header

    async def make_app(self):
        self.app = web.Application(
            middlewares=[cls.middleware for cls in self.middlewares]
        )
        self.session = aiohttp.ClientSession()
        self.app.add_routes(
            [
                web.get("/lol/match/v4/matches/{tail:.*}", self.match_v4_matches),
                web.get("/lol/match/v4/matchlists/{tail:.*}", self.match_v4_matchlists),
                web.get("/lol/match/v4/timelines/{tail:.*}", self.match_v4_timelines),
                web.get(
                    "/lol/summoner/v4/summoners/{tail:.*}", self.summoner_v4_summoners
                ),
                web.get("/lol/league/v4/entries/{tail:.*}", self.league_v4_entries),
                web.get(
                    "/lol/league-exp/v4/entries/{tail:.*}", self.league_exp_v4_entries
                ),
                web.get(
                    "/lol/spectator/v4/active-games/{tail:.*}",
                    self.spectator_v4_active_games,
                ),
            ]
        )
        return self.app
