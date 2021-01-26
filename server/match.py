from aiohttp import web
import logging

logger = logging.getLogger("Match-V4")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(
    logging.Formatter('%(asctime)s [Match-V4] %(message)s'))
logger.addHandler(handler)


async def match_v4_matches(self, request):
    """Query handler for the endpoints under the method /lol/match/v4/matches."""
    https = request.rel_url.replace('http://', 'https://')
    async with self.session.get(https, headers={key: dict(request.headers)[key] for key in dict(request.headers) if
                                                key in self.required_header}) as response:
        resp = await response.text()
        logger.info("Query to %s", request.rel_url)
        return response


async def match_v4_matchlists(self, request):
    """Query handler for the endpoints under the method /lol/match/v4/matchlists."""
    https = request.rel_url.replace('http://', 'https://')
    async with self.session.get(https, headers={key: dict(request.headers)[key] for key in dict(request.headers) if
                                                key in self.required_header}) as response:
        resp = await response.text()
        logger.info("Query to %s", request.rel_url)
        return response


async def match_v4_timelines(self, request):
    """Query handler for the endpoints under the method /lol/match/v4/timelines."""
    https = request.rel_url.replace('http://', 'https://')
    async with self.session.get(https, headers={key: dict(request.headers)[key] for key in dict(request.headers) if
                                                key in self.required_header}) as response:
        resp = await response.text()
        logger.info("Query to %s", request.rel_url)
        return response
