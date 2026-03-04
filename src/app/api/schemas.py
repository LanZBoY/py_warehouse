from typing import Generic, TypeVar, List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from src.app.domain.user.enums import UserRole

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    data: T

class ListResponse(BaseModel, Generic[T]):
    total: int
    data: List[T]

class LoginRequest(BaseModel):
    username: str = Field(..., example="admin")
    password: str = Field(..., example="admin123")

class UserRead(BaseModel):
    id: UUID
    username: str
    role: UserRole
    created_at: datetime
    created_by: UUID
    updated_at: Optional[datetime] = None
    updated_by: Optional[UUID] = None

    class Config:
        from_attributes = True
