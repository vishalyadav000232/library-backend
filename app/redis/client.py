import os
import json
import redis

import logging

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL")

logger.info("Initializing Redis client")

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True
)

print(redis_client.ping())

CACHE_TTL = 30

logger.info("Redis client initialized successfully")