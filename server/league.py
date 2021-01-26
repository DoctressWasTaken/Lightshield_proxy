from aiohttp import web
import logging

logger = logging.getLogger("League-V4")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(
    logging.Formatter('%(asctime)s [League-V4] %(message)s'))
logger.addHandler(handler)


async def league_v4_entries(self, request):
    """Query handler for the endpoints under the method /lol/league/v4/entries."""
    https = request.rel_url.replace('http://', 'https://')
    async with self.session.get(https, headers={key: dict(request.headers)[key] for key in dict(request.headers) if
                                                key in self.required_header}) as response:
        resp = await response.text()
        logger.info("Query to %s", request.rel_url)
        return response
