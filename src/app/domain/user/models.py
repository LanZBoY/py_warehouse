from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import String, Enum, UUID as UUID_TYPE, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from src.app.infrastructure.base import BaseAuditModel
from src.app.domain.user.enums import UserRole


class User(BaseAuditModel):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID_TYPE(as_uuid=True), primary_key=True)
    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    password_with_salt: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False, default=UserRole.USER
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
