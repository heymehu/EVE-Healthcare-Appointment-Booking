from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.redis import get_redis_client, redis_lifespan, close_redis_pool, REDIS_AVAILABLE

settings = get_settings()


def get_limiter_storage_uri() -> str:
    if settings.RATE_LIMIT_ENABLED and REDIS_AVAILABLE:
        try:
            client = get_redis_client()
            if client:
                return settings.REDIS_URL
        except Exception:
            pass
    return "memory://"


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW_SECONDS}seconds"] if settings.RATE_LIMIT_ENABLED else [],
    storage_uri=get_limiter_storage_uri(),
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded",
            "retry_after": exc.retry_after,
        },
    )


def setup_rate_limiter(app: FastAPI) -> None:
    if not settings.RATE_LIMIT_ENABLED:
        return
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    async with redis_lifespan():
        yield