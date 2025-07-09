from typing import TYPE_CHECKING, Optional

from app.models.model_base import ModelBase

if TYPE_CHECKING:
    pass


class ResearchTrace(ModelBase):

    research_id: str = None
    problem_description: str = None
    question: str = None
    search_keyword: str = None
    is_relevant: bool = False
    summary: str = None
    pdf_file_name: str = None
    relevant_parts: Optional[list[str]] = None
    legal_provisions: Optional[list[str]] = None
    metadata: Optional[str] = None


