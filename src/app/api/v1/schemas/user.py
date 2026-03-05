from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
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
