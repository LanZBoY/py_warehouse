import uuid
from typing import Optional, Tuple
from src.app.domain.user.models import User
from src.app.domain.user.enums import UserRole
from src.app.domain.user.refresh_token import RefreshToken
from src.app.infrastructure.repositories.user_repository import UserRepository
from src.app.infrastructure.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from src.app.core.security.auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
)
from src.app.api.v1.schemas.user import UserRead


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        refresh_token_repo: RefreshTokenRepository,
    ):
        self._user_repo = user_repo
        self._refresh_token_repo = refresh_token_repo

    async def authenticate(
        self, username: str, password: str
    ) -> Optional[Tuple[str, str]]:
        """登入並簽發 (access_token, refresh_token)。失敗回傳 None。"""
        user = await self._user_repo.get_by_username(username)
        if not user or not verify_password(password, user.password_with_salt):
            return None

        return await self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> Optional[Tuple[str, str]]:
        """以 refresh token 換一組新的 (access, refresh)；rotation：舊的撤銷。

        若 token 不存在 / 已撤銷 / 已過期，回傳 None。
        """
        token_hash = hash_refresh_token(refresh_token)
        record = await self._refresh_token_repo.get_active_by_hash(token_hash)
        if not record:
            return None

        user = await self._user_repo.get_by_id(record.user_id)
        if not user:
            # user 已被軟刪：撤銷這條 chain
            await self._refresh_token_repo.revoke(token_hash)
            return None

        # rotation：先撤銷舊的，再簽新的
        await self._refresh_token_repo.revoke(token_hash)
        return await self._issue_tokens(user)

    async def logout(self, refresh_token: str) -> bool:
        """撤銷指定的 refresh token；access token 因短 TTL 自然過期。"""
        token_hash = hash_refresh_token(refresh_token)
        return await self._refresh_token_repo.revoke(token_hash)

    async def _issue_tokens(self, user: User) -> Tuple[str, str]:
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role}
        )
        plain, token_hash, expires_at = create_refresh_token()
        await self._refresh_token_repo.create(
            RefreshToken(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expires_at,
            )
        )
        return access_token, plain


class UserService:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def get_users(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[list[UserRead], int]:
        users, total = await self._user_repo.get_list(skip, limit)
        return [UserRead.model_validate(u) for u in users], total

    async def get_user(self, user_id: uuid.UUID) -> Optional[UserRead]:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            return None
        return UserRead.model_validate(user)

    async def create_user(
        self, username: str, password: str, creator_id: uuid.UUID
    ) -> UserRead:
        hashed_pw = hash_password(password)
        new_user = User(
            id=uuid.uuid4(),
            username=username,
            password_with_salt=hashed_pw,
            role=UserRole.USER,
            created_by=creator_id,
        )
        created_user = await self._user_repo.create(new_user)
        return UserRead.model_validate(created_user)

    async def update_role(
        self, user_id: uuid.UUID, role: UserRole, updater_id: uuid.UUID
    ) -> Optional[UserRead]:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            return None
        user.role = role
        user.updated_by = updater_id
        updated = await self._user_repo.update(user)
        return UserRead.model_validate(updated)

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            return False
        await self._user_repo.soft_delete(user)
        return True

    async def change_password(
        self, user_id: uuid.UUID, old_password: str, new_password: str
    ) -> bool:
        """使用者改自己密碼，需驗證舊密碼。"""
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            return False
        if not verify_password(old_password, user.password_with_salt):
            return False
        user.password_with_salt = hash_password(new_password)
        user.updated_by = user_id
        await self._user_repo.update(user)
        return True

    async def reset_password(
        self, user_id: uuid.UUID, new_password: str, updater_id: uuid.UUID
    ) -> bool:
        """管理員重設他人密碼，不需舊密碼。"""
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            return False
        user.password_with_salt = hash_password(new_password)
        user.updated_by = updater_id
        await self._user_repo.update(user)
        return True
