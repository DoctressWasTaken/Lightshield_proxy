from server import Proxy
import asyncio  # noqa: F401
from aiohttp import web


if __name__ == '__main__':
    p = Proxy()
    web.run_app(p.make_app())
