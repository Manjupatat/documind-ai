
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    question: str = Field(min_length=3)
    document_id: str | None = None
    top_k: int = Field(default=3, ge=1, le=10)

class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list[dict]