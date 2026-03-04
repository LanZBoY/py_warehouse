from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import redis.asyncio as redis
from src.app.core.config import settings
from src.app.infrastructure.repositories.user_repository import UserRepository
from src.app.application.user.services import AuthService, UserService

class Container(containers.DeclarativeContainer):
    # 這裡定義 Wiring 注入的範圍，讓 FastAPI 路由可以直接使用
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.app.api.v1.endpoints.auth",  # 認證路由
            "src.app.api.v1.endpoints.user",  # 使用者管理路由
            "src.app.main",                   # 包含入口點
        ]
    )

    # 1. 基礎設施資源 (Database)
    engine = providers.Singleton(
        create_async_engine,
        url=settings.DATABASE_URL,
        echo=True
    )

    session_factory = providers.Singleton(
        async_sessionmaker,
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # 2. 基礎設施資源 (Redis)
    redis_pool = providers.Resource(
        redis.from_url,
        url=settings.REDIS_URL,
        decode_responses=True
    )

    # 3. Repository
    user_repository = providers.Factory(
        UserRepository,
        session_factory=session_factory
    )

    # 4. Application Services
    auth_service = providers.Factory(
        AuthService,
        user_repo=user_repository
    )
    
    user_service = providers.Factory(
        UserService,
        user_repo=user_repository
    )
