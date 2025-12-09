import time
import redis
from fastapi import HTTPException, status
from config import get_settings


def _get_redis() -> redis.Redis:
    settings = get_settings()
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def check_rate_limit(user_id: str) -> None:
    """
    Simple token bucket: allow N requests per window.
    """
    settings = get_settings()
    key = f"rl:{user_id}"
    now = int(time.time())
    window = settings.rate_limit_window_seconds
    limit = settings.rate_limit_requests

    r = _get_redis()
    with r.pipeline() as pipe:
        try:
            pipe.watch(key)
            current = pipe.get(key)
            current = int(current) if current else 0
            if current >= limit:
                ttl = pipe.ttl(key)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {ttl if ttl else window} seconds.",
                )
            pipe.multi()
            pipe.incr(key, 1)
            if pipe.ttl(key) == -1:
                pipe.expire(key, window)
            pipe.execute()
        except HTTPException:
            pipe.reset()
            raise
        except redis.RedisError:
            pipe.reset()
            # Fail open: allow request but log in future
            return

