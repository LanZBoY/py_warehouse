from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from src.app.domain.item.models import Item


class ItemRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def get_by_id(self, item_id: UUID) -> Optional[Item]:
        async with self._session_factory() as session:
            result = await session.execute(select(Item).where(Item.id == item_id))
            return result.scalar_one_or_none()

    async def get_list(self, skip: int = 0, limit: int = 10) -> tuple[List[Item], int]:
        async with self._session_factory() as session:
            total_result = await session.execute(select(func.count()).select_from(Item))
            total = total_result.scalar_one()

            result = await session.execute(
                select(Item).offset(skip).limit(limit).order_by(Item.created_at.desc())
            )
            items = result.scalars().all()
            return list(items), total

    async def create(self, item: Item) -> Item:
        async with self._session_factory() as session:
            session.add(item)
            await session.commit()
            await session.refresh(item)
            return item

    async def update(self, item: Item) -> Item:
        async with self._session_factory() as session:
            await session.merge(item)
            await session.commit()
            return item

    async def delete(self, item: Item) -> None:
        async with self._session_factory() as session:
            await session.delete(item)
            await session.commit()
