from server import Proxy
import asyncio  # noqa: F401
from aiohttp import web
import sys
import os
sys.path.append(os.getcwd())


async def start_gunicorn():
    """Return webserver element to gunicorn.

    Called by gunicorn directly.
    """
    proxy = Proxy()
    return await proxy.make_app()


if __name__ == '__main__':
    p = Proxy()
    web.run_app(p.make_app())
