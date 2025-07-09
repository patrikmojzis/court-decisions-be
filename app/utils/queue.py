import os

from redis import Redis
from rq import Queue

rq = Queue(connection=Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT", 6379)), db=8))


def queue(func, *args, **kwargs):
    q_worker = os.getenv('QUEUE_DRIVER', "sync").lower()

    if q_worker == 'sync':
        func(*args, **kwargs)
    elif q_worker == 'rq':
        rq.enqueue(func, *args, **kwargs)
