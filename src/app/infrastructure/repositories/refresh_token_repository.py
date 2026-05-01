from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.app.domain.user.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        async with self._session_factory() as session:
            session.add(refresh_token)
            await session.commit()
            await session.refresh(refresh_token)
            return refresh_token

    async def get_active_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """取仍有效（未撤銷且未過期）的 refresh token。"""
        async with self._session_factory() as session:
            result = await session.execute(
                select(RefreshToken).where(
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.revoked_at.is_(None),
                    RefreshToken.expires_at > datetime.now(timezone.utc),
                )
            )
            return result.scalar_one_or_none()

    async def revoke(self, token_hash: str) -> bool:
        """撤銷單一 refresh token；回傳是否實際更新到資料列。"""
        async with self._session_factory() as session:
            result = await session.execute(
                update(RefreshToken)
                .where(
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.revoked_at.is_(None),
                )
                .values(revoked_at=datetime.now(timezone.utc))
            )
            await session.commit()
            return result.rowcount > 0

    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """撤銷使用者所有未撤銷的 refresh token，回傳影響筆數。"""
        async with self._session_factory() as session:
            result = await session.execute(
                update(RefreshToken)
                .where(
                    RefreshToken.user_id == user_id,
                    RefreshToken.revoked_at.is_(None),
                )
                .values(revoked_at=datetime.now(timezone.utc))
            )
            await session.commit()
            return result.rowcount
