from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "PyWarehouse"

    # 資料庫連線資訊
    DATABASE_URL: str = "postgresql+asyncpg://xxx:xxx@localhost:5432/warehouse"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Database Credentials
    POSTGRES_USER: str = "xxx"
    POSTGRES_PASSWORD: str = "xxx"
    POSTGRES_DB: str = "xxx"

    # JWT Settings
    SECRET_KEY: str = "your-secret-key"  # 建議由環境變數提供
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days

    # Root User Initial Settings
    ROOT_USER_NAME: str = "admin"
    ROOT_USER_PASSWORD: str = "admin123"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
