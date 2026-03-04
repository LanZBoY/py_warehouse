# PyWarehouse

一個基於 Domain-Driven Design (DDD) 原則建構的現代化倉庫管理系統 API。

## 🚀 快速啟動

### 1. 環境準備
確保你已經安裝了 [uv](https://github.com/astral-sh/uv) (現代化 Python 套件管理器) 與 Docker。

### 2. 啟動基礎設施
```bash
docker-compose up -d
```

### 3. 設定環境變數
將 `.env.example` (如果有) 拷貝為 `.env` 並填入正確的資料庫連線資訊。

### 4. 執行資料庫遷移
```bash
uv run alembic upgrade head
```

### 5. 啟動服務 (開發模式)
```bash
uv run uvicorn src.app.main:app --reload
```
存取 API 文件：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🛠 開發習慣與規範

本專案遵循嚴格的工程實踐，詳細規範請參考 `GEMINI.md`。

### 1. 建築架構 (DDD)
*   **Domain**: 核心業務邏輯與實體（`src/app/domain`）。
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
*   **認證**: JWT 基礎認證，API 支援 Bearer Token 自動帶入（Swagger HTTPBearer）。

---

## 📜 開發歷程 (Implementation History)

1.  **專案初始化**: 建立基礎 DDD 目錄結構與 Dependency Injector 配置。
2.  **基礎設施建置**: 整合 SQLAlchemy (Async) 與 Redis，解決 Postgres 18+ Docker 掛載相容性問題。
3.  **使用者系統實作**: 
    - 實作帶有審計欄位的 `BaseAuditModel`。
    - 建立 `User` 模型與 Alembic 遷移邏輯。
    - 初始化 Root User (全零 UUID, Admin 權限)。
4.  **API 演進**:
    - 建立通用的 `BaseResponse` 與 `ListResponse` 規範。
    - 實作 JSON 格式登入 API 並分離 Auth/Users 標籤。
    - 抽離安全相依項目 (`dependencies.py`) 供全域使用。

---

## 📝 技術筆記 (Deep Dives)
更多技術細節請參考 `Note/` 目錄：
*   [Service 層回傳 DTO 策略](Note/service_layer_dto_strategy.md)
*   [Python 路徑與執行機制](Note/python_path_and_execution.md)
*   [相依注入研究](Note/dependency_injection_study.md)
