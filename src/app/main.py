from fastapi import FastAPI
from src.app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/")
async def root():
    return {"message": "Welcome to PyWarehouse API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
