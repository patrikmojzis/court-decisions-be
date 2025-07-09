from agents import Agent

from app.ai.agents.keyword_agent import spawn_keyword_agent
from app.ai.agents.report_agent import spawn_report_agent
from app.ai.contexts.research_scope_context import ResearchScopeContext, set_research_scope
from app.ai.function_tools.get_search_results_tool import get_research_results
from app.ai.function_tools.search_results_tool import search_results
from app.ai.prompts.agents_prompts import ORCHESTRATOR_PROMPT
from app.utils.agent_utils import PrintHooks

orchestrator_agent = Agent[ResearchScopeContext](
    name="orchestrator_agent",
    instructions=ORCHESTRATOR_PROMPT,
    tools=[
        set_research_scope,
        spawn_keyword_agent,
        search_results,
        get_research_results,
        spawn_report_agent,
    ],
    hooks=PrintHooks("Orchestrator Agent"),
    model="o4-mini"
)