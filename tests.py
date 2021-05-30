import asyncio
import logging

import aiohttp

import settings
from lightshield.proxy import Proxy

logging.basicConfig(level=logging.DEBUG, format='%(levelname)8s %(name)s %(message)s')


async def fetch(endpoint, session):
    url = 'https://euw1.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/CHALLENGER/I'
    try:
        await endpoint.request(url, session)
    except:
        pass


async def run():
    url = 'https://euw1.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/CHALLENGER/I'
    proxy = Proxy()
    await proxy.init(host='localhost', port=6380)
    endpoint = await proxy.get_endpoint(url)
    headers = {'X-Riot-Token': settings.API_KEY}
    async with aiohttp.ClientSession(headers=headers) as session:
        for i in range(150):
            await asyncio.gather(*[
                asyncio.create_task(fetch(endpoint, session)) for _ in range(9)
            ])
            await asyncio.sleep(1)

    await asyncio.sleep(1)


asyncio.run(run())
