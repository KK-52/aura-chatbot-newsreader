from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class IngestRequest(BaseModel):
    url: str
    session_id: Optional[str] = None # Optional, will use username if authenticated

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3
    session_id: Optional[str] = None # Optional, will use username if authenticated
