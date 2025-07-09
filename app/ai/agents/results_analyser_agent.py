from typing import Optional

from agents import Agent
from pydantic import BaseModel, Field

from app.ai.contexts.research_scope_context import ResearchScopeContext
from app.ai.prompts.agents_prompts import RESULTS_ANALYSER_PROMPT
from app.utils.agent_utils import PrintHooks


class ResultsAnalyserResult(BaseModel):
    pdf_file_names: Optional[list[str]] = Field(None, description="List of PDF file names from metadata->file_name")


results_analyser_agent = Agent[ResearchScopeContext](
    name="results_analyser_agent",
    instructions=RESULTS_ANALYSER_PROMPT,
    output_type=ResultsAnalyserResult,
    hooks=PrintHooks("Results Analyser Agent"),
    model="o4-mini"
)
