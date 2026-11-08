"""Retry transient API failures (504 gateway timeouts, 5xx, connection errors, rate limits).

The same request is simply sent again (up to 4 attempts, backoff 3/6/12 s), so a retried call is
identical to an unretried one; only runs that would have been lost to an API error are saved.
"""
import asyncio

RETRY_STATUS = {408, 409, 429, 500, 502, 503, 504}


def transient(e):
    status = getattr(e, "status_code", None) or getattr(getattr(e, "response", None), "status_code", None)
    name = type(e).__name__
    return status in RETRY_STATUS or any(k in name for k in ("Timeout", "Connection", "InternalServer", "RateLimit"))


async def create(client, attempts=4, **kwargs):
    for i in range(attempts):
        try:
            return await client.responses.create(**kwargs)
        except Exception as e:
            if i == attempts - 1 or not transient(e):
                raise
            await asyncio.sleep(3 * 2 ** i)
