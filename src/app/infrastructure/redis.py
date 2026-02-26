import redis.asyncio as redis
from src.app.core.config import settings

async def get_redis():
    client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.close()
