import os
import json
import redis
import logging

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL")

try:
    logger.info("Initializing Redis client")

    redis_client = redis.from_url(
        REDIS_URL,
        decode_responses=True
    )

    redis_client.ping()

    logger.info("Redis connected successfully")

except Exception:
    logger.exception("Failed to connect to Redis")
    raise

CACHE_TTL = 30