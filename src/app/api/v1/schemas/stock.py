from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from src.app.domain.stock.enums import StockMovementType


class StockBalanceRead(BaseModel):
    id: UUID
    item_id: UUID
    location_id: UUID
    quantity: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StockMovementRead(BaseModel):
    id: UUID
    item_id: UUID
    location_id: UUID
    movement_type: StockMovementType
    change_qty: int
    quantity_after: int
    note: Optional[str] = None
    created_at: datetime
    created_by: UUID

    class Config:
        from_attributes = True


class StockMovementCreate(BaseModel):
    """入庫 / 出庫共用：quantity 為正整數，伺服器依路由決定方向。"""

    item_id: UUID
    location_id: UUID
    quantity: int = Field(..., gt=0, description="異動數量（正整數）")
    note: Optional[str] = Field(None, example="採購入庫 PO-1234")


class StockAdjustCreate(BaseModel):
    """盤點調整：直接給目標總量，由伺服器算差異。"""

    item_id: UUID
    location_id: UUID
    target_quantity: int = Field(..., ge=0, description="盤點後的目標總量")
    note: Optional[str] = Field(None, example="月底盤點調整")
