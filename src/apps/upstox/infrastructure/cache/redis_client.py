import json
import logging
from typing import Any, Optional

import redis
from redis.retry import Retry
from redis.backoff import ExponentialBackoff

from apps.upstox.config.settings import settings

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self):
        self._client = redis.Redis.from_url(
           settings.UPSTOX_REDIS_URL,

            # Performance
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,

            # Retry strategy
            retry=Retry(ExponentialBackoff(), retries=3),
            retry_on_timeout=True,

            # Connection pool
            max_connections=20,
        )

        self._namespace = getattr(settings, "REDIS_NAMESPACE", "upstox")

    # ----------------------------
    # Internal Helpers
    # ----------------------------
    def _build_key(self, key: str) -> str:
        return f"{self._namespace}:{key}"

    def _serialize(self, value: Any) -> str:
        return json.dumps(value)

    def _deserialize(self, value: Optional[str]) -> Any:
        if value is None:
            return None
        return json.loads(value)

    # ----------------------------
    # Basic Operations
    # ----------------------------
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        try:
            namespaced_key = self._build_key(key)
            serialized_value = self._serialize(value)

            self._client.set(name=namespaced_key, value=serialized_value, ex=ttl)

        except Exception:
            logger.exception("Redis SET failed for key=%s", key)
            raise

    def get(self, key: str) -> Any:
        try:
            namespaced_key = self._build_key(key)
            value = self._client.get(namespaced_key)
            return self._deserialize(value)

        except Exception:
            logger.exception("Redis GET failed for key=%s", key)
            return None  # fail-safe

    def delete(self, key: str):
        try:
            namespaced_key = self._build_key(key)
            self._client.delete(namespaced_key)

        except Exception:
            logger.exception("Redis DELETE failed for key=%s", key)

    def exists(self, key: str) -> bool:
        try:
            return bool(self._client.exists(self._build_key(key)))
        except Exception:
            logger.exception("Redis EXISTS failed for key=%s", key)
            return False

    # ----------------------------
    # Advanced Operations
    # ----------------------------
    def set_if_not_exists(self, key: str, value: Any, ttl: int) -> bool:
        """
        Atomic lock (useful for ETL dedup / job locking)
        """
        try:
            return self._client.set(
                name=self._build_key(key),
                value=self._serialize(value),
                nx=True,
                ex=ttl
            )
        except Exception:
            logger.exception("Redis NX SET failed for key=%s", key)
            return False

    def increment(self, key: str, amount: int = 1) -> int:
        try:
            return self._client.incr(self._build_key(key), amount)
        except Exception:
            logger.exception("Redis INCR failed for key=%s", key)
            raise

    def ttl(self, key: str) -> int:
        try:
            return self._client.ttl(self._build_key(key))
        except Exception:
            logger.exception("Redis TTL failed for key=%s", key)
            return -1
        
        
redis_client = RedisClient()