
import asyncio

from colorama import init

from agents import Runner, trace
from app.ai.agents.orchestrator_agent import orchestrator_agent
from app.ai.contexts.research_scope_context import ResearchScopeContext
from app.config.config import load_env

# Initialize colorama for cross-platform color support
init(autoreset=True)
            
load_env()
    
async def main():
    msg = input("\033[34m>>>\033[0m ")
    
    context = ResearchScopeContext()
        
    with trace("Research workflow"):
        result = await Runner.run(
            starting_agent=orchestrator_agent,
            input=msg,
            max_turns=40,
            context=context,
        )
        
    print(f"\033[32m{result}\033[0m")
    
    
if __name__ == "__main__":
    asyncio.run(main())