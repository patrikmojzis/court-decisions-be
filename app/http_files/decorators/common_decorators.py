import os
from functools import wraps

from flask import jsonify

from app.exceptions.app_exception import AppException
from app.exceptions.http_exception import HttpException


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpException as e:
            return jsonify(e.dict()), e.status_code
        except AppException as e:
            if os.getenv("ENV") == "debug":
                raise e

            return jsonify({"server_error"}), 500

    return wrapper
