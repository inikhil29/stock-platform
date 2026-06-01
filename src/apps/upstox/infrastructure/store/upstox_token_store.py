from apps.upstox.infrastructure.cache.redis_keys import RedisKeys, RedisConfig
from apps.upstox.infrastructure.cache.redis_client import RedisClient

class UpstoxAccessTokenStore:
    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client
        self.redis_access_token_key = RedisKeys.UPSTOX_ACCESS_TOKEN_KEY.value
        self.auth_lock_key = RedisKeys.UPSTOX_AUTH_LOCK_KEY.value

    def get_token(self):
        return self.redis.get(self.redis_access_token_key)

    def set_token(self, token_data, ttl: int):
        self.redis.set(
            self.redis_access_token_key,
            token_data,
            ttl
        )

    def acquire_lock(self):
        return self.redis.set_if_not_exists(
            self.auth_lock_key,
            "locked",
            ttl=RedisConfig.UPSTOX_AUTH_CALL_RETRY_TIME
        )