from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import redis.asyncio as redis
from src.app.core.config import settings

class Container(containers.DeclarativeContainer):
    # 這裡定義 Wiring 注入的範圍，讓 FastAPI 路由可以直接使用
    wiring_config = containers.WiringConfiguration(
        modules=[
            # "src.app.api.v1.endpoints",  # 暫時註解，等建立 v1 資料夾後再開啟
            "src.app.main",              # 包含入口點
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

    # 3. 領域模型與應用服務 (範例)
    # 以後你會在這裡註冊 Repository 或 UseCase
    # repository = providers.Factory(
    #     UserRepository,
    #     session=session_factory
    # )
