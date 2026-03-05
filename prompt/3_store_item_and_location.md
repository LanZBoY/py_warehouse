接下來要來做基礎的設定
1. 儲存物品的設定
2. 儲存位置的設定

---  DB Schema ---

首先儲存物品資料表Schema
1. id, uuid;pk
2. name str (必填)
3. note str
4. <audit_info>

再來是儲存位置的資料表Schema
1. id, uuid;pk
2. name str (必填)
3. note str
4. <audit_info>

---
## 實作紀錄 (Status: Done)

1.  **Domain**: 建立 `src/app/domain/item/models.py` 與 `src/app/domain/location/models.py`。
2.  **Infrastructure**:
    *   建立 `src/app/infrastructure/repositories/item_repository.py` 與 `location_repository.py`。
    *   更新 `src/app/infrastructure/models.py` 匯總點。
3.  **Application**: 建立 `src/app/application/item/services.py` 與 `location/services.py`。
4.  **API**:
    *   更新 `src/app/api/schemas.py` 增加 Item 與 Location DTO。
    *   建立 `src/app/api/v1/endpoints/item.py` 與 `location.py`。
    *   在 `src/app/main.py` 註冊路由。
5.  **DI**: 在 `src/app/core/container.py` 註冊新的 Service 與 Repository。
6.  **DB**: 執行 Alembic 遷移，建立 `items` 與 `locations` 資料表。