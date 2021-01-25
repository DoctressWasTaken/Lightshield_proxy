import aiohttp
import asyncio


async def fetch(session):
    async with session.get("http://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/Doctress",
                           proxy='http://localhost:8080') as response:
        resp = await response.json()
        print(response.status)
        print(resp)
        return resp


async def main():
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[asyncio.create_task(fetch(session)) for i in range(1)])

    await asyncio.sleep(.5)


asyncio.run(main())
