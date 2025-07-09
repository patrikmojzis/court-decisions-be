from typing import TYPE_CHECKING

from app.http_files.resources.resource_base import ResourceBase

if TYPE_CHECKING:
    from app.models.research_model import Research

class ResearchResource(ResourceBase):

    def to_dict(self, research: 'Research'):
        return {
            '_id': research.id,
            'query': research.query,
            'created_by_user_id': research.created_by_user_id,
            'events': research.get('events', []),
            'error': research.error,
            'result': research.result,
            'report': research.report,
            'created_at': research.created_at,
            'processing_started_at': research.processing_started_at,
            'processing_ended_at': research.processing_ended_at,
            'is_active': research.get('is_active', False)
        }