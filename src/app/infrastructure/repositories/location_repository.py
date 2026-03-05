from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from src.app.domain.location.models import Location


class LocationRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def get_by_id(self, location_id: UUID) -> Optional[Location]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(Location).where(Location.id == location_id)
            )
            return result.scalar_one_or_none()

    async def get_list(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[List[Location], int]:
        async with self._session_factory() as session:
            total_result = await session.execute(
                select(func.count()).select_from(Location)
            )
            total = total_result.scalar_one()

            result = await session.execute(
                select(Location)
                .offset(skip)
                .limit(limit)
                .order_by(Location.created_at.desc())
            )
            locations = result.scalars().all()
            return list(locations), total

    async def create(self, location: Location) -> Location:
        async with self._session_factory() as session:
            session.add(location)
            await session.commit()
            await session.refresh(location)
            return location

    async def update(self, location: Location) -> Location:
        async with self._session_factory() as session:
            await session.merge(location)
            await session.commit()
            return location

    async def delete(self, location: Location) -> None:
        async with self._session_factory() as session:
            await session.delete(location)
            await session.commit()
