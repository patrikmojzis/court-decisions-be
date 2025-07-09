import os

import redis

redis_events_pubsub_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"), 
    port=int(os.getenv("REDIS_PORT", 6379)), 
    db=int(os.getenv("REDIS_EVENTS_PUBSUB_DB", 10))
)

redis_worker_pubsub_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"), 
    port=int(os.getenv("REDIS_PORT", 6379)), 
    db=int(os.getenv("REDIS_WORKER_PUBSUB_DB", 11))
)