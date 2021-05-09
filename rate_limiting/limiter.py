import asyncio
import logging
from datetime import timedelta

import settings
from exceptions import LimitBlocked


class Bucket:
    count = 0
    over_requests = 0
    blocked = False
    end_max = None
    latest_count = 0

    def __init__(self, limit, logging, max, start, end_min):
        self.logging = logging
        self.limit = limit
        self.max = max
        self.start = start
        self.latest_timestamp = start
        self.end_min = end_min
        self.end_max = end_min + timedelta(seconds=2)
        if settings.LIMIT_SHARE < 1:
            self.count += int((1 - settings.LIMIT_SHARE) * self.max) + 1

    async def add(self):
        self.count += 1
        if self.count >= self.max:
            self.blocked = True

    async def update_count(self, count):
        if self.count < count:
            self.count = count
            if self.count >= self.max:
                self.blocked = True

    async def set_end_max(self, end_max):
        if self.end_max > end_max:
            self.end_max = end_max

    async def close(self, start_next):
        """Send a short message with status of the closing bucket."""
        self.logging.info(
            "",
            extra={
                "previous": "%s/%s" % (self.count, self.max),
                "dead": round((self.end_max - self.end_min).total_seconds(), 5),
                "space": round((start_next - self.end_max).total_seconds(), 5),
                "over": self.over_requests,
            },
        )


class LimitHandler:
    bucket = None

    def __init__(self, server, span=None, limit=None, method="app"):

        self.type = method
        self.logging = logging
        self.span = span  # Duration of the bucket
        self.max = limit  # Max Calls per bucket (Reduced by some for safety measures)
        self.logging.info(f"Initiated %s with %s:%s.", self.type, self.max, self.span)
        self.init_lock = asyncio.Lock()
        self.logging = logging.getLogger(f"[{server.upper()}:{method}:{span}]")
        self.logging.propagate = False
        level = logging.INFO
        if settings.DEBUG:
            level = logging.DEBUG
        self.logging.setLevel(level)
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(name)45s previous: %(previous)15s | dead: %(dead)7s | space: %(space)8s | over: %(over)s"
            )
        )
        self.logging.addHandler(handler)

    def __repr__(self):

        return str(self.max) + ":" + str(self.span)

    def __str__(self):

        return self.__repr__()

    async def init_bucket(self, start_time):
        """Create a new bucket.

        The bucket is unverified by default but can be started verified if its initialized by a delayed request.
        """
        if self.bucket and self.bucket.end_max >= start_time:
            return
        if self.bucket:
            await self.bucket.close(start_time)
        self.bucket = Bucket(
            logging=self.logging,
            limit=self,
            max=self.max,
            start=start_time,
            end_min=start_time + timedelta(seconds=self.span),
        )

    async def acquire_permit(self, planning_timestamp):
        """Verify if the limit still has space. If not throws error."""
        if self.bucket.end_max < planning_timestamp:
            return self.bucket
        if self.bucket.end_min < planning_timestamp:
            raise LimitBlocked(retry_at=self.bucket.end_max)
        if not self.bucket.blocked:
            return self.bucket
        self.bucket.over_requests += 1
        raise LimitBlocked(retry_at=self.bucket.end_max)

    async def add(self, planning_timestamp):
        if self.bucket.end_max < planning_timestamp:
            await self.init_bucket(planning_timestamp)

        await self.bucket.add()

    async def update(self, pre, post, count):
        """Called with headers after the request."""
        # Create bucket if non-existent
        async with self.init_lock:
            if not self.bucket:
                await self.init_bucket(pre)
                await self.bucket.set_end_max(post + timedelta(seconds=self.span))
            # or timed out
            elif (
                post > self.bucket.latest_timestamp
                and count <= self.bucket.latest_count
            ):
                await self.init_bucket(pre)
                await self.bucket.set_end_max(post + timedelta(seconds=self.span))

        # Ignore requests that are too old
        if post < self.bucket.latest_timestamp:
            return

        await self.bucket.set_end_max(post + timedelta(seconds=self.span))

        # Update the latest received response
        if count > self.bucket.latest_count:
            self.bucket.latest_count = count
            self.bucket.latest_timestamp = post

        await self.bucket.update_count(count)
