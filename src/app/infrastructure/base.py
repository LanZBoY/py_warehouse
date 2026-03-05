from datetime import datetime
from uuid import UUID
from typing import Optional
from sqlalchemy import DateTime, UUID as UUID_TYPE
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class BaseAuditModel(Base):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    created_by: Mapped[UUID] = mapped_column(UUID_TYPE(as_uuid=True), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    updated_by: Mapped[Optional[UUID]] = mapped_column(
        UUID_TYPE(as_uuid=True), nullable=True
    )
