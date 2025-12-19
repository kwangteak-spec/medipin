from redis import Redis
from app.config import settings
import json

redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

def cache_set(key: str, value: dict, ttl: int = 3600):
    """Redis에 JSON 데이터 저장"""
    redis_client.set(key, json.dumps(value), ex=ttl)

def cache_get(key: str):
    """Redis에서 JSON 반환"""
    data = redis_client.get(key)
    return json.loads(data) if data else None
