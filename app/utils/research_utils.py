import json

from bson import ObjectId

from app.http_files.resources.research_resource import ResearchResource
from app.models.research_model import Research
from app.utils.redis_utils import redis_events_pubsub_client


def research_event(research_id: str | ObjectId, event_type: str, event_data: dict = None):
    event = {
        "type": event_type,
        "data": event_data
    }
    
    if research := Research.find_by_id(research_id):
        research.update({
            "events": research.get("events", []) + [event]
        })
        
        redis_events_pubsub_client.publish(f"research:{str(research_id)}", json.dumps(ResearchResource(research).dump()))


