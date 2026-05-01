from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from src.app.domain.user.enums import UserRole


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


class UserUpdate(BaseModel):
    role: UserRole = Field(..., example="USER")


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8)
