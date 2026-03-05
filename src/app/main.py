from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from src.app.core.config import settings
from src.app.core.container import Container
from src.app.api.v1.endpoints.user import router as user_router
from src.app.api.v1.endpoints.auth import router as auth_router
from src.app.api.v1.endpoints.item import router as item_router
from src.app.api.v1.endpoints.location import router as location_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化 DI 容器
    container = Container()
    app.container = container

    # 初始化資源 (例如非同步 DB 連線)
    # await container.init_resources()

    yield

    # 關閉資源
    # await container.shutdown_resources()


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# 掛載路由
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(item_router, prefix="/api/v1/items", tags=["Items"])
app.include_router(location_router, prefix="/api/v1/locations", tags=["Locations"])


@app.get("/")
async def root():
    return RedirectResponse(url="/docs", status_code=301)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
