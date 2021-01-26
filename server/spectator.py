from aiohttp import web
import logging

logger = logging.getLogger("Spectator-V4")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(
    logging.Formatter('%(asctime)s [Spectator-V4] %(message)s'))
logger.addHandler(handler)


async def spectator_v4_active_games(self, request):
    """Query handler for the endpoints under the method /lol/spectator/v4/active_games."""
    https = request.rel_url.replace('http://', 'https://')
    async with self.session.get(https, headers={key: dict(request.headers)[key] for key in dict(request.headers) if
                                                key in self.required_header}) as response:
        resp = await response.text()
        logger.info("Query to %s", request.rel_url)
        return response


