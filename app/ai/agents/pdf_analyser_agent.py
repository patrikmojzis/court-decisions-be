

from typing import Optional

from agents import Agent
from pydantic import BaseModel, Field

from app.ai.contexts.research_scope_context import ResearchScopeContext
from app.ai.prompts.agents_prompts import PDF_ANALYSER_PROMPT
from app.utils.agent_utils import PrintHooks


class PDFAnalyserResult(BaseModel):
    metadata: str = Field(..., description="Court, case number, date")
    summary: str = Field(..., description="One sentence summary of matter of the case")
    is_relevant: bool = Field(..., description="Whether the PDF is relevant to the research scope")
    relevant_parts: Optional[list[str]] = Field(None, description="Word by word if apply")
    legal_provisions: Optional[list[str]] = Field(None, description="Linked legal provisions (e.g. § 195 of the Labour Code) related to the scope, if pdf relevant, else None")
    

pdf_analyser_agent = Agent[ResearchScopeContext](
    name="pdf_analyser_agent",
    instructions=PDF_ANALYSER_PROMPT,
    output_type=PDFAnalyserResult,
    hooks=PrintHooks("PDF Analyser Agent"),
    model="gpt-4.1"
)