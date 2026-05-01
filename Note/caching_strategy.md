# Technical Note: Caching Strategy（暫不啟用，留待需要時參考）

## 0. 結論先講

**目前不需要加 cache。** 內部倉儲系統規模下（推測 ~1000 物品 / ~200 位置 / < 100 活躍使用者），Postgres 加正確索引就足以應付，加 cache 只會帶來一致性負擔卻看不到效能收益。

本文件記錄**未來真的需要時**該往哪些方向看、各個候選的成本/效益分析，避免重新討論。

---

## 1. 何時才應該開始考慮加 cache

不是憑感覺，要靠數據：

| 訊號 | 該做的事 |
|---|---|
| Endpoint p99 latency 超過 SLA（例如 > 200ms） | 先 `EXPLAIN ANALYZE` 看是不是 query plan 問題 / 缺索引 |
| DB CPU 持續高水位 | 看是哪幾條 query 吃資源（pg_stat_statements） |
| 同一份資料在短時間被反覆查 | 才是 cache 真正適用的場景 |

**順序：profiling → 補索引 → 改 query → 才考慮 cache。** 跳過前面直接加 cache 是 premature optimization。

---

## 2. 候選盤點（按 CP 值排序）

### 2.1 Item / Location 主檔（推薦的第一個 cache 點）

**模式：** Cache-Aside

```
讀：Redis → miss 就打 DB，寫回 Redis（TTL 1h）
寫：update / delete 後 DEL 對應 key
```

- **Key 設計：** `item:{uuid}`、`location:{uuid}`
- **TTL：** 1 小時（即使忘了 invalidate 也不會錯太久）
- **適用點：** `ItemService.get_item`, `LocationService.get_location`
- **Invalidate 點：** `update_item`, `delete_item`, `update_location`, `delete_location`

**為什麼推這個當第一個：**
- 模式單純、無併發陷阱
- 寫入頻率極低（物品基本不變）
- 即使 cache 全失效也不影響正確性
- 適合練手

**注意事項：**
- ⚠️ 目前 `apply_movement` **沒有**驗證 item / location 存在（直接信任 API 傳入的 ID），所以加這個 cache **不會**減少 stock 流程的 DB 查詢，純粹只加速 GET endpoint。
- 列表查詢（`list_items`）不要 cache：分頁參數組合太多、invalidate 麻煩、收益低。

### 2.2 StockBalance.get_balance

**模式：** Cache-Aside + Write-Through invalidate

- **Key 設計：** `stock:balance:{item_id}:{location_id}`
- **TTL：** 短（5~10 分鐘），降低過期風險
- **Invalidate 點：** `apply_movement` 的 transaction commit 後

**重要陷阱：**
- ❌ **`StockService.adjust` 內部讀 balance 算 delta 時絕對不能讀 cache**，否則高併發下 delta 會算錯導致數量錯亂。決策路徑（讀後寫）必須直接打 DB（甚至要 `with_for_update`，`apply_movement` 已有）。
- ⚠️ Invalidate 必須在 transaction commit **之後**做，commit 前刪掉 cache 會讓其他 reader 重新讀到舊值再寫回。
- ⚠️ Write-then-invalidate 仍有微小 race window；嚴格場景需考慮「Write → Set TTL=0」或 double-delete 模式。

**為什麼建議比 Item 晚做：**
- 寫入路徑分散在 `apply_movement` 各分支，invalidate 點要全部找齊
- 一致性陷阱多

### 2.3 列表查詢（`list_balances` / `list_movements` / `list_items` 等）

**結論：不建議 cache。**

- Key 要含 `(skip, limit, filters)` 所有組合 → 命中率低
- 任一筆資料變動就要 invalidate 整類 → 維運痛
- 分頁查詢本身也不是熱點

例外：如果有「首頁儀表板」這種固定查詢且更新可容忍幾秒延遲，可以單獨針對該 endpoint 做短 TTL（10~30 秒）的 result cache。

---

## 3. 不該放 cache 的東西（已討論過的決策）

| 項目 | 原因 |
|---|---|
| JWT decoded payload | HS256 驗證本身在微秒級，cache 無意義 |
| Refresh token | 屬於認證狀態（state），需要持久性與 JOIN 查詢能力，放 Postgres |
| 寫入操作（apply_movement, create / update / delete） | 寫操作本身不該被 cache，重點是觸發 invalidate |
| 使用者密碼比對 | 永遠不要 cache 密碼相關計算 |

---

## 4. 實作通則（真的開始做的時候）

### 4.1 抽象層

建議在 `infrastructure/cache/` 下建一個薄薄的 `CacheService`：

```python
class CacheService:
    def __init__(self, redis: Redis): ...
    async def get_json(self, key: str) -> Optional[dict]: ...
    async def set_json(self, key: str, value: dict, ttl: int) -> None: ...
    async def delete(self, *keys: str) -> None: ...
    async def delete_pattern(self, pattern: str) -> None: ...  # 慎用
```

讓 application service 只看到 `CacheService`，方便日後換 store 或加 in-memory L1。

### 4.2 Key 命名規範

`{資源}:{識別子}` — 例：`item:abc-123`、`stock:balance:item-id:loc-id`

加版本前綴（`v1:item:...`）方便未來破壞性變更時整批失效。

### 4.3 Invalidate vs TTL 雙保險

每個 cache 都要同時設：
1. **明確的 invalidate 點**（write 後 DEL）
2. **合理的 TTL**（兜底，避免 invalidate 漏掉時資料永遠錯）

### 4.4 Cache miss 不該讓系統倒下

Redis 掛掉時，整個 read path 必須 fallback 到 DB（try/except 包起來、log warning、不 raise）。Cache 是優化，不是相依。

### 4.5 寫入失敗的處理順序

正確順序：
```
1. DB write (commit)
2. Redis DEL  ← 失敗就 log，不 rollback DB
```

錯誤順序：
```
1. Redis DEL
2. DB write   ← 中間有人讀會把舊值寫回 cache
```

---

## 5. Redis 已有的設定

容器中已經 wired 好（暫未使用）：

- `src/app/core/container.py:42` — `redis_pool` provider
- `src/app/infrastructure/redis.py` — 一個未被使用的 `get_redis()` async generator（可清掉或當參考）
- `src/app/core/config.py` — `REDIS_URL: str = "redis://localhost:6379/0"`
- `docker-compose.yml` — Redis service 應已就緒（如未確認請開啟此檔案）

要啟用時的最小步驟：
1. 在 `infrastructure/cache/cache_service.py` 建立 `CacheService`
2. 在 `Container` 加上 `cache_service = providers.Factory(CacheService, redis=redis_pool)`
3. 注入到要 cache 的 application service

---

## 6. 觀察指標（加 cache 後一定要監測）

- Cache hit rate（< 70% 通常代表設計有問題）
- Redis 記憶體用量趨勢
- DB query 數量是否真的下降
- p99 latency 變化

沒有這些指標就別加 cache —— 不知道有沒有效，比沒做還糟。
