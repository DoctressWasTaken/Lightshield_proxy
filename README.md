## Lightshield Tools

Tools and Code-Sections of the Lightshield Framework that were better fit to be provided through dependency
rather then included in the main project.



### Ratelimiter (WIP)

Multi-Host async ratelimiting service. The clients each sync via a central redis server. 

Set up the proxy in an async context with redis connection details.
```python
from lightshield.proxy import Proxy
import aiohttp

async def run():
    p = Proxy()
    # Initiate the redis connector in async context
    await p.init(host='localhost', port=5432)
```

Make singular calls directly through the Proxy.
```python
async with aiohttp.ClientSession(headers={'X-Riot-Token': ''}) as session:
    await p.request('https://euw1.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/SILVER/I', session=session)
```

Make calls directly to one endpoint without having the proxy select the proper limits 
through a regex comparison to increase processing speed.
```python
async with aiohttp.ClientSession(headers={'X-Riot-Token': ''}) as session:
    zone = await p.get_endpoint('https://euw1.api.riotgames.com/lol/league-exp/v4/entries/')
    for page in range(1, 10):
        zone.request('https://euw1.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/SILVER/I?page=%s' % page, session)
```
