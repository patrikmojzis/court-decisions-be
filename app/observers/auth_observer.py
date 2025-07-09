import secrets
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from app.observers.observer_base import ObserverBase

if TYPE_CHECKING:
    from app.models.auth_model import Auth


class AuthObserver(ObserverBase):

    def on_creating(self, auth: 'Auth'):
        if not auth.get('expires_at'):
            auth.set('expires_at', datetime.now() + timedelta(days=365 * 20))

        if not auth.get('token'):
            auth.set('token', secrets.token_urlsafe(32))
