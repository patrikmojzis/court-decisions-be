from typing import TYPE_CHECKING

from app.models.model_base import ModelBase

if TYPE_CHECKING:
    pass

class Keyword(ModelBase):

    research_id: str = None
    search_keyword: str = None
    analysed_results: int = None
    relevant_results: int = None

