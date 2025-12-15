import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.RL.rl_supabase import upload_event

LOGS_DIR = ROOT / "scripts" / "logs"
EVENTS_FILE = LOGS_DIR / "rl_events.jsonl"


def load_events(path: Path):
    events = []
    if not path.exists():
        return events

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except Exception:
                pass

    return events


def main():
    events = load_events(EVENTS_FILE)
    if not events:
        print("[SYNC] No events to upload.")
        return

    uploaded = 0
    failed = 0

    for ev in events:
        try:
            upload_event(ev)
            uploaded += 1
        except Exception as e:
            # duplicate interaction_id → safe to ignore
            if "duplicate key value" in str(e).lower():
                continue
            failed += 1
            print("[SYNC] upload failed:", e)

    print(f"[SYNC] Events uploaded={uploaded}, failed={failed}")


if __name__ == "__main__":
    main()
