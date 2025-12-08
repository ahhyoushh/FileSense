import json
import time
from pathlib import Path
import threading

class RLLogger:
    def __init__(self):
        self.lock = threading.Lock()
        self.base_dir = Path(__file__).resolve().parent
        self.logs_dir = self.base_dir.parent / "logs" / "RL"
        self.logs_dir.mkdir(exist_ok=True)
        self.events_path = self.logs_dir / "rl_events.jsonl"

    def log_event(self, event: dict):
        event.setdefault("timestamp", int(time.time()))
        json_line = json.dumps(event, default=str, ensure_ascii=False)
        with self.lock:
            with open(self.events_path, "a", encoding="utf-8") as f:
                f.write(json_line + "\n")

    def load_events(self):
        if not self.events_path.exists():
            return []
        events = []
        with self.lock:
            with open(self.events_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        continue
        return events

    def overwrite_events(self, events_list):
        with self.lock:
            with open(self.events_path, "w", encoding="utf-8") as f:
                for ev in events_list:
                    f.write(json.dumps(ev, default=str, ensure_ascii=False) + "\n")

_rl_logger_instance = None

def get_rl_logger():
    global _rl_logger_instance
    if _rl_logger_instance is None:
        _rl_logger_instance = RLLogger()
    return _rl_logger_instance
