from pydantic import BaseModel

class LiveRAG(BaseModel):
    query: str
    top_k: int = 1
    score_threshold: float