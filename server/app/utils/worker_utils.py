from app.core.config import Settings
import redis

settings = Settings()
redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
redis_connection = redis.Redis.from_url(redis_url)
