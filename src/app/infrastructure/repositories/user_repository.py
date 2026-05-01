from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from src.app.domain.user.models import User


class UserRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(User).where(User.id == user_id, User.deleted_at.is_(None))
            )
            return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(User).where(
                    User.username == username, User.deleted_at.is_(None)
                )
            )
            return result.scalar_one_or_none()

    async def get_list(self, skip: int = 0, limit: int = 10) -> tuple[List[User], int]:
        async with self._session_factory() as session:
            total_result = await session.execute(
                select(func.count())
                .select_from(User)
                .where(User.deleted_at.is_(None))
            )
            total = total_result.scalar_one()

            result = await session.execute(
                select(User)
                .where(User.deleted_at.is_(None))
                .offset(skip)
                .limit(limit)
                .order_by(User.created_at.desc())
            )
            users = result.scalars().all()
            return list(users), total

    async def create(self, user: User) -> User:
        async with self._session_factory() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def update(self, user: User) -> User:
        async with self._session_factory() as session:
            merged = await session.merge(user)
            await session.commit()
            await session.refresh(merged)
            return merged

    async def soft_delete(self, user: User) -> None:
        async with self._session_factory() as session:
            user.deleted_at = datetime.now(timezone.utc)
            await session.merge(user)
            await session.commit()
