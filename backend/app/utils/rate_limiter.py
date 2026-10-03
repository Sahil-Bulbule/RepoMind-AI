import time
from collections import defaultdict
from threading import Lock
from fastapi import Request, HTTPException, status

class SlidingWindowRateLimiter:
    """
    Thread-safe in-memory sliding window rate limiter.
    Provides abuse protection without requiring Redis.
    """
    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.window = 60.0
        self.requests = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, client_key: str, limit: int = None) -> bool:
        max_allowed = limit or self.rpm
        now = time.time()
        
        with self.lock:
            timestamps = self.requests[client_key]

            cutoff = now - self.window
            while timestamps and timestamps[0] < cutoff:
                timestamps.pop(0)

            if len(timestamps) >= max_allowed:
                return False

            timestamps.append(now)
            return True

    def check_request(self, request: Request, custom_limit: int = None):
        """
        FastAPI dependency / helper to check rate limit for the incoming request.
        """

        client_ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        if not self.is_allowed(client_ip, limit=custom_limit):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please wait a moment before sending more requests."
            )


global_rate_limiter = SlidingWindowRateLimiter(requests_per_minute=60)
chat_rate_limiter = SlidingWindowRateLimiter(requests_per_minute=30)
analyze_rate_limiter = SlidingWindowRateLimiter(requests_per_minute=10)
