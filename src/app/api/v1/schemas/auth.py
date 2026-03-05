from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class LoginRequest(BaseModel):
    username: str = Field(..., example="admin")
    password: str = Field(..., example="admin123")


class TokenPayload(BaseModel):
    sub: UUID  # User ID
    username: str
    role: str
    exp: Optional[int] = None
