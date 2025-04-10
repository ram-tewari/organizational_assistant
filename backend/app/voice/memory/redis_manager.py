import redis
import json
from datetime import timedelta


class ConversationMemory:
    def __init__(self, host='localhost', port=6379):
        self.redis = redis.Redis(host=host, port=port, decode_responses=True)

    def get_context(self, user_id: str) -> dict:
        """Retrieve conversation context"""
        data = self.redis.get(f"conversation:{user_id}")
        return json.loads(data) if data else {"history": []}

    def update_context(self, user_id: str, new_data: dict, ttl_minutes=30):
        """Update context with new data"""
        context = self.get_context(user_id)
        context.update(new_data)
        context["history"].append(new_data)  # Store full history

        self.redis.setex(
            f"conversation:{user_id}",
            timedelta(minutes=ttl_minutes),
            json.dumps(context)
        )

    def clear_context(self, user_id: str):
        self.redis.delete(f"conversation:{user_id}")