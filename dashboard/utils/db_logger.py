# 로깅 설정
import logging
import os
from datetime import datetime

logging.basicConfig(handlers=[], levle=logging.NOTSET)
root_logger = logging.getLogger()
root_logger.handlers.clear()


LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs"
)
os.makedirs(LOG_DIR, exist_ok=True)
today_str = datetime.now().strftime("%Y-%m-%d")
log_filename = os.path.join(LOG_DIR, f"{today_str}database.log")


logger = logging.getLogger("DatabaseLogger")
logger.setLevel(logging.INFO)

logger.handlers.clear()
logger.propagate = False

# if logger.hasHandlers():
#    logger.handlers.clear()

file_handler = logging.FileHandler(log_filename, mode="w", encoding="utf-8")
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)


logger.addHandler(file_handler)
