from collections import defaultdict, deque
from time import monotonic

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

MAX_REQUESTS = 60
WINDOW_SECONDS = 60
request_history: dict[str, deque[float]] = defaultdict(deque)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_key = request.client.host if request.client else "unknown"

        if is_rate_limited(client_key):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Muitas requisições. Tente novamente em um minuto."},
                headers={"Retry-After": str(WINDOW_SECONDS)},
            )

        return await call_next(request)


def is_rate_limited(key: str) -> bool:
    now = monotonic()
    window_start = now - WINDOW_SECONDS
    history = request_history[key]

    while history and history[0] < window_start:
        history.popleft()

    if len(history) >= MAX_REQUESTS:
        return True

    history.append(now)
    return False
