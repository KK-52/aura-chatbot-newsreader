from pydantic import BaseModel
from typing import Optional

class IngestRequest(BaseModel):
    url: str
    session_id: str

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3
    session_id: str
