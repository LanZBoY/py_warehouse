# PyWarehouse

一個基於 Domain-Driven Design (DDD) 原則建構的現代化倉庫管理系統 API。

## 🚀 開發環境 Setup

> 以下指令皆於 **專案根目錄** (`py_warehouse/`) 執行。

### 1. 環境準備
請先安裝：
- [uv](https://github.com/astral-sh/uv)（Python 套件 / 虛擬環境管理）
- Docker 與 Docker Compose

### 2. 設定環境變數
將範本複製成 `.env`，並依需要修改：

```bash
cp .env.example .env
```

`.env` 是 **單一來源**，同時被以下兩處讀取：
- `docker-compose.yml`：`POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB`（建立 Postgres container 用）
- `src/app/core/config.py`：`DATABASE_URL` / `REDIS_URL` / `SECRET_KEY` 等（FastAPI 與 Alembic 用）

> ⚠️ `DATABASE_URL` 的帳密務必與 `POSTGRES_USER` / `POSTGRES_PASSWORD` 一致，否則 app 連不上 DB。

### 3. 安裝相依套件
```bash
uv sync
```

啟用虛擬環境（可選；用 `uv run` 不需要先啟用）：
```bash
source .venv/bin/activate
```

### 4. 啟動基礎設施 (Postgres + Redis)
```bash
docker compose up -d
```

如果之前已有舊 volume 帳密對不上，加 `-v` 重建：
```bash
docker compose down -v && docker compose up -d
```

### 5. 執行資料庫遷移
```bash
uv run alembic upgrade head
```

常用 Alembic 指令：
```bash
uv run alembic revision --autogenerate -m "your message"  # 依 models 自動產生 migration
uv run alembic upgrade head                                # 套用至最新版本
uv run alembic downgrade -1                                # 倒回上一版
uv run alembic current                                     # 查看目前版本
uv run alembic history                                     # 查看歷史
```

### 6. 啟動 API 服務 (開發模式)
```bash
uv run uvicorn src.app.main:app --reload
```

- API 文件 (Swagger)：<http://127.0.0.1:8000/docs>
- Health check：<http://127.0.0.1:8000/health>

### 7. 預設管理員帳號
首次啟動會依 `.env` 的 `ROOT_USER_NAME` / `ROOT_USER_PASSWORD` 建立 root admin，可用 `POST /api/v1/auth/login` 登入取得 JWT。

---

## 🛠 開發習慣與規範

本專案遵循嚴格的工程實踐。

### 1. 架構設計 (DDD)
*   **Domain**: 核心業務邏輯與實體（`src/app/domain`，目前包含 `user` / `item` / `location` / `stock`）。
*   **Application**: 應用服務與 DTO 轉換（`src/app/application`）。
*   **Infrastructure**: 資料庫實作與外部資源（`src/app/infrastructure`）。
*   **API**: FastAPI 路由與 Schema 定義（`src/app/api`）。

### 2. 資料處理標準
*   **DTO 優先**: Service 層必須將 SQLAlchemy ORM 物件轉換為 Pydantic DTO 後再回傳，以實現層級隔離並避免 `DetachedInstanceError`。
*   **UTC DateTime**: 
    - 程式碼一律使用 `datetime.now(timezone.utc)`。
    - 資料庫欄位一律為 `TIMESTAMP WITH TIME ZONE`。
*   **型別標註**: 所有函式與類別屬性必須標註型別，提升可讀性與安全性。

### 3. 安全與認證
*   **密碼**: 使用原生 `bcrypt` 進行雜湊（不建議使用已廢棄的 passlib 內部方法）。
*   **認證**: JWT access token + refresh token rotation，登出時撤銷 refresh token；API 支援 Bearer Token 自動帶入（Swagger HTTPBearer）。
*   **CORS**: 預設允許前端開發伺服器來源，正式環境請於 `.env` 調整。

---

## 📜 開發歷程 (Implementation History)

1.  **專案初始化**: 建立基礎 DDD 目錄結構與 Dependency Injector 配置。
2.  **基礎設施建置**: 整合 SQLAlchemy (Async) 與 Redis，解決 Postgres 18+ Docker 掛載相容性問題。
3.  **使用者系統實作**:
    - 實作帶有審計欄位的 `BaseAuditModel`。
    - 建立 `User` 模型與 Alembic 遷移邏輯。
    - 初始化 Root User (全零 UUID, Admin 權限)。
    - 擴充 CRUD：軟刪除、密碼變更端點。
4.  **API 演進**:
    - 建立通用的 `BaseResponse` 與 `ListResponse` 規範。
    - 實作 JSON 格式登入 API 並分離 Auth/Users 標籤。
    - 抽離安全相依項目 (`dependencies.py`) 供全域使用。
5.  **核心倉儲領域**:
    - `Item` / `Location` CRUD 與 Service 層回傳 DTO 重構。
    - `Stock`：以原子異動紀錄 (movement log) 追蹤 item × location 的庫存平衡。
6.  **認證強化**: Refresh token rotation 與登出撤銷機制。
7.  **前後端整合**: 開放前端開發伺服器 CORS 來源。

---

## 📝 技術筆記 (Deep Dives)
更多技術細節請參考 `Note/` 目錄：
*   [Service 層回傳 DTO 策略](Note/service_layer_dto_strategy.md)
*   [SQLAlchemy 型別標註與預設值](Note/sqlalchemy_typing_and_defaults.md)
*   [快取策略](Note/caching_strategy.md)
*   [相依注入研究](Note/dependency_injection_study.md)
*   [Python 路徑與執行機制](Note/python_path_and_execution.md)
