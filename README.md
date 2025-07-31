# 🎧 Async Transcription Service

Масштабируемый сервис для асинхронного транскрибирования аудиофайлов с использованием FastAPI, Redis и воркеров.

---

## 📦 Возможности

- Асинхронная постановка задач на транскрипцию
- Поддержка нескольких моделей Whisper
- Параллельная обработка задач (воркеры)
- Масштабируемость с помощью Docker Compose
- Постоянное хранилище для Redis
- Поддержка логирования

---

## 🚀 Быстрый старт

Убедитесь, что у вас установлен [Docker](https://www.docker.com/), [Docker Compose](https://docs.docker.com/compose/) и присутствуют модели в директории ./_cache/whisper, иначе загрузка будет происходить при первом запросе и значительно увеличит время обработки.

## 🔧 Сборка и запуск

```bash
docker compose up --build --scale worker=4
```

- API будет доступен по адресу: http://localhost:8000
- Redis работает в фоновом режиме
- Воркеры автоматически читают и обрабатывают задачи из очереди

---

## 🛠 Масштабирование воркеров

Для увеличения числа воркеров:

```bash
docker compose up --scale worker=10 -d
```

---

## 📁 Структура проекта

```bash
.
├── _cache/
│   └── wisper                 # Кэш модели Whisper
│       ├── base.pt
│       ├── large.pt
│       ├── small.pt
│       └── ...
├── .devcontainer/
│   ├── devcontainer.json      # Конфигурация VS Code для разработки
│   └── Dockerfile             # Докерфайл для разработки
├── app/
│   ├── core
│   │   ├── config.py          # Настройки окружения
│   │   ├── decorators.py      # Логирование этапов обработки
│   │   └── utils.py           # Валидация и вспомогательные функции
│   └── services               # Валидация и вспомогательные функции
│   │   ├── audio_service.py   # Обёртка над Whisper
│   │   └── redis_service.py   # Сервис для работы с redis
├── benchmark/
│   ├── audios/                # Аудио записи для теста
│   ├── plots/                 # Графики по результатам тестироваиня моделеф
│   ├── text-references/       # Эталонные тексты для сверки результатов
│   └── run.py                 # Скрипт тестирования моделей
├── logs/                      # Логи приложения
├── shared_audio/              # Общие аудиофайлы для обработки
├── utils/
│   └── logger.py              # Логирование приложения
├── main.py                    # FastAPI сервер
├── worker.py                  # Воркеры, обрабатывающие очередь
├── Dockerfile.api             # Dockerfile для API
├── Dockerfile.worker          # Dockerfile для воркеров
├── docker-compose.yml         # Docker Compose конфигурация
├── requirements.txt           # Python зависимости
└── README.md                  # Документация
```

---

## 📤 API

### `POST /transcribe/`

Отправка аудиофайла на транскрипцию.

#### Параметры запроса:
| Параметр | Тип    | Обязательный | Описание                                                                          |
| -------- | ------ | -------------|---------------------------------------------------------------------------------- |
| `file`   | файл   | ✅           | Аудиофайл (`.mp3`, `.wav`, `.m4a` и т.д.)                                         |
| `model`  | строка | ❌           | Название модели (`tiny`, `base`, `small`, `medium`, `large`, `turbo`)             |

Дефолтная модель - `turbo`

#### Пример запроса:
```
curl -F "file=@example.m4a" \
     "http://localhost:8000/transcribe/?model=base&trim=30"
```

#### Пример ответа:
```json
{
  "task_id": "abc123",
  "status": "queued"
}
```

### `GET /transcribe/{task_id}`

Получение статуса задачи транскрипции или результата.

#### Параметры пути:
| Параметр  | Тип    | Описание                    |
| --------- | ------ |---------------------------- |
| `task_id` | строка | ID задачи, полученный ранее |

#### Пример запроса:
```
curl http://localhost:8000/status/abc123
```

#### Возможные ответы:

### Статус: в очереди

```json
{
  "task_id": "1234...",
  "status": "queued",
}
```

### Статус: обработка

```json
{
  "task_id": "1234...",
  "status": "processing",
}
```

### Статус: готово

```json
{
  "task_id": "1234...",
  "status": "done",
  "result": {
    "text": "Привет, это голосовое сообщение...",
    ...
  },
}
```

### Статус: ошибка

```json
{
  "task_id": "1234...",
  "status": "error",
}
```

---

## 📊 Бенчмарк

Для теста нужно предоставить аудиофайлы и текст-референс для сравнения результатов. Название файла и текста-референса должны быть одинаковые.

```
audio -> sample1.m4a
reference -> sample1.txt
```

Так же допускаются варианты

```
audio -> sample1-loud.m4a
reference -> sample1.txt
```

Далее нужно запустить контейнер

```
docker compose run --rm benchmark
```

И внутри контейнера запускаем скрипт

```
python3 -m benchmark.run
```

---

## ⚙️ Переменные окружения

Пример `.env` файла:

```env
DEFAULT_MODEL=base
DEFAULT_DURATION=30
LOG_LEVEL=INFO
ALLOWED_EXTENSIONS=.mp3,.wav,.m4a,.aac,.ogg

REDIS_QUEUE_NAME = "transcribe_tasks"
REDIS_RESULTS_PREFIX = "transcribe_result:"
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

UPLOAD_DIR=/app/shared_audio

WHISPER_BEAM_SIZE=5
```

---

## 👷🏻‍♂️ Локальная разработка

### Для локального запуска docker

`.env` файл остается таким же за исключением:

```
REDIS_HOST=localhost
UPLOAD_DIR=/shared_audio
```

- Установите VS Code расширение `Dev Containers`
- В одном терминале запустите `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- В другом терминале запустите `watchmedo auto-restart --patterns="*.py" --recursive -- python worker.py`

### Для разработки

#### Развернуть python окружение
_(На 11.06.2025 последняя стабильная версия python 3.11, для управления версиями используйте утилиту ___pyenv___)_

```bash
python3.11 -m venv venv
```

#### Активировать окружение

macOS / Linux
```bash
source venv/bin/activate
```

Windows (CMD)
```bash
venv\Scripts\activate
```

Windows (PowerShell)
```bash
.\venv\Scripts\Activate.ps1
```

#### Установить зависимости

```bash
pip install -r requirements.txt
```

#### Для деактивации окружения используйте команду

```bash
deactivate
```

---

## 📚 Зависимости

Файл `requirements.txt`:

```txt
python-multipart
fastapi
uvicorn
openai-whisper
faster-whisper
typer
dotenv
jiwer>=3.0.0
matplotlib
redis
torch
aiofiles
```

---

## 📝 Логирование

- Все логи пишутся в файл logs/service.log
- Также логи выводятся в stdout
- Готово к подключению стороннего лог-сервиса (Logtail, ELK, Grafana Loki и др.)

---

## 📚 Предустановка моделей

Для того чтобы модели не загружались при первом запуске, поместите заранее скачанные модели в директорию `_cache/whisper`. Это ускорит первые обработки файлов.

---

## 🧼 Очистка проекта

```bash
docker compose down --rmi all --volumes
```

Удалит все контейнеры и volume (включая Redis-хранилище).

---

## 📃 Лицензия

MIT License
