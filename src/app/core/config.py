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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
