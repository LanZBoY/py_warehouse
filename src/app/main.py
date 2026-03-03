from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.app.core.config import settings
from src.app.core.container import Container


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


@app.get("/")
async def root():
    return {"message": "Welcome to PyWarehouse API"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
