# Technical Note: Service Layer Return Strategy (DTO vs ORM)

## 1. Pydantic `from_attributes` 機制
在 Pydantic v2 中，設定 `model_config = ConfigDict(from_attributes=True)`（舊版為 `orm_mode=True`）允許 Pydantic 從非字典物件（如 SQLAlchemy 模型實體）中讀取資料。

*   **運作原理**：Pydantic 會遍歷 Schema 定義的欄位，並使用 `getattr(obj, field_name)` 從傳入的物件中獲取值。
*   **型別轉換**：如果 Schema 欄位型別與物件屬性不完全一致（如 `UUID` 物件 vs `str` 欄位），Pydantic 會嘗試自動轉換。

## 2. FastAPI 序列化流程
當一個路由回傳資料時，流程如下：
1.  **Endpoint 執行**：呼叫 Service 獲取資料。
2.  **型別檢查**：FastAPI 檢查回傳值是否符合 `response_model`。
3.  **對應 (Mapping)**：如果回傳的是 ORM 物件且 `from_attributes=True`，FastAPI 會呼叫 `Schema.model_validate(obj)` 進行對應。
4.  **序列化**：使用 `jsonable_encoder` 將 Pydantic 物件轉為 Dict，最後由 `JSONResponse` 轉為 JSON 字串。

## 3. 直接回傳 ORM 物件的風險：`DetachedInstanceError`
在非同步 (Async) SQLAlchemy 環境中，直接將 ORM 物件交由 FastAPI 進行 Mapping 存在重大風險：
*   **Session 生命週期**：如果 `AsyncSession` 在 Service 層執行完畢後就已關閉（如使用了 `async with session` 區塊）。
*   **延遲讀取錯誤**：當 FastAPI 在最後一刻（序列化階段）嘗試讀取物件屬性時，如果該物件已與已關閉的 Session 斷開（Detached），會拋出 `DetachedInstanceError` 導致 500 錯誤。

## 4. 最佳實踐：在 Service 層轉換為 DTO
為了確保架構的穩定性與層級隔離，建議在 **Application Service** 層就完成轉換：

```python
# 推薦做法：Service 層回傳 Pydantic DTO
async def get_user(self, user_id: UUID) -> UserRead:
    user = await self._user_repo.get(user_id)
    # 此時完成轉換，資料與 Session 脫鉤
    return UserRead.model_validate(user)
```

### 優點：
1.  **層級隔離**：API 層不需感知資料庫實體（SQLAlchemy Model），僅處理純資料物件。
2.  **安全可靠**：避免 `DetachedInstanceError`，因為回傳給 API 層的是已載入完畢的 Pydantic 實體。
3.  **測試友善**：Service 的單元測試不需要 Mock 複雜的 SQLAlchemy 狀態，只需驗證輸出的資料格式。
4.  **明確合約**：Service 的回傳型別提示 (Type Hint) 非常明確，提升程式碼可讀性。
