from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy import String, Text, UUID as UUID_TYPE
from sqlalchemy.orm import Mapped, mapped_column
from src.app.infrastructure.base import BaseAuditModel


class Item(BaseAuditModel):
    __tablename__ = "items"

    id: Mapped[UUID] = mapped_column(
        UUID_TYPE(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
