import sys
import os

sys.path.append(os.getcwd())
from server import Proxy
import asyncio  # noqa: F401
from aiohttp import web
import logging

