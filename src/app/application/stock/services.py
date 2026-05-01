from uuid import UUID
from typing import List, Optional, Tuple

from src.app.infrastructure.repositories.stock_repository import StockRepository
from src.app.domain.stock.enums import StockMovementType
from src.app.api.v1.schemas.stock import StockBalanceRead, StockMovementRead


class StockService:
    def __init__(self, stock_repo: StockRepository):
        self._stock_repo = stock_repo

    async def get_balance(
        self, item_id: UUID, location_id: UUID
    ) -> Optional[StockBalanceRead]:
        balance = await self._stock_repo.get_balance(item_id, location_id)
        if not balance:
            return None
        return StockBalanceRead.model_validate(balance)

    async def list_balances(
        self,
        skip: int = 0,
        limit: int = 10,
        item_id: Optional[UUID] = None,
        location_id: Optional[UUID] = None,
    ) -> Tuple[List[StockBalanceRead], int]:
        balances, total = await self._stock_repo.list_balances(
            skip=skip, limit=limit, item_id=item_id, location_id=location_id
        )
        return [StockBalanceRead.model_validate(b) for b in balances], total

    async def list_movements(
        self,
        skip: int = 0,
        limit: int = 10,
        item_id: Optional[UUID] = None,
        location_id: Optional[UUID] = None,
    ) -> Tuple[List[StockMovementRead], int]:
        movements, total = await self._stock_repo.list_movements(
            skip=skip, limit=limit, item_id=item_id, location_id=location_id
        )
        return [StockMovementRead.model_validate(m) for m in movements], total

    async def inbound(
        self,
        item_id: UUID,
        location_id: UUID,
        quantity: int,
        note: Optional[str],
        user_id: UUID,
    ) -> Tuple[StockBalanceRead, StockMovementRead]:
        balance, movement = await self._stock_repo.apply_movement(
            item_id=item_id,
            location_id=location_id,
            change_qty=quantity,
            movement_type=StockMovementType.INBOUND,
            note=note,
            user_id=user_id,
        )
        return (
            StockBalanceRead.model_validate(balance),
            StockMovementRead.model_validate(movement),
        )

    async def outbound(
        self,
        item_id: UUID,
        location_id: UUID,
        quantity: int,
        note: Optional[str],
        user_id: UUID,
    ) -> Tuple[StockBalanceRead, StockMovementRead]:
        balance, movement = await self._stock_repo.apply_movement(
            item_id=item_id,
            location_id=location_id,
            change_qty=-quantity,
            movement_type=StockMovementType.OUTBOUND,
            note=note,
            user_id=user_id,
        )
        return (
            StockBalanceRead.model_validate(balance),
            StockMovementRead.model_validate(movement),
        )

    async def adjust(
        self,
        item_id: UUID,
        location_id: UUID,
        target_quantity: int,
        note: Optional[str],
        user_id: UUID,
    ) -> Optional[Tuple[StockBalanceRead, StockMovementRead]]:
        """盤點調整：以差異量寫一筆 ADJUST 流水。差為 0 時不動作。"""
        current = await self._stock_repo.get_balance(item_id, location_id)
        current_qty = current.quantity if current else 0
        delta = target_quantity - current_qty
        if delta == 0:
            return None

        balance, movement = await self._stock_repo.apply_movement(
            item_id=item_id,
            location_id=location_id,
            change_qty=delta,
            movement_type=StockMovementType.ADJUST,
            note=note,
            user_id=user_id,
        )
        return (
            StockBalanceRead.model_validate(balance),
            StockMovementRead.model_validate(movement),
        )
