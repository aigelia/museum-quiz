import redis.asyncio as redis


class Database:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def set_current_question(self, user_id: int, question: str):
        await self.redis.set(f"user:{user_id}:current_question", question)

    async def get_current_question(self, user_id: int):
        return await self.redis.get(f"user:{user_id}:current_question")

    async def reset_current_question(self, user_id: int):
        await self.redis.delete(f"user:{user_id}:current_question")

    async def increment_score(self, user_id: int):
        await self.redis.incr(f"user:{user_id}:score")

    async def get_score(self, user_id: int):
        score = await self.redis.get(f"user:{user_id}:score")
        return int(score) if score else 0
