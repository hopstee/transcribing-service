import logging
import os
import time
from app.services.audio_service import Transcriber
from app.core.config import LOG_LEVEL, WORKERS_LOG_FILE
from app.services.redis_service import RedisService
from utils.logger import setup_logging

# r = RedisService()

# setup_logging(WORKERS_LOG_FILE, level=LOG_LEVEL, with_pid=True)

# transcriber = None

# def init_model(model_name: str):
#     global transcriber
#     if transcriber is None:
#         transcriber = Transcriber(model_name)

# def process_task(task):
#     try:
#         task_id = task["task_id"]
#         path = task["audio_path"]
#         model = task["model"]
#         trim = float(task["trim"])

#         r.set_status(task_id, "processing")

#         logging.info(f"🔄 Начата задача {task_id} | Модель: {model} | Файл: {path}")

#         # transcriber = Transcriber(model_name=model)
#         init_model(model)
#         result = transcriber.run(path, trim_duration=trim)

#         r.set_result(task_id, result.get('text'))
#         logging.info(f"✅ Завершена задача {task_id} | Результат: {result.get('text', '')[:60]}")

#     except Exception as e:
#         r.set_error(task_id, str(e))
#         logging.error(f"❌ Ошибка в задаче {task_id}: {e}")
#     finally:
#         os.remove(path)

# def run_worker():
#     logging.info("🎧 Worker запущен, ожидает задачи...")
#     while True:
#         try:
#             task = r.dequeue_task()
#             if task:
#                 process_task(task)
#         except r.exceptions.ResponseError as e:
#             logging.error(f"Redis error: {e}")
#             time.sleep(1)
#             return
        
        
        
        
class TranscriptionWorker:
    def __init__(self):
        setup_logging(WORKERS_LOG_FILE, level=LOG_LEVEL, with_pid=True)
        self.logger = logging.getLogger(__name__)
        self.redis = RedisService()
        self.transcriber = None
        self.model_name = None

    def init_model(self, model_name: str):
        if self.transcriber is None or self.model_name != model_name:
            self.logger.info(f"🚀 Загрузка модели {model_name}")
            self.transcriber = Transcriber(model_name=model_name)
            self.model_name = model_name

    def process_task(self, task: dict):
        task_id = task["task_id"]
        path = task["audio_path"]
        model = task["model"]

        self.redis.set_status(task_id, "processing")
        self.logger.info(f"🔄 Начата задача {task_id} | Модель: {model} | Файл: {path}")

        try:
            self.init_model(model)
            result = self.transcriber.run(path)
            self.redis.set_result(task_id, result.get("text"))
            self.logger.info(f"✅ Завершена задача {task_id} | Результат: {result.get('text', '')[:60]}")
        except Exception as e:
            self.redis.set_error(task_id, str(e))
            self.logger.error(f"❌ Ошибка в задаче {task_id}: {e}")
        finally:
            try:
                os.remove(path)
            except OSError as e:
                self.logger.warning(f"Не удалось удалить файл {path}: {e}")

    def run_loop(self):
        self.logger.info("🎧 Worker запущен, ожидает задачи...")
        while True:
            try:
                task = self.redis.dequeue_task()
                if task:
                    self.process_task(task)
            except self.redis.exceptions.ResponseError as e:
                self.logger.error(f"Redis error: {e}")
                time.sleep(1)
                return

if __name__ == "__main__":
    while True:
        try:
            worker = TranscriptionWorker()
            worker.run_loop()
        except Exception as e:
            logging.exception("Unhandled error in worker:")
            time.sleep(3)
