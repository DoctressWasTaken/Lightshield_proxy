import asyncio
import logging
from datetime import datetime, timedelta
from logging import handlers

import pytz

import settings

logger = logging.getLogger("Limiter")
logger.propagate = False
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(
    logging.Formatter('%(asctime)s [Limiter] %(message)s'))
logger.addHandler(handler)

file_logger = logging.getLogger("log_writer")
file_logger.setLevel(logging.INFO)
file_logger.addHandler(
    handlers.TimedRotatingFileHandler('/logs/%s_bucket_usage_.log' % settings.SERVER.lower(), when='h', interval=1,
                                      backupCount=24)
)


class LimitBlocked(Exception):

    def __init__(self, retry_after):
        self.retry_after = retry_after


class LimitHandler:

    bucket_active = False
    bucket_start = None

    bucket_killer = None  # call_later() that deletes the current bucket
    bucket_reset_limiter = None  # call_later() that enables an early refresh on the bucket
    bucket_refreshable = None  # If true bucket can be refreshed
    bucket_verifier = None  # Count used to reconfigure a bucket.
    count = None

    def __init__(self, limits=None, span=None, max_=None, method='app'):

        self.type = method

        if limits:
            max_, span = [int(i) for i in limits]
        self.span = int(span)  # Duration of the bucket
        self.max = max(5, max_ - 5)  # Max Calls per bucket (Reduced by 5 for safety measures)
        logging.info(f"Initiated {self.max}:{self.span}.")
        self.sync_create_bucket()

    def __repr__(self):
        return str(self.max + 5) + ":" + str(self.span)

    def __str__(self):
        return self.__repr__()

    @property
    def add(self):
        """Called before the request is made. Throws error if Limit is reached."""
        # (Re)set bucket if applicable
        if not self.bucket_active:
            self.sync_create_bucket()

        if self.count < self.max:
            self.count += 1
            return
        raise LimitBlocked(self.when_reset())

    async def allow_reset(self):
        self.bucket_refreshable = True

    def sync_create_bucket(self):
        self.bucket_start = datetime.utcnow()
        self.bucket_killer = asyncio.get_event_loop().call_later(self.span + 1.5, self.close_bucket)
        self.bucket_reset_limiter = asyncio.get_event_loop().call_later((self.span + 1.5) * 0.8, self.allow_reset)
        self.bucket_refreshable = False
        self.bucket_verifier = False
        self.count = 0
        self.bucket_active = True

    async def create_bucket(self):
        self.bucket_start = datetime.utcnow()
        self.bucket_killer = asyncio.get_event_loop().call_later(self.span + 1.5, self.close_bucket)
        self.bucket_reset_limiter = asyncio.get_event_loop().call_later((self.span + 1.5) * 0.8, self.allow_reset)
        self.bucket_refreshable = False
        self.bucket_verifier = False
        self.count = 0
        self.bucket_active = True

    async def close_bucket(self):
        """Closes and removes the bucket at a specified time."""
        self.bucket_active = False
        file_logger.info("%s,%s,%s,%s", self.type, self.span, self.max, self.count)

    def when_reset(self):
        """Return seconds until reset."""
        return int((self.bucket_start - datetime.utcnow() + timedelta(seconds=self.span)).total_seconds())

    async def update(self, date, limits):
        """Called with headers after the request."""
        count = None
        for limit in limits.split(","):
            if int(limit.split(":")[1]) == self.span:
                count = int(limit.split(":")[0])
        if not count:
            return
        naive = datetime.strptime(
            date,
            '%a, %d %b %Y %H:%M:%S GMT')
        local = pytz.timezone('GMT')
        local_dt = local.localize(naive, is_dst=None)
        date = local_dt.astimezone(pytz.utc)
        if date < self.bucket_start:  # Call too old
            return
        if count <= 10:  # Early call handling
            if not self.bucket_active or self.bucket_refreshable:
                await self.create_bucket()
                self.count = count
                return
            if not self.bucket_verifier or count < self.bucket_verifier:
                # remove old timed handler
                self.bucket_killer.cancel()
                self.bucket_reset_limiter.cancel()
                # create new timed handler
                asyncio.get_event_loop().call_at(date + timedelta(self.span), self.close_bucket)
                asyncio.get_event_loop().call_later(date + timedelta(self.span * 0.8), self.allow_reset)
        else:
            if count > self.count:
                self.count = count
