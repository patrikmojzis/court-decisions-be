import json
from datetime import datetime
from typing import Dict, Any

from agents import Agent, AgentHooks, RunContextWrapper, Tool
from bson import ObjectId
from colorama import Fore, Style

from app.ai.contexts.research_scope_context import ResearchScopeContext
from app.models.research_model import Research
from app.utils.redis_utils import redis_events_pubsub_client


class PrintHooks(AgentHooks):
    def __init__(self, display_name: str):
        self.event_counter = 0
        self.display_name = display_name

    def _get_agent_color(self) -> str:
        """Get a consistent color for this agent based on display name"""
        # Create a simple hash-based color assignment
        agent_colors = {
            "orchestrator_agent": Fore.BLUE,
            "scraping_agent": Fore.CYAN,
            "pdf_analyser_agent": Fore.MAGENTA,
            "pdf_reader_agent": Fore.YELLOW,
            "scraping_results_analyser_agent": Fore.GREEN,  
            "law_agent": Fore.RED,
            "report_agent": Fore.CYAN,
        }
        # Default color if agent not in mapping
        return agent_colors.get(self.display_name, Fore.WHITE)

    def _get_event_style(self, event_type: str) -> str:
        """Get style modifier based on event type"""
        styles = {
            "start": Style.BRIGHT,
            "end": Style.DIM,
            "handoff": Style.BRIGHT,
            "tool_start": "",
            "tool_end": Style.DIM,
        }
        return styles.get(event_type, "")

    async def on_start(self, context: RunContextWrapper, agent: Agent) -> None:
        self.event_counter += 1
        color = self._get_agent_color()
        style = self._get_event_style("start")
        print(f"{color}{style}### ({self.display_name}) {self.event_counter}: Agent {agent.name} started{Style.RESET_ALL}\n")

    async def on_end(self, context: RunContextWrapper, agent: Agent, output: Any) -> None:
        self.event_counter += 1
        color = self._get_agent_color()
        style = self._get_event_style("end")
        print(
            f"{color}{style}### ({self.display_name}) {self.event_counter}: Agent {agent.name} ended with output {output}{Style.RESET_ALL}\n"
        )

    async def on_handoff(self, context: RunContextWrapper, agent: Agent, source: Agent) -> None:
        self.event_counter += 1
        color = self._get_agent_color()
        style = self._get_event_style("handoff")
        print(
            f"{color}{style}### ({self.display_name}) {self.event_counter}: Agent {source.name} handed off to {agent.name}{Style.RESET_ALL}\n"
        )

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        self.event_counter += 1
        color = self._get_agent_color()
        style = self._get_event_style("tool_start")
        print(
            f"{color}{style}### ({self.display_name}) {self.event_counter}: Agent {agent.name} started tool {tool.name}{Style.RESET_ALL}\n"
        )

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        self.event_counter += 1
        color = self._get_agent_color()
        style = self._get_event_style("tool_end")
        print(
            f"{color}{style}### ({self.display_name}) {self.event_counter}: Agent {agent.name} ended tool {tool.name} with result {result}{Style.RESET_ALL}\n"
        )


class ResearchHooks(AgentHooks):
    def __init__(self):
        self.event_counter = 0

    def _publish_event(self, event_type: str, research_id: ObjectId, data: Dict[str, Any]) -> None:
        """Publish an event to Redis pub/sub channel"""
        event_data = {
            "event_type": event_type,
            "research_id": str(research_id),
            "timestamp": datetime.now().isoformat(),
            **data
        }
        
        if research := Research.find_by_id(research_id):
            research.update({'events': research.get('events', []) + [event_data]})
        else:
            print(f"Research with ID {research_id} not found")
        
        try:
            redis_events_pubsub_client.publish(f"research:{research_id}", json.dumps(event_data))
        except Exception as e:
            print(f"Failed to publish event to Redis: {e}")
            
        print(event_data)

    async def on_agent_start(self, context: RunContextWrapper[ResearchScopeContext], agent: Agent) -> None:
        self.event_counter += 1
        self._publish_event("agent_start", context.context.research_id, {
            "agent_name": agent.name,
            "counter": self.event_counter
        })

    async def on_agent_end(self, context: RunContextWrapper[ResearchScopeContext], agent: Agent, output: Any) -> None:
        self.event_counter += 1
        self._publish_event("agent_end", context.context.research_id, {
            "agent_name": agent.name,
            "output": str(output),
            "counter": self.event_counter
        })

    async def on_handoff(self, context: RunContextWrapper[ResearchScopeContext], agent: Agent, source: Agent) -> None:
        self.event_counter += 1
        self._publish_event("agent_handoff", context.context.research_id, {
            "from_agent": source.name,
            "to_agent": agent.name,
            "counter": self.event_counter
        })

    async def on_tool_start(self, context: RunContextWrapper[ResearchScopeContext], agent: Agent, tool: Tool) -> None:
        self.event_counter += 1
        self._publish_event("tool_start", context.context.research_id, {
            "agent_name": agent.name,
            "tool_name": tool.name,
            "counter": self.event_counter
        })

    async def on_tool_end(
        self, context: RunContextWrapper[ResearchScopeContext], agent: Agent, tool: Tool, result: Any
    ) -> None:
        self.event_counter += 1
        self._publish_event("tool_end", context.context.research_id, {
            "agent_name": agent.name,
            "tool_name": tool.name,
            "result": str(result), 
            "counter": self.event_counter
        })
    
    