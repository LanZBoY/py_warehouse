from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "PyWarehouse"
    
    # 資料庫連線資訊 (開發環境預設連至 localhost)
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/warehouse"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
