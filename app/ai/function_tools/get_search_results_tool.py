from agents import RunContextWrapper, function_tool

from app.ai.contexts.research_scope_context import ResearchScopeContext
from app.models.research_trace_model import ResearchTrace
from app.utils.research_utils import research_event


@function_tool
async def get_research_results(context: RunContextWrapper[ResearchScopeContext]) -> list[dict] | str:
    """
    Get the research result for a given research ID.
    """
    research_event(context.context.research_id, "planning")
    res = ResearchTrace.find({'research_id': context.context.research_id})
    
    if not res:
        return "No relevant results found"
    
    return [
        {
            'search_keyword': doc.search_keyword,
            'metadata': doc.metadata,
            'pdf_file_name': doc.pdf_file_name,
            'summary': doc.summary,
            'relevant_parts': doc.relevant_parts,
            'legal_provisions': doc.legal_provisions
        }
        for doc in res
    ]