from datetime import datetime
from typing import TYPE_CHECKING

from app.models.model_base import ModelBase
from app.models.utils.has_observers import register_observer
from app.observers.user_observer import UserObserver

if TYPE_CHECKING:
    pass

@register_observer(UserObserver)
class User(ModelBase):

    email: str = None
    last_seen_at: datetime = None
    apple_auth_token: str = None
    google_access_token: str = None
    has_access: bool = False
    password: str = None

