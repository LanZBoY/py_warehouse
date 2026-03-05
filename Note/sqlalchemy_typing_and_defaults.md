# SQLAlchemy 2.0 型別提示與預設值最佳實作

這份筆記記錄了在 SQLAlchemy 2.0 (透過 `DeclarativeBase`) 定義 Model 時，關於主鍵預設值與可空欄位型別設計的關鍵邏輯。

## 1. 主鍵預設值：`default=uuid4` vs. 資料庫生成

在定義 UUID 主鍵時，常見做法是使用 `default=uuid4`：

```python
id: Mapped[UUID] = mapped_column(UUID_TYPE(as_uuid=True), primary_key=True, default=uuid4)
```

### 為什麼要在 Python 層級設定 `default`？
1. **即時 ID 獲取 (Immediate Access)**：
   當你在程式碼中實例化一個物件（例如 `user = User(name="Alex")`）時，SQLAlchemy 會立即呼叫 `uuid4()` 並賦值給 `user.id`。你不需要等到 `session.commit()` 或 `session.flush()` 就能拿到這個 ID。這在需要回傳新建立物件的 ID，或建立關連資料時非常方便。
2. **與資料庫解耦**：
   即使資料庫層級沒有設定 `DEFAULT gen_random_uuid()`，應用程式也能保證每一筆資料都有唯一的 ID。
3. **區別 `default` 與 `server_default`**：
   - `default`：由 Python (SQLAlchemy) 在 Insert 前生成並傳送給資料庫。
   - `server_default`：由資料庫在寫入時自動生成。
   - **最佳實作**：在 Python 層級設定 `default` 能提供更好的開發體驗（即時拿到 ID）。

---

## 2. 可空欄位：`Mapped[Optional[str]]` 與 `nullable`

在 SQLAlchemy 2.0 中，欄位的定義包含兩個層次：**靜態型別**與**執行期屬性**。

```python
# 推薦的顯式定義方式
note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
```

### 靜態檢查 (Static Analysis) 的影響
- **`Mapped[str]`**：編輯器（如 VS Code / Pyright）會認為此欄位「絕對不為 None」。若你對其進行字串操作（如 `.strip()`），編輯器會認為是安全的。
- **`Mapped[Optional[str]]`**：編輯器會提醒你該欄位可能是 `None`。若直接操作，會出現黃色底線警告，提示你需要先進行 `if note is not None` 的檢查。這能大幅減少 `AttributeError: 'NoneType' object has no attribute '...'` 的錯誤。

### 執行期 (Runtime) 的影響
- **SQLAlchemy 推導**：SQLAlchemy 會嘗試從型別推導 `nullable` 屬性。
  - `Mapped[str]` $\rightarrow$ 預設推導為 `nullable=False`。
  - `Mapped[Optional[str]]` $\rightarrow$ 預設推導為 `nullable=True`。
- **顯式定義優勢**：手動加上 `nullable=True` 能確保即使在複雜的型別推導失敗時，資料庫 Schema 依然正確。

---

## 3. 總結與最佳實作建議

| 需求 | 推薦定義方式 | 理由 |
| :--- | :--- | :--- |
| **UUID 主鍵** | `default=uuid4` | 確保實例化後立即擁有 ID，不依賴資料庫回傳。 |
| **必填欄位** | `Mapped[str]` | 強制靜態檢查與資料庫層級都不允許空值。 |
| **選填欄位** | `Mapped[Optional[T]]` | 讓開發者在存取該欄位時，受到 Linter 的「空值安全」保護。 |

透過結合 **Python Type Hints (PEP 484)** 與 **SQLAlchemy Column Definition**，我們可以打造出一個既具備資料庫約束，又能提供開發期安全保護的 Robust Data Model。
