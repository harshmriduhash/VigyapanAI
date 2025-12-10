import time
import redis
from fastapi import HTTPException, status
from config import get_settings
from queue import get_redis


def _key(user_id: str) -> str:
    return f"credits:{user_id}"


def get_balance(user_id: str) -> int:
    r: redis.Redis = get_redis()
    value = r.get(_key(user_id))
    return int(value) if value else 0


def add_credits(user_id: str, amount: int, ttl_days: int | None = 30) -> int:
    r: redis.Redis = get_redis()
    key = _key(user_id)
    with r.pipeline() as pipe:
        while True:
            try:
                pipe.watch(key)
                current = int(pipe.get(key) or 0)
                new_balance = current + amount
                pipe.multi()
                pipe.set(key, new_balance)
                if ttl_days:
                    pipe.expire(key, ttl_days * 86400)
                pipe.execute()
                return new_balance
            except redis.WatchError:
                continue


def consume_credit(user_id: str) -> None:
    r: redis.Redis = get_redis()
    key = _key(user_id)
    with r.pipeline() as pipe:
        while True:
            try:
                pipe.watch(key)
                current = int(pipe.get(key) or 0)
                if current <= 0:
                    raise HTTPException(
                        status_code=status.HTTP_402_PAYMENT_REQUIRED,
                        detail="No credits remaining. Please purchase a plan.",
                    )
                pipe.multi()
                pipe.decr(key, 1)
                pipe.execute()
                return
            except redis.WatchError:
                continue

