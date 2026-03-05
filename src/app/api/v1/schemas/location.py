from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    name: str = Field(..., example="A-1")
    note: Optional[str] = Field(None, example="First shelf on the left")


class LocationCreate(LocationBase):
    pass


class LocationUpdate(LocationBase):
    pass


class LocationRead(LocationBase):
    id: UUID
    created_at: datetime
    created_by: UUID
    updated_at: Optional[datetime] = None
    updated_by: Optional[UUID] = None

    class Config:
        from_attributes = True
