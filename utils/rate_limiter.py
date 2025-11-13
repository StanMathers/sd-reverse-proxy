import time
import asyncio

class TokenBucket:
    """
    Very small per-process token bucket limiting N requests per minute.
    NOTE: As there is a limited time, I won't be adding caching or distributed support.
    """
    def __init__(self, rate_per_min: int):
        """
        - refill_rate are tokens per second
        """
        self.capacity = max(1, rate_per_min)
        self.tokens = float(self.capacity)
        self.refill_rate = self.capacity / 60.0
        self.last = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last
            self.last = now

            # refill here
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)

            if self.tokens < 1.0:
                # need to wait for next token to be available
                to_wait = (1.0 - self.tokens) / self.refill_rate
                await asyncio.sleep(to_wait)
                self.tokens = 1.0
            # consume tokens
            self.tokens -= 1.0
