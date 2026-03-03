幫我建立一個di 容器，以API服務需要用到直接注入

---
## 實作紀錄 (Status: Done)

### 1. DI 框架選擇與安裝
- **套件**: `dependency-injector` (4.48.3)
- **理由**: 支援嚴謹的型別檢查、非同步資源管理與 DDD 深度解耦。

### 2. 核心元件配置
- **`src/app/core/container.py`**:
    - 實作 `DeclarativeContainer`。
    - 註冊 `DATABASE_URL` 相關的 `engine` 與 `session_factory`。
    - 註冊 `REDIS_URL` 非同步連線資源。
    - 設定 `wiring_config` 自動佈線範圍。

### 3. 系統整合
- **`src/app/main.py`**:
    - 初始化 `Container`。
    - 使用 `lifespan` 處理容器與資源的生命週期。
    - 啟動時執行 `container.wire()` 讓 `@inject` 生效。

### 4. 學習資源
- **`Note/dependency_injection_study.md`**: 紀錄了 DI 的底層運作原理、`__class_getitem__` 實作方式以及與 FastAPI `Depends` 的聯動細節。
