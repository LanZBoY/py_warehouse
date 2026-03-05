from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    name: str = Field(..., example="Apple")
    note: Optional[str] = Field(None, example="Green apple from Japan")


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: UUID
    created_at: datetime
    created_by: UUID
    updated_at: Optional[datetime] = None
    updated_by: Optional[UUID] = None

    class Config:
        from_attributes = True
