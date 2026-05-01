from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class LoginRequest(BaseModel):
    username: str = Field(..., example="admin")
    password: str = Field(..., example="admin123")


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenPayload(BaseModel):
    sub: UUID  # User ID
    username: str
    role: str
    exp: Optional[int] = None
    type: Optional[str] = None
