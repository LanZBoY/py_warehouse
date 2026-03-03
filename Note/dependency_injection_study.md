# Python 依賴注入 (Dependency Injection) 技術筆記

本筆記記錄了在 `py-warehouse` 專案中，關於 Pydantic 設定與 `dependency-injector` 框架的深度技術探討。

---

## 1. Pydantic Settings & SettingsConfigDict
在 Pydantic v2 中，`SettingsConfigDict` 取代了舊版的 `class Config` 內部類別，用來定義設定模型的行為。

*   **用途**：集中管理環境變數（`.env`）讀取、大小寫敏感度、編碼等設定。
*   **範例**：
    ```python
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    ```

---

## 2. Dependency Injection (DI) 核心概念
專案採用了 `dependency-injector` 作為 DI 框架，特別適合 **DDD (領域驅動設計)** 架構。

### A. 關鍵元件
*   **Providers**: 物件生成的「配方」。
    *   `Singleton`: 全域單例。
    *   `Factory`: 每次呼叫都生成新物件。
    *   `Resource`: 具備初始化與關閉（Init/Shutdown）週期的資源（如 DB, Redis）。
*   **DeclarativeContainer**: 集中註冊所有配方的「倉庫」。
*   **Wiring (佈線)**: 將容器中的物件自動注入到指定模組的函式參數中。

---

## 3. 底層運作機制 (How it works?)

### A. 標記與掃描 (The Marker & Scanning)
當你寫下 `Provide[Container.service]` 時，背後使用了 Python 的 `__class_getitem__` 語法糖。

1.  **`Provide` 類別**：實作了 `__class_getitem__`，這讓它可以像 `List[int]` 一樣被呼叫。它並不回傳真正的物件，而是一個 **Marker (標記物件)**。
2.  **`@inject` 修飾器**：在函式物件上貼一個「標籤」（例如 `fn.__di_injected__ = True`）。
3.  **`container.wire()`**：使用 `inspect` 模組掃描所有函式，尋找帶有標籤的函式。

### B. 參數劫持 (Parameter Hijacking)
在執行期，DI 框架會攔截函式的呼叫：
*   它會解析函式的參數預設值（`__defaults__`）。
*   如果發現預設值是 `Provide` 標記，它會去容器中尋找對應的 Provider 並實例化。
*   最後將產生的實體動態地塞進 `kwargs` 中。

---

## 4. 遞迴依賴鏈 (Recursive Resolution)
DI 容器最優雅的地方在於它能自動處理「剝洋蔥」般的依賴關係。

*   **情境**：`Service` 依賴於 `Repository`，`Repository` 依賴於 `Database Session`。
*   **自動化**：你只需要在 `Container` 裡定義：
    ```python
    repo = providers.Factory(Repository, session=db_session)
    service = providers.Factory(Service, repo=repo)
    ```
*   **結果**：當你請求 `service` 時，容器會自動遞迴向下尋找，先建立 `db_session` -> 再建立 `repo` -> 最後組裝成 `service`。

---

## 5. 與 FastAPI `Depends` 的聯動

### A. 為什麼還要用 `Depends()`？
FastAPI 透過 `Depends` 建立請求級別的依賴解析門戶，而 `Provide` 則是 DI 容器的提取門戶。兩者結合可以達到：
1.  **單點注入**：路由只需注入最頂層的 Service，不需要寫多個 `Depends`。
2.  **乾淨的路由**：路由不需要知道底層 Repository 或 DB 的組裝細節。
3.  **測試友好**：透過 `container.provider.override(Mock())` 即可完成全域替換。

### B. 實作範例
```python
@router.get("/")
@inject
async def get_items(
    service: MyService = Depends(Provide[Container.my_service])
):
    return await service.execute()
```
*這行代碼中，`Depends` 是門票，`Provide` 是導航，`@inject` 則是最後把貨物送到手上的快遞員。*
