from typing import TYPE_CHECKING

from app.observers.observer_base import ObserverBase

if TYPE_CHECKING:
    from app.models.research_model import Research


class ResearchObserver(ObserverBase):

    def on_creating(self, research: 'Research'):
        # research.created_by_user_id = g.user.id
        pass
