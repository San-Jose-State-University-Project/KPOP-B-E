import redis.asyncio as redis
import json

class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0):
        self.r = redis.Redis(host=host, port=port, db=db)

    async def set(self, key, value, ex=None):
        json_data = json.dumps(value)
        await self.r.set(key, json_data,ex=ex)

    async def get(self, key):
        raw_data = await self.r.get(key)
        if raw_data is None:
            return None
        value = json.loads(raw_data.decode('utf-8'))
        return value

redis_client = RedisClient()