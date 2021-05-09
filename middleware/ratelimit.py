import asyncio
import logging
import re
import traceback
from datetime import datetime, timezone, timedelta
import settings
import pytz
from aiohttp.web import middleware

from exceptions import LimitBlocked, HTTPTooManyRequestsLocal, HTTPException
from rate_limiting.limiter import LimitHandler


class Limiter:
    regex = re.compile(
        "https*://([a-z]{2,4}[12]?)\.api\.riotgames\.com/lol/([^/]*/v./[^/]*)/.*"
    )

    def __init__(self):
        self.required_header = [
            "Date",
            "X-Method-Rate-Limit-Count",
            "X-Method-Rate-Limit",
            "X-App-Rate-Limit-Count",
            "X-App-Rate-Limit",
        ]
        self.method_limits = {}
        self.app_limits = {}
        self.lock = asyncio.Lock()
        self.first_time_lock = (
            asyncio.Lock()
        )  # Blocks all but one request until the first request returns on a route
        self.logging = logging.getLogger("Limiter")
        self.logging.propagate = False
        level = logging.INFO
        if settings.DEBUG:
            level = logging.DEBUG
        self.logging.setLevel(level)
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter("%(asctime)s [Limiter] %(message)s"))
        self.logging.addHandler(handler)
        self.logging.info("Initiated middleware.")

    @middleware
    async def middleware(self, request, handler):
        """Handle tests for rate limits."""
        url = request.rel_url.__str__()
        server, method = self.regex.findall(url)[0]
        identifier = "%s/%s" % (server, method)
        try:
            async with self.lock:
                if identifier not in self.method_limits:
                    self.logging.info("Initiating limit for %s method.", identifier)
                    await self.first_time_lock.acquire()
                    self.method_limits[identifier] = {}
                    if server not in self.app_limits:
                        self.app_limits[server] = {}
                planning_timestamp = datetime.now(timezone.utc)
                try:
                    await asyncio.gather(
                        *[
                            asyncio.create_task(
                                limit.acquire_permit(planning_timestamp)
                            )
                            for limit in self.method_limits[identifier].values()
                        ]
                    )

                    await asyncio.gather(
                        *[
                            asyncio.create_task(
                                limit.acquire_permit(planning_timestamp)
                            )
                            for limit in self.app_limits[server].values()
                        ]
                    )

                    add = [
                        asyncio.create_task(limit.add(planning_timestamp))
                        for limit in self.method_limits[identifier].values()
                    ] + [
                        asyncio.create_task(limit.add(planning_timestamp))
                        for limit in self.app_limits[server].values()
                    ]
                    await asyncio.gather(*add)

                except LimitBlocked as err:
                    raise HTTPTooManyRequestsLocal(
                        headers={
                            "Retry-At": err.retry_at.strftime("%Y-%m-%d %H:%M:%S.%f")
                        }
                    )
                except Exception as err:
                    traceback.print_tb(err.__traceback__)
                    self.logging.error("Failed. [Code: %s]", err)
                    raise HTTPException

            pre_request = datetime.now(timezone.utc)
            response = await handler(request)
            self.logging.debug(response.headers)
            self.logging.debug(response.text)
            post_request = datetime.now(timezone.utc)
            if response and "Date" in response.headers:
                naive = datetime.strptime(
                    response.headers["Date"], "%a, %d %b %Y %H:%M:%S GMT"
                )
                local = pytz.timezone("GMT")
                local_dt = local.localize(naive, is_dst=None)
                post_request = local_dt.astimezone(pytz.utc) + timedelta(seconds=1)

            # METHOD ratelimits
            limit_status = {}
            for limit in response.headers["X-Method-Rate-Limit"].split(","):
                rate_limit, span = limit.split(":")
                limit_status[span] = {"max": int(rate_limit)}
                if span not in self.method_limits[identifier]:
                    self.method_limits[identifier][span] = LimitHandler(
                        server, span=int(span), limit=int(rate_limit), method=method
                    )
            for limit_count in response.headers["X-Method-Rate-Limit-Count"].split(","):
                rate_limit_count, span = limit_count.split(":")
                limit_status[span]["count"] = int(rate_limit_count)

                await self.method_limits[identifier][span].update(
                    pre_request, post_request, count=int(rate_limit_count)
                )
            # APP ratelimits
            limit_status = {}
            for limit in response.headers["X-App-Rate-Limit"].split(","):
                rate_limit, span = limit.split(":")
                limit_status[span] = {"max": int(rate_limit)}
                if span not in self.app_limits[server]:
                    self.app_limits[server][span] = LimitHandler(
                        server, span=int(span), limit=int(rate_limit), method="app"
                    )
            for limit_count in response.headers["X-App-Rate-Limit-Count"].split(","):
                rate_limit_count, span = limit_count.split(":")
                limit_status[span]["count"] = int(rate_limit_count)

                await self.app_limits[server][span].update(
                    pre_request, post_request, count=int(rate_limit_count)
                )

        except HTTPTooManyRequestsLocal as err:
            raise err
        except Exception as err:
            traceback.print_tb(err.__traceback__)
            self.logging.error(
                "Failed to apply response data to query. [Code: %s]", err
            )
            raise HTTPException
        finally:
            if self.first_time_lock.locked():
                self.first_time_lock.release()
        return response
