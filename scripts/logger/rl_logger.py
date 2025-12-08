import json
import time
from pathlib import Path
import threading
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)
RL_EVENTS_JSONL = LOGS_DIR / "rl_events.jsonl"

class RLLogger:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.events_path = RL_EVENTS_JSONL
        self.events_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event: Dict[str, Any]) -> None:
        ev = dict(event)
        ev.setdefault("timestamp", int(time.time()))

        # sanitize non-serializable values
        for k, v in list(ev.items()):
            try:
                json.dumps(v)
            except Exception:
                ev[k] = str(v)

        line = json.dumps(ev, ensure_ascii=False)

        with self.lock:
            with open(self.events_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")

    def load_events(self) -> List[Dict[str, Any]]:
        if not self.events_path.exists():
            return []
        events: List[Dict[str, Any]] = []
        with self.lock:
            with open(self.events_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        pass
        return events

    def overwrite_events(self, events_list: List[Dict[str, Any]]) -> None:
        with self.lock:
            with open(self.events_path, "w", encoding="utf-8") as f:
                for ev in events_list:
                    f.write(json.dumps(ev, ensure_ascii=False) + "\n")

_rl_logger_instance: RLLogger | None = None

def get_rl_logger() -> RLLogger:
    global _rl_logger_instance
    if _rl_logger_instance is None:
        _rl_logger_instance = RLLogger()
    return _rl_logger_instance
