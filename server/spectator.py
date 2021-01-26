from aiohttp import web
import logging
import json


logger = logging.getLogger("Spectator-V4")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(
    logging.Formatter('%(asctime)s [Spectator-V4] %(message)s'))
logger.addHandler(handler)


async def spectator_v4_active_games(self, request):
    """Query handler for the endpoints under the method /lol/spectator/v4/active_games."""
    target = request.rel_url
    async with self.session.get(target, headers=dict(request.headers)) as response:
        logger.info("Query to %s", target)
        returned_headers = {}
        for header in response.headers:
            if header in self.required_header:
                returned_headers[header] = response.headers[header]

        res = web.Response(text=json.dumps(await response.json()), headers=returned_headers, status=response.status)
        return res



