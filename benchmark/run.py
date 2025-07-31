import time
import os
import sys
import csv
from jiwer import wer

import matplotlib.pyplot as plt
from collections import defaultdict
import statistics

from utils.logger import setup_logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.audio_service import Transcriber
from app.core.config import BENCHMARK_LOG_FILE, LOG_LEVEL, MODEL_TYPES

AUDIO_DIR = "benchmark/audios"
TEXT_REFERENCES_DIR = "benchmark/text-references"
RESULT_CSV = "benchmark/results.csv"

AUDIO_FILES = [f for f in os.listdir(AUDIO_DIR) if not f.startswith('.')]

setup_logging(BENCHMARK_LOG_FILE, level=LOG_LEVEL)

def get_reference_text(audio_filename: str) -> str:
    base_name = audio_filename.split("-")[0].split(".")[0]
    reference_path = os.path.join(TEXT_REFERENCES_DIR, f"{base_name}.txt")
    
    if not os.path.exists(reference_path):
        raise FileNotFoundError(f"❌ Эталонный текст не найден: {reference_path}")
    
    with open(reference_path, "r", encoding="utf-8") as ref_file:
        return ref_file.read().strip()

def benchmark():
    results = []

    with open(RESULT_CSV, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Модель",
            "Аудио файл",
            "Влительность",
            "Длина распознанного текста",
            "WER",
            "Оценка точности",
            "Распознанный текст"
        ])

        for model in MODEL_TYPES:
            transcriber = Transcriber(model_name=model)
            print(f"\n🧪 Тестируем модель: {model}")

            for audio_file in AUDIO_FILES:
                audio_path = os.path.join(AUDIO_DIR, audio_file)

                try:
                    reference_text = get_reference_text(audio_file)
                except FileNotFoundError as e:
                    print(e)
                    continue

                start = time.perf_counter()
                result = transcriber.run(audio_path)
                duration = round(time.perf_counter() - start, 2)
                
                recognized = result.get("text", "").strip()
                error_rate = round(wer(reference_text, recognized), 3)

                row = [
                    model,
                    audio_file,
                    duration,
                    len(recognized),
                    error_rate,
                    get_estimate_error_rate(error_rate),
                    recognized
                ]
                writer.writerow(row)
                results.append(row)

                print(f"✅ {audio_file}: {duration}s, {len(recognized)} символов, WER: {error_rate}")

    visualize(results)

def get_estimate_error_rate(error_rate):
    if (error_rate == 0.0):
        return "Идеально"
    
    if (error_rate < 0.2):
        return "Отлично"
    
    if (error_rate < 0.4):
        return "Терпимо"
    
    if (error_rate >= 0.4):
        return "Плохо"

def visualize(results):

    os.makedirs("benchmark/plots", exist_ok=True)

    durations = defaultdict(list)
    wers = defaultdict(list)

    for row in results:
        model, _, duration, _, wer_val, _, _ = row
        durations[model].append(float(duration))
        wers[model].append(float(wer_val))

    avg_wers = average_wer(plt, wers)
    wer_vars = wer_variance(plt, wers)
    avg_durations = average_duration(durations)
    summary_chart(avg_wers, wer_vars, avg_durations)

def average_wer(plt, wers):
    plt.figure(figsize=(8, 5))
    avg_wers = {m: sum(wers[m]) / len(wers[m]) for m in wers}
    plt.bar(avg_wers.keys(), avg_wers.values(), color='skyblue')
    plt.title("Сравнение точности моделей (средний WER)")
    plt.ylabel("Средний WER")
    plt.xlabel("Модель")
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig("benchmark/plots/avg_wer.png")
    plt.show()

    return avg_wers

def wer_variance(plt, wers):
    plt.figure(figsize=(8, 5))
    wer_vars = {m: statistics.variance(w) if len(w) > 1 else 0 for m, w in wers.items()}
    plt.bar(wer_vars.keys(), wer_vars.values(), color='orange')
    plt.title("Стабильность моделей (дисперсия WER)")
    plt.ylabel("Дисперсия WER")
    plt.xlabel("Модель")
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig("benchmark/plots/wer_variance.png")
    plt.show()

    return wer_vars

def average_duration(durations):
    plt.figure(figsize=(8, 5))
    avg_durations = {m: sum(durations[m]) / len(durations[m]) for m in durations}
    plt.bar(avg_durations.keys(), avg_durations.values(), color='green')
    plt.title("Скорость обработки моделей (время в секундах)")
    plt.ylabel("Средняя длительность")
    plt.xlabel("Модель")
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig("benchmark/plots/avg_duration.png")
    plt.show()

    return avg_durations

def summary_chart(avg_wers, wer_vars, avg_durations):
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))

    axs[0].bar(avg_wers.keys(), avg_wers.values(), color='skyblue')
    axs[0].set_title("Средний WER")
    axs[0].set_ylabel("WER")
    axs[0].set_xlabel("Модель")
    axs[0].grid(True, axis='y')

    axs[1].bar(wer_vars.keys(), wer_vars.values(), color='orange')
    axs[1].set_title("Дисперсия WER")
    axs[1].set_ylabel("Дисперсия")
    axs[1].set_xlabel("Модель")
    axs[1].grid(True, axis='y')

    axs[2].bar(avg_durations.keys(), avg_durations.values(), color='green')
    axs[2].set_title("Средняя длительность")
    axs[2].set_ylabel("Секунды")
    axs[2].set_xlabel("Модель")
    axs[2].grid(True, axis='y')

    plt.suptitle("Объединённая визуализация бенчмарка")
    plt.tight_layout()
    plt.savefig("benchmark/plots/summary.png")
    plt.show()

if __name__ == "__main__":
    benchmark()
