import uuid
from datetime import timedelta
from typing import List, Optional
from src.app.domain.user.models import User
from src.app.domain.user.enums import UserRole
from src.app.infrastructure.repositories.user_repository import UserRepository
from src.app.core.security.auth import (
    verify_password,
    create_access_token,
    hash_password,
)
from src.app.api.v1.schemas.user import UserRead


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def authenticate(self, username: str, password: str) -> Optional[str]:
        user = await self._user_repo.get_by_username(username)
        if not user or not verify_password(password, user.password_with_salt):
            return None

        # 建立 JWT Token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role}
        )
        return access_token


class UserService:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def get_users(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[list[UserRead], int]:
        users, total = await self._user_repo.get_list(skip, limit)
        # 在 Service 層完成型別轉換，確保回傳的是純資料物件
        return [UserRead.model_validate(u) for u in users], total

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
