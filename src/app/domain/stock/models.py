from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy import (
    BigInteger,
    Text,
    Enum as SAEnum,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Index,
    UUID as UUID_TYPE,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.app.infrastructure.base import BaseAuditModel
from src.app.domain.stock.enums import StockMovementType


class StockBalance(BaseAuditModel):
    """item × location 的即時存量快取，由流水帳更新時同步維護。"""

    __tablename__ = "stock_balances"

    id: Mapped[UUID] = mapped_column(
        UUID_TYPE(as_uuid=True), primary_key=True, default=uuid4
    )
    item_id: Mapped[UUID] = mapped_column(
        UUID_TYPE(as_uuid=True), ForeignKey("items.id"), nullable=False
    )
    location_id: Mapped[UUID] = mapped_column(
        UUID_TYPE(as_uuid=True), ForeignKey("locations.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint(
            "item_id", "location_id", name="uq_stock_balances_item_location"
        ),
        CheckConstraint("quantity >= 0", name="ck_stock_balances_non_negative"),
    )


class StockMovement(BaseAuditModel):
    """庫存異動流水帳（append-only）。"""

    __tablename__ = "stock_movements"

    id: Mapped[UUID] = mapped_column(
        UUID_TYPE(as_uuid=True), primary_key=True, default=uuid4
    )
    item_id: Mapped[UUID] = mapped_column(
        UUID_TYPE(as_uuid=True), ForeignKey("items.id"), nullable=False
    )
    location_id: Mapped[UUID] = mapped_column(
        UUID_TYPE(as_uuid=True), ForeignKey("locations.id"), nullable=False
    )
    movement_type: Mapped[StockMovementType] = mapped_column(
        SAEnum(StockMovementType, name="stockmovementtype"), nullable=False
    )
    # 異動量：入庫為正、出庫為負；ADJUST 兩者皆可（盤點調整）
    change_qty: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # 異動後當下存量，方便對帳與時間序列查詢
    quantity_after: Mapped[int] = mapped_column(BigInteger, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index(
            "ix_stock_movements_item_loc_time",
            "item_id",
            "location_id",
            "created_at",
        ),
        CheckConstraint("change_qty <> 0", name="ck_stock_movements_nonzero"),
    )
