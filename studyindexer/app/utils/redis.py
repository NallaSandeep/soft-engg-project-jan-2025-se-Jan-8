"""Redis client utilities"""
import redis
from app.core.config import settings

def get_redis_client():
    """Get Redis client instance with robust configuration"""
    client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=30,
        socket_timeout=30,
        retry_on_timeout=True,
        health_check_interval=30
    )
    return client 