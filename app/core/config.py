import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

MODEL_TYPES = ["tiny", "base", "small", "medium", "large", "turbo"]

def _get(key: str, env_default: str) -> str:
    return os.getenv(key, env_default) or env_default

DEFAULT_MODEL = _get("DEFAULT_MODEL", "turbo")
DEFAULT_DURATION = int(_get("DEFAULT_DURATION", "30"))
LOG_LEVEL = _get("LOG_LEVEL", "INFO")
ALLOWED_EXTENSIONS: List[str] = _get("ALLOWED_EXTENSIONS", ".mp3,.wav,.m4a").split(",")

REDIS_QUEUE_NAME = _get("REDIS_QUEUE_NAME", "transcribe_tasks")
REDIS_RESULTS_PREFIX = _get("REDIS_RESULTS_PREFIX", "transcribe_result:")
REDIS_HOST = _get("REDIS_HOST", "localhost")
REDIS_PORT = int(_get("REDIS_PORT", "6379"))
REDIS_DB = int(_get("REDIS_DB", "0"))

TRANSCRIBER_LOG_FILE = _get("TRANSCRIBER_LOG_FILE", "logs/transcribing_service.log")
WORKERS_LOG_FILE = _get("WORKERS_LOG_FILE", "logs/workers.log")
BENCHMARK_LOG_FILE = _get("BENCHMARK_LOG_FILE", "logs/benchmark.log")

UPLOAD_DIR = _get("UPLOAD_DIR", "/app/shared_audio")

WHISPER_BEAM_SIZE = _get("WHISPER_BEAM_SIZE", "5")
