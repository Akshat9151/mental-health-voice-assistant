# utils/logger.py
import datetime
def log_message(sender, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {sender}: {message}")
