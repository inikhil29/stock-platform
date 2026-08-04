from enum import Enum

class UpstoxRedisKeys(str, Enum):
    UPSTOX_ACCESS_TOKEN_KEY = "auth:upstox_access_token"
    UPSTOX_AUTH_LOCK_KEY = "auth:auth_call_lock"
    
    
class UpstoxRedisConfig:
    UPSTOX_AUTH_CALL_RETRY_TIME = 300