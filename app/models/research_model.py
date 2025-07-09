from datetime import datetime
from typing import TYPE_CHECKING

from bson import ObjectId

from app.models.model_base import ModelBase
from app.models.utils.has_observers import register_observer
from app.observers.research_observer import ResearchObserver

if TYPE_CHECKING:
    pass

@register_observer(ResearchObserver)
class Research(ModelBase):

    query: str = None
    created_by_user_id: ObjectId = None
    events: list[dict] = []
    error: str = None
    result: str = None
    report: str = None
    is_active: bool = False
    
    processing_started_at: datetime = None
    processing_ended_at: datetime = None
    
    def user(self):
        from app.models.user_model import User
        return self.belongs_to(User, 'created_by_user_id')


