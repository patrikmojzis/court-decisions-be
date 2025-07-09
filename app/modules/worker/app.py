import asyncio
import os
from datetime import datetime

import redis.asyncio as redis
from agents import Runner

from app.ai.agents.orchestrator_agent import orchestrator_agent
from app.ai.contexts.research_scope_context import ResearchScopeContext
from app.config.config import load_env
from app.models.research_model import Research
from app.utils.logger import setup_logger
from app.utils.redis_utils import redis_worker_pubsub_client
from app.utils.research_utils import research_event

load_env()
logger = setup_logger(__name__)


redis_worker_pubsub_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"), 
    port=int(os.getenv("REDIS_PORT", 6379)), 
    db=int(os.getenv("REDIS_WORKER_PUBSUB_DB", 11))
)


async def process_research(research: 'Research'):
    context = ResearchScopeContext()
    context.research_id = research.id
    
    research.update({
        'is_active': True,
        'processing_started_at': datetime.now(),
    })
    
    try:
        research_event(research.id, 'started')
        
        result = await Runner.run(
            starting_agent=orchestrator_agent,
            input=research.query,
            max_turns=40,
            context=context,
        )
        research.refresh()
        research.update({'result': result.final_output})
    except Exception as e:
        research.update({'error': str(e)})
    finally:
        research.update({
            'is_active': False,
            'processing_ended_at': datetime.now(),
        })
        research_event(research.id, 'ended')
    


async def run():
    print("\033[96m🚀 Worker started\033[0m")
    async with redis_worker_pubsub_client.pubsub() as pubsub:
        await pubsub.subscribe(os.getenv("REDIS_WORKER_PUBSUB_CHANNEL", "worker:new_research"))
        print(f"\033[94m📡 Listening on channel: {os.getenv('REDIS_WORKER_PUBSUB_CHANNEL', 'worker:new_research')}\033[0m")
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                research_id = message['data'].decode('utf-8')
                if research := Research.find_by_id(research_id):
                    print(f"\033[92m✨ Processing research: {research_id}...\033[0m")
                    asyncio.create_task(process_research(research))
                else:
                    print(f"\033[93m⚠️ Research not found: {research_id}...\033[0m")



async def run_as_db_polling():
    if pending_researches := Research.find({"processing_started_at": {"$exists": False}}):
        tasks = [process_research(research) for research in pending_researches]
        for task in tasks:
            asyncio.create_task(task)