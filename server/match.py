from aiohttp import web
import logging
import json


logger = logging.getLogger("Match-V4")
logger.propagate = False
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(
    logging.Formatter('%(asctime)s [Match-V4] %(message)s'))
logger.addHandler(handler)


async def match_v4_matches(self, request):
    """Query handler for the endpoints under the method /lol/match/v4/matches."""
    target = request.rel_url
    async with self.session.get(target, headers=dict(request.headers)) as response:
        logger.debug("Query to %s", target)
        returned_headers = {}
        for header in response.headers:
            if header in self.required_header:
                returned_headers[header] = response.headers[header]

        res = web.Response(text=json.dumps(await response.json()), headers=returned_headers, status=response.status)
        return res


async def match_v4_matchlists(self, request):
    """Query handler for the endpoints under the method /lol/match/v4/matchlists."""
    target = request.rel_url
    async with self.session.get(target, headers=dict(request.headers)) as response:
        logger.debug("Query to %s", target)
        returned_headers = {}
        for header in response.headers:
            if header in self.required_header:
                returned_headers[header] = response.headers[header]

        res = web.Response(text=json.dumps(await response.json()), headers=returned_headers, status=response.status)
        return res


async def match_v4_timelines(self, request):
    """Query handler for the endpoints under the method /lol/match/v4/timelines."""
    target = request.rel_url
    async with self.session.get(target, headers=dict(request.headers)) as response:
        logger.debug("Query to %s", target)
        returned_headers = {}
        for header in response.headers:
            if header in self.required_header:
                returned_headers[header] = response.headers[header]

        res = web.Response(text=json.dumps(await response.json()), headers=returned_headers, status=response.status)
        return res

