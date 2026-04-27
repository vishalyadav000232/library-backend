# app/cache/redis_client.py

import redis
import json

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

CACHE_TTL = 30 