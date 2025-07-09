from agents import Agent, RunContextWrapper, Runner, function_tool

from app.ai.contexts.research_scope_context import ResearchScopeContext
from app.ai.prompts.agents_prompts import KEYWORD_GENERATOR_PROMPT
from app.models.keyword_model import Keyword
from app.models.research_trace_model import ResearchTrace
from app.utils.agent_utils import PrintHooks
from app.utils.research_utils import research_event

keyword_agent = Agent[ResearchScopeContext](
    name="keyword_agent",
    instructions=KEYWORD_GENERATOR_PROMPT,
    hooks=PrintHooks("Keyword Agent"),
    model="o4-mini"
)


@function_tool
async def spawn_keyword_agent(context: RunContextWrapper[ResearchScopeContext], instructions: str) -> str:
    """
    Spawn a keyword agent that can generate keywords for a research problem.
    """
    research_event(context.context.research_id, "planning")
    
    res = ResearchTrace.find({'research_id': context.context.research_id, 'is_relevant': True})
    research_history = [
        {
            'search_keyword': doc.get('search_keyword'),
            'relevant_parts': doc.get('relevant_parts'),
            'legal_provisions': doc.get('legal_provisions')
        }
        for doc in res
    ] if res else "No relevant results found"
    
    keyword_history = Keyword.find({'research_id': context.context.research_id})
    keyword_history = [
        {
            'search_keyword': doc.get('search_keyword'),
            'analysed_results': doc.get('analysed_results'),
            'relevant_results': doc.get('relevant_results'),
        }
        for doc in keyword_history
    ] if keyword_history else "No keyword history yet"
    
    res = await Runner.run(
        starting_agent=keyword_agent,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": context.context.model_dump_json(exclude={'research_id'})
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Relevant court cases: {research_history}"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Keyword history: {keyword_history}"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": instructions
                    }
                ]
            }
        ],
        context=context.context,
    )
    
    return res.final_output