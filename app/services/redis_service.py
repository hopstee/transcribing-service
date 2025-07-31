import json
import redis

from app.core.config import REDIS_DB, REDIS_HOST, REDIS_PORT, REDIS_QUEUE_NAME, REDIS_RESULTS_PREFIX

class RedisService:
    def __init__(self):
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

    def _key(self, task_id: str) -> str:
        return f"{REDIS_RESULTS_PREFIX}{task_id}"

    def enqueue_task(self, task_data: dict):
        self.redis.rpush(REDIS_QUEUE_NAME, json.dumps(task_data))

    def dequeue_task(self, timeout: int = 5):
        result = self.redis.blpop(REDIS_QUEUE_NAME, timeout=timeout)
        if result is None:
            return None

        _, task_data_str = result
        return json.loads(task_data_str)

    def set_status(self, task_id: str, status: str):
        state = self.get_result(task_id) or self.default_state()
        state["status"] = status
        self._save(task_id, state)

    def update_progress(self, task_id: str, progress: float, text: str | None = None):
        state = self.get_result(task_id) or self.default_state()
        state["status"] = "processing"
        state["progress"] = round(progress, 4)
        if text:
            state["text"] = text
        self._save(task_id, state)

    def set_error(self, task_id: str, message: str):
        state = self.get_result(task_id) or self.default_state()
        state["status"] = "error"
        state["error"] = message
        self._save(task_id, state)

    def set_result(self, task_id: str, text: str, meta: dict | None = None):
        state = self.default_state()
        state.update({
            "status": "done",
            "progress": 1.0,
            "text": text,
            "meta": meta or {}
        })
        self._save(task_id, state)

    def get_result(self, task_id: str):
        key = self._key(task_id)
        raw = self.redis.get(key)
        if raw:
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return None
        return None

    def delete_task(self, task_id: str):
        self.redis.delete(self._key(task_id))

    def _save(self, task_id: str, data: dict):
        self.redis.set(self._key(task_id), json.dumps(data), ex=3600)

    def default_state(self) -> dict:
        return {
            "status": "queued",
            "progress": 0.0,
            "text": None,
            "error": None,
            "meta": {}
        }
