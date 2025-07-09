from agents import Agent, WebSearchTool
from openai.types.responses.web_search_tool_param import UserLocation

from app.ai.contexts.research_scope_context import ResearchScopeContext
from app.ai.prompts.agents_prompts import LAW_AGENT_PROMPT
from app.utils.agent_utils import PrintHooks

law_agent = Agent[ResearchScopeContext](
    name="law_agent",
    instructions=LAW_AGENT_PROMPT,
    hooks=PrintHooks("Law Agent"),
    tools=[
        WebSearchTool(
            user_location=UserLocation(
                type="approximate",
                city="Bratislava",
                country="SK",
            )
        )
    ]
)