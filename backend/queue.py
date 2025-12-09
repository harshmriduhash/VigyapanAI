import redis
from rq import Queue
from config import get_settings


def get_redis() -> redis.Redis:
    settings = get_settings()
    return redis.Redis.from_url(settings.redis_url)


def get_queue(name: str = "default") -> Queue:
    return Queue(name, connection=get_redis())

