from fastapi import HTTPException, status
from redis.exceptions import RedisError

from app.core.redis_client import redis_client, REDIS_AVAILABLE


def rate_limit(
    user_id: int,
    route: str,
    limit: int = 20,
    window_seconds: int = 60,
) -> None:
    if not REDIS_AVAILABLE:
        # Redis is down → no rate limiting, but don't slow the request
        return

    key = f"rate:{user_id}:{route}"

    try:
        current = redis_client.incr(key)
        if current == 1:
            redis_client.expire(key, window_seconds)
    except RedisError as e:
        # In case Redis goes down after startup
        # Fail open: no rate limiting but don't crash or delay.
        return

    if current > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
        )
