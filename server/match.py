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
    target = request.rel_url
    https = target.replace('http://', 'https://')
    async with self.session.get(https, headers={key: dict(request.headers)[key] for key in dict(request.headers) if
                                                key in self.required_header}) as response:
        resp = await response.text()
        logger.info("Query to %s", target)
        return response
