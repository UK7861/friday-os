import os
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RedisCache:
    def __init__(self):
        self._client = None
        self._available = False
        try:
            self._client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
            self._client.ping()
            self._available = True
            print("[Redis] Connected successfully.")
        except Exception as e:
            print(f"[Redis] Not available ({e}). Running with in-memory fallback.")
        self._memory: dict = {}

    def set_state(self, key: str, value: str, ex: int = 3600):
        if self._available:
            try:
                self._client.set(key, value, ex=ex)
                return
            except Exception:
                pass
        self._memory[key] = value

    def get_state(self, key: str):
        if self._available:
            try:
                return self._client.get(key)
            except Exception:
                pass
        return self._memory.get(key)

    def publish_update(self, channel: str, message: str):
        if self._available:
            try:
                self._client.publish(channel, message)
            except Exception:
                pass

redis_cache = RedisCache()
