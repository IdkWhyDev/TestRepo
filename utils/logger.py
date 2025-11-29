from datetime import datetime
from config.config import Config


def logger(message):
    timestamped_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
    with open(Config.LOG_PATH, "a", encoding="utf-8") as f:
        f.write(timestamped_message)
