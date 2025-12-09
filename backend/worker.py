from rq import Worker
from queue import get_redis


if __name__ == "__main__":
    redis_conn = get_redis()
    worker = Worker(["default"], connection=redis_conn)
    worker.work(with_scheduler=True)

