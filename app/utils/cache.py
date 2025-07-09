import os
import pickle
from typing import Optional

import redis

r = redis.Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT", 6379)), db=2)

class Cache:
    @classmethod
    def set(cls, key: str, value: any, expire_in_m: Optional[int] = None):
        """
        Set a value in the cache.
        :param key: The cache key.
        :param value: The value to store.
        :param expire_in_m: Expiration time in minutes (optional).
        """
        serialized_value = pickle.dumps(value)
        if expire_in_m is not None:
            r.setex(key, expire_in_m * 60, serialized_value)
        else:
            r.set(key, serialized_value)

    @classmethod
    def get(cls, key: str, default=None):
        """
        Get a value from the cache.
        :param key: The cache key.
        :param default: Default value if key doesn't exist.
        :return: The cached value or default.
        """
        value = r.get(key)
        if value is None:
            return default
        return pickle.loads(value)

    @classmethod
    def delete(cls, key: str):
        """
        Delete a value from the cache.
        :param key: The cache key to delete.
        """
        r.delete(key)

    @classmethod
    def exists(cls, key: str) -> bool:
        """
        Check if a key exists in the cache.
        :param key: The cache key to check.
        :return: True if the key exists, False otherwise.
        """
        return r.exists(key) > 0

    @classmethod
    def increment(cls, key: str, amount: int = 1):
        """
        Increment a numeric value in the cache.
        :param key: The cache key.
        :param amount: The amount to increment by.
        :return: The new value.
        """
        return r.incr(key, amount)

    @classmethod
    def decrement(cls, key: str, amount: int = 1):
        """
        Decrement a numeric value in the cache.
        :param key: The cache key.
        :param amount: The amount to decrement by.
        :return: The new value.
        """
        return r.decr(key, amount)

    @classmethod
    def remember(cls, key: str, callback, expire_in_m: Optional[int] = None):
        """
        Get an item from the cache, or store the default value.
        :param key: The cache key.
        :param expire_in_m: Expiration time in minutes.
        :param callback: Function that returns the default value.
        :return: The cached value.
        """
        value = cls.get(key)
        if value is None:
            value = callback()
            cls.set(key, value, expire_in_m)
        return value

    @classmethod
    def flush(cls):
        """
        Flush the entire cache.
        """
        r.flushdb()
