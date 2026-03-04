我需要建立一個基礎的使用者系統

所以需要建立一個Users資料表

1. Users
- id uuid pk
- username string, 必填
- password_with_salt string, 必填
- role enum (admin, user), 必填
- created_at datetime, 必填
- created_by datetime, 必填
- updated_at datetime, 非必填
- updated_by datetime, 非必填

備註：建議將
- created_at datetime, 必填
- created_by datetime, 必填
- updated_at datetime, 非必填
- updated_by datetime, 非必填
這是個欄位透過base 產生一個root_class 讓所有class繼承之 (因為所有資料表都會用到)

再來要建立一個root user
id 為 全零的uuid作為表示
username跟password則可透過.env 設定(在跑migration時建立)
role 預設為admin

2.API layer

備註：回傳物件規則，分為兩種
  1. 存取單一物件 {
    data: [T]
  }
  2. 存取列表物件 {
    total: int
    data: list[T]
  }
建議幫我透過繼承的方式來定義return schema
另外幫我寫在GEMINI.md中供後續使用

--- AuthAPI ---
- (POST) login API
  - 透過username跟password換jwt token(時效暫時為30天)
  - return {
    data: <jwt_token>
  }

--- UserAPI ---
以下API 需要登入後並且role=admin才可呼叫
- (GET) Mgmt UserList
  - 取得所有使用者列表
  - query
    - top:int = 10
    - offset:int = 0
  - return {
    total: 所有資料數量
    data:{
        id,
        username,
        role,
        created_at,
        created_by,
        updated_at,
        updated_by
    }
  }

- (POST) Mgmt Create User
  - input {
    username,
    password,
  }

---
## 實作紀錄 (Status: Done)
1. **Infrastructure & Base**:
   - 在 `src/app/infrastructure/base.py` 定義 `BaseAuditModel`。
   - 在 `GEMINI.md` 更新 API 回傳規範。
   - 更新 `.env` 與 `src/app/core/config.py` 加入 JWT 與 Root User 設定。
2. **Domain Layer**:
   - 建立 `src/app/domain/user/enums.py` 定義 `UserRole`。
   - 建立 `src/app/domain/user/models.py` 定義 `User` 模型。
3. **Migration & Seeding**:
   - 執行 Alembic 遷移並在腳本中加入 Root User 初始化 (ID: `0000...`, Role: `admin`)。
4. **Application Layer**:
   - 實作 `src/app/core/security/auth.py` (Bcrypt, JWT)。
   - 實作 `src/app/infrastructure/repositories/user_repository.py`。
   - 實作 `src/app/application/user/services.py` (`AuthService`, `UserService`)。
5. **API Layer**:
   - 實作 `src/app/api/schemas.py` 基礎與 User 相關 Schema。
   - 實作 `src/app/api/v1/endpoints/user.py` 整合登入與管理 API。
6. **DI & Main**:
   - 更新 `src/app/core/container.py` 註冊元件。
   - 更新 `src/app/main.py` 掛載路由。
