from pydantic import BaseModel


class ResearchRequestSchema(BaseModel):
    message: str 