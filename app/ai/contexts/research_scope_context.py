import uuid
from typing import Optional

from agents import RunContextWrapper, function_tool
from pydantic import BaseModel, Field


class ResearchScopeContext(BaseModel):
    research_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    problem_description: Optional[str] = None
    question: Optional[str] = None
    
    
@function_tool
async def set_research_scope(
    context: RunContextWrapper[ResearchScopeContext],
    problem_description: str,
    question: str,
) -> str:
    """
    Set the research scope context.
    """
    context.context.problem_description = problem_description
    context.context.question = question
    return "Research scope updated"