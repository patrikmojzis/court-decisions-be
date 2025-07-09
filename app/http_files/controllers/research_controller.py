import os

from flask import g

from app.http_files.decorators.auth_decorators import protected_route
from app.http_files.decorators.common_decorators import handle_exceptions
from app.http_files.resources.research_resource import ResearchResource
from app.http_files.schemas.research_request_schema import ResearchRequestSchema
from app.models.research_model import Research
from app.utils.api_utils import paginate_all, validate_request
from app.utils.redis_utils import redis_worker_pubsub_client


@handle_exceptions
@protected_route
def store():
    """Start a new research process"""
    validate_request(ResearchRequestSchema)
    research = Research.create({'query': g.validated['message']})
    redis_worker_pubsub_client.publish(os.getenv("REDIS_WORKER_PUBSUB_CHANNEL", "worker:new_research"), str(research.id))
    return ResearchResource(research).to_response()

@handle_exceptions
@protected_route
def show(research_id: str):
    """Get a research by ID"""
    research = Research.find_by_id_or_fail(research_id)
    return ResearchResource(research).to_response()

@handle_exceptions
@protected_route
def destroy(research_id: str):
    """Delete a research by ID"""
    research = Research.find_by_id_or_fail(research_id)
    research.delete()
    return "", 204

@handle_exceptions
@protected_route
def index():
    """Get all research"""
    return paginate_all(Research, resource=ResearchResource)