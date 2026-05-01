from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.app.domain.stock.models import StockBalance, StockMovement
from src.app.domain.stock.enums import StockMovementType
from src.app.domain.stock.exceptions import InsufficientStockError


class StockRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def get_balance(
        self, item_id: UUID, location_id: UUID
    ) -> Optional[StockBalance]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(StockBalance).where(
                    StockBalance.item_id == item_id,
                    StockBalance.location_id == location_id,
                )
            )
            return result.scalar_one_or_none()

    async def list_balances(
        self,
        skip: int = 0,
        limit: int = 10,
        item_id: Optional[UUID] = None,
        location_id: Optional[UUID] = None,
    ) -> Tuple[List[StockBalance], int]:
        async with self._session_factory() as session:
            base = select(StockBalance)
            if item_id is not None:
                base = base.where(StockBalance.item_id == item_id)
            if location_id is not None:
                base = base.where(StockBalance.location_id == location_id)

            total_result = await session.execute(
                select(func.count()).select_from(base.subquery())
            )
            total = total_result.scalar_one()

            result = await session.execute(
                base.offset(skip)
                .limit(limit)
                .order_by(StockBalance.updated_at.desc().nullslast())
            )
            return list(result.scalars().all()), total

    async def list_movements(
        self,
        skip: int = 0,
        limit: int = 10,
        item_id: Optional[UUID] = None,
        location_id: Optional[UUID] = None,
    ) -> Tuple[List[StockMovement], int]:
        async with self._session_factory() as session:
            base = select(StockMovement)
            if item_id is not None:
                base = base.where(StockMovement.item_id == item_id)
            if location_id is not None:
                base = base.where(StockMovement.location_id == location_id)

            total_result = await session.execute(
                select(func.count()).select_from(base.subquery())
            )
            total = total_result.scalar_one()

            result = await session.execute(
                base.offset(skip)
                .limit(limit)
                .order_by(StockMovement.created_at.desc())
            )
            return list(result.scalars().all()), total

    async def apply_movement(
        self,
        item_id: UUID,
        location_id: UUID,
        change_qty: int,
        movement_type: StockMovementType,
        note: Optional[str],
        user_id: UUID,
    ) -> Tuple[StockBalance, StockMovement]:
        """單一交易內：upsert balance、鎖列、寫流水、更新存量。"""
        if change_qty == 0:
            raise ValueError("change_qty must be non-zero")

        async with self._session_factory() as session:
            async with session.begin():
                # 確保 balance row 存在（concurrent insert 由 unique constraint 防護）
                await session.execute(
                    pg_insert(StockBalance)
                    .values(
                        id=uuid4(),
                        item_id=item_id,
                        location_id=location_id,
                        quantity=0,
                        created_by=user_id,
                    )
                    .on_conflict_do_nothing(
                        index_elements=["item_id", "location_id"]
                    )
                )

                # 鎖定 balance row 進行扣減/加總
                balance = (
                    await session.execute(
                        select(StockBalance)
                        .where(
                            StockBalance.item_id == item_id,
                            StockBalance.location_id == location_id,
                        )
                        .with_for_update()
                    )
                ).scalar_one()

                new_qty = balance.quantity + change_qty
                if new_qty < 0:
                    raise InsufficientStockError(
                        item_id=item_id,
                        location_id=location_id,
                        current=balance.quantity,
                        requested=-change_qty,
                    )

                balance.quantity = new_qty
                balance.updated_by = user_id

                movement = StockMovement(
                    id=uuid4(),
                    item_id=item_id,
                    location_id=location_id,
                    movement_type=movement_type,
                    change_qty=change_qty,
                    quantity_after=new_qty,
                    note=note,
                    created_by=user_id,
                )
                session.add(movement)
                await session.flush()

            await session.refresh(balance)
            await session.refresh(movement)
            return balance, movement
