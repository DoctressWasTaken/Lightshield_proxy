import asyncio
import logging
from datetime import datetime, timezone, timedelta
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
    bucket = False
    blocked = False
    verified = False
    reset_ready = False

    def __init__(self, limits=None, span=None, max_=None, method='app'):

        self.type = method

        if limits:
            max_, span = [int(i) for i in limits]
        self.span = int(span)  # Duration of the bucket
        self.max = max(5, max_ - 5)  # Max Calls per bucket (Reduced by 1 for safety measures)
        logging.info(f"Initiated {self.max}:{self.span}.")

    def __repr__(self):

        return str(self.max + 5) + ":" + str(self.span)

    def __str__(self):

        return self.__repr__()

    async def init_bucket(self, pre_verified=None, verified_count=0):
        """Create a new bucket.

        The bucket is unverified by default but can be started verified if its initialized by a delayed request.
        """
        self.bucket_task_crack.cancel()
        self.bucket_task_reset.cancel()
        duration = self.span
        if not pre_verified:
            duration *= 1.2
            self.bucket_start = datetime.now(timezone.utc)
        else:
            self.verified = verified_count
            self.bucket_start = pre_verified
        self.bucket_end = self.bucket_start + timedelta(seconds=duration)

        self.bucket = True
        self.blocked = False
        self.reset_ready = False
        self.bucket_task_reset = asyncio.get_event_loop().call_later(duration, self.destroy_bucket)
        self.bucket_task_crack = asyncio.get_event_loop().call_later(duration * 0.8, self.crack_bucket)
        self.count = 0
        logger.info("[%s] Initiated new bucket at %s.", self.span, self.bucket_start)

    async def crack_bucket(self):
        """Allow the bucket to be reset from this point forward.

        Buckets can be reset early starting 80% of its lifetime along the way.
        """
        self.reset_ready = True
        logger.info("[%s] Cracked bucket.", self.span)

    async def verify_bucket(self, verified_start, verified_count):
        """Verify an existing buckets starting point.

        Removes the extra 20% duration added as safety net.
        """
        self.verified = verified_count
        self.bucket_start = verified_start
        self.bucket_end = self.bucket_start + timedelta(seconds=self.span)
        self.bucket_task_reset.cancel()
        self.bucket_task_reset = asyncio.get_event_loop().call_at(
            (self.bucket_end - datetime.now(timezone.utc)).total_seconds(), self.destroy_bucket)
        logger.info("[%s] Verified bucket.", self.span)

    async def destroy_bucket(self):
        """Mark the bucket as destroyed.
        """
        self.bucket = False
        self.blocked = False
        file_logger.info("%s,%s,%s,%s", self.type, self.span, self.max, self.count)
        logger.info("[%s] Destroyed bucket.", self.span)

    async def add(self):
        """Called before the request is made. Throws error if Limit is reached."""
        # If already blocked throw exception
        if self.blocked:
            raise LimitBlocked(self.bucket_task_reset.when())

        # If no active bucket create a new one
        if not self.bucket:
            await self.init_bucket()

        self.count += 1
        # If count reaches/breaches max, block.
        if self.count >= self.max:
            self.blocked = True
            self.bucket = False


    async def update(self, date, limits):
        """Called with headers after the request."""
        count = None
        for limit in limits.split(","):
            if int(limit.split(":")[1]) == self.span:
                count = int(limit.split(":")[0])
        naive = datetime.strptime(
            date,
            '%a, %d %b %Y %H:%M:%S GMT')
        local = pytz.timezone('GMT')
        local_dt = local.localize(naive, is_dst=None)
        date = local_dt.astimezone(pytz.utc)
        if count <= 5 and date > self.bucket_start:
            if self.reset_ready:
                await self.init_bucket(pre_verified=date, verified_count=count)
            elif self.verified < count:
                await self.verify_bucket(verified_start=date, verified_count=count)

        if count > self.count:
            self.count = count
            if self.count >= self.max:
                self.blocked = True
                self.bucket = False
