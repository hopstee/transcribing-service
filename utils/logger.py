import os
import logging

def setup_logging(log_file: str, level: str = "INFO", with_pid: bool = False):
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    log_format = (
        '[%(asctime)s] [%(process)d] %(levelname)s: %(message)s'
        if with_pid else
        '[%(asctime)s] %(levelname)s: %(message)s'
    )

    logging.basicConfig(
        level=logging.getLevelName(level),
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
