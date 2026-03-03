幫我根據以下需求建置基礎設施

python 版本 3.14.3，建立一個具有DDD架構的後端專案

1. 基於asyncio模組
2. 基於FastAPI
3. SQL ORM為SQLAlchemy並透過alembic 做初始化(請基於asyncio)
4. API Model請使用pydantic做驗證

docker

1. 使用最新版本的postgres
2. 先引入redis
3. 後端專案先不要寫入docker compose開發時直接透過host 連入 db or cache做開發

---
## 實作紀錄 (Status: Done)

### 1. 環境與專案初始化
- **Python**: 3.14.3 (via `uv`)
- **Web**: `fastapi`, `uvicorn`
- **DB**: `sqlalchemy[asyncio]`, `alembic`, `asyncpg`
- **Cache**: `redis` (asyncio)
- **Config**: `pydantic-settings`

### 2. DDD 架構目錄結構
- `src/app/domain/`: 領域模型與介面
- `src/app/application/`: 業務邏輯與 Use Cases
- `src/app/infrastructure/`: 資料庫、Redis 與外部服務實作
- `src/app/api/`: FastAPI 路由與 Schema
- `src/app/core/`: 全域設定 (config.py)

### 3. 關鍵基礎設施配置
- **Docker Compose**: 已建立 `postgres:latest` 與 `redis:latest`。
- **Database**: 
  - `src/app/infrastructure/database.py`: 非同步 Session 管理。
  - `src/app/infrastructure/base.py`: 統一的 SQLAlchemy Base 類別。
- **Alembic**: 已初始化並修改 `env.py` 支援 `asyncio` 及自動偵測模型。
- **Redis**: `src/app/infrastructure/redis.py` 提供非同步連線池。
- **Main App**: `src/app/main.py` 包含基礎路由與健康檢查。

### 4. 常用開發指令
- 啟動基礎設施: `docker-compose up -d`
- 啟動 API: `uv run uvicorn src.app.main:app --reload`
- 建立遷移檔案: `uv run alembic revision --autogenerate -m "description"`
- 執行遷移: `uv run alembic upgrade head`