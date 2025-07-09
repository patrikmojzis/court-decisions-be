import os


def raise_if_debug(e: Exception):
    if os.getenv("ENV") == "debug":
        raise e