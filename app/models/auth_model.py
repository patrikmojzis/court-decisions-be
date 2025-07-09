from datetime import datetime

from bson import ObjectId

from app.models.model_base import ModelBase
from app.models.utils.has_observers import register_observer
from app.observers.auth_observer import AuthObserver


@register_observer(AuthObserver)
class Auth(ModelBase):

    token: str = None
    user_id: ObjectId = None
    expires_at: datetime = None
    identification: str = None

    def user(self):
        from app.models.user_model import User
        return self.belongs_to(User)