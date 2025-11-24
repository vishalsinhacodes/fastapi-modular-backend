import json
import logging
from typing import Any, Optional

import redis
from redis.exceptions import RedisError
from redis.exceptions import ConnectionError as RedisConnectionError

from app.core.config import settings

logger = logging.getLogger("app")

# Try to create Redis client with short timeouts
redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=0.2,  # 200ms connect timeout
    socket_timeout=0.2,          # 200ms read/write timeout
)

# Global flag: is Redis usable?
REDIS_AVAILABLE = True

# One-time check at startup
try:
    redis_client.ping()
    logger.info("Redis is available, caching/rate limiting enabled.")
except RedisError as e:
    REDIS_AVAILABLE = False
    logger.warning(f"Redis not available ({e}), caching/rate limiting disabled.")


def set_json(key: str, value: Any, ttl_seconds: int = 60) -> None:
    """
    Store a Python object as JSON in Redis with an expiry.
    If Redis is unavailable, just return.
    """
    if not REDIS_AVAILABLE:
        return

    data = json.dumps(value)
    try:
        redis_client.setex(key, ttl_seconds, data)
    except RedisError as e:
        logger.warning(f"Redis error in set_json: {e}")


def get_json(key: str) -> Optional[Any]:
    """
    Get JSON value from Redis and parse into Python object.
    Returns None if key doesn't exist or Redis is down.
    """
    if not REDIS_AVAILABLE:
        return None

    try:
        data = redis_client.get(key)
    except RedisError as e:
        logger.warning(f"Redis error in get_json: {e}")
        return None

    if data is None:
        return None
    return json.loads(data)


def delete_prefix(prefix: str) -> None:
    """
    Delete all keys starting with a given prefix.
    If Redis is unavailable, do nothing.
    """
    if not REDIS_AVAILABLE:
        return

    pattern = f"{prefix}*"
    try:
        for key in redis_client.scan_iter(pattern):
            redis_client.delete(key)
    except RedisError as e:
        logger.warning(f"Redis error in delete_prefix: {e}")
