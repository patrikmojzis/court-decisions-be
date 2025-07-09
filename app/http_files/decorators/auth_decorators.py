import os
from datetime import datetime
from functools import wraps

from flask import g

from app.db.mongo import get_db
from app.exceptions.database_not_initialized import DatabaseNotInitialized
from app.exceptions.unauthorised_exception import UnauthorisedException
from app.models.auth_model import Auth
from app.utils.api_utils import get_bearer_auth_token


def _authenticate_user():
    """Authenticate the user and return None if authenticated, or handle errors."""
    token = get_bearer_auth_token()
    if not token:
        raise UnauthorisedException()

    db = get_db()
    if db is None:
        raise DatabaseNotInitialized()

    auth_res = Auth.find_one({'token': token, 'expires_at': {'$gt': datetime.now()}})
    if not auth_res:
        raise UnauthorisedException()

    user = auth_res.user()
    if not user:
        raise UnauthorisedException()

    user.update({'last_seen_at': datetime.now()})
    g.user = user
    g.auth = auth_res


def protected_route(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        _authenticate_user()
        return func(*args, **kwargs)

    wrapper.__name__ = f"{func.__name__}_{id(func)}"
    return wrapper

def protected_admin_route(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = get_bearer_auth_token()
        if not token:
            raise UnauthorisedException()

        if token != os.getenv("ADMIN_AUTH_TOKEN"):
            raise UnauthorisedException()

        return func(*args, **kwargs)

    wrapper.__name__ = f"{func.__name__}_{id(func)}"
    return wrapper