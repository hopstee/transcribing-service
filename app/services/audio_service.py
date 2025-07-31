from faster_whisper import WhisperModel
from app.core.decorators import log_duration
import logging
import torch

if torch.cuda.is_available():
    torch.backends.cudnn.benchmark = True

class Transcriber:
    def __init__(self, model_name):
        self.with_cuda = torch.cuda.is_available()
        logging.info(f"\n\nЗагрузка модели: {model_name}")
        
        device = "cuda" if self.with_cuda else "cpu"
        print(f"\n\nУстройство: {device}\n\n")
        
        if self.with_cuda:
            compute_type = "float16"
        else:
            compute_type = "int8"
        
        self.model = WhisperModel(model_name, device=device, compute_type=compute_type)

    @log_duration("Обработка файла")
    def run(self, path: str):
        logging.info(f"\n\nОбработка файла: {path}")
        try:
            segments, info = self.model.transcribe(path, beam_size=5)
            text = " ".join(segment.text for segment in segments)
            
            return {"text": text}
                
        except Exception as e:
            logging.error(f"Ошибка при транскрипции {path}: {e}")
            return {"error": str(e)}

        finally:
            if self.with_cuda:
                torch.cuda.empty_cache()
            logging.info(f"Обработка файла {path} завершена")
