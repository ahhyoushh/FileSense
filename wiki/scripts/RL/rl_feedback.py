import time
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.logger.rl_logger import get_rl_logger
from scripts.RL.rl_config import GRACE_SECONDS


def find_file_by_name(filename: str, sorted_dir: Path) -> Optional[Path]:
    if not sorted_dir.exists():
        return None
    for p in sorted_dir.rglob(filename):
        return p
    return None


def reward_event(current_label: str, predicted: str, retries: int, manual_labelled: bool) -> float:
    reward = 0.0

    if current_label == predicted:
        reward += 1.0
    else:
        reward -= 1.0

    if predicted == "Uncategorized":
        reward -= 0.5

    if retries > 0:
        reward -= 0.1 * retries

    if manual_labelled:
        reward -= 0.3

    return round(reward, 3)


def run_feedback(sorted_dir_path: Optional[str] = None):
    rl = get_rl_logger()
    events = rl.load_events()
    now = int(time.time())

    sorted_dir = Path(sorted_dir_path) if sorted_dir_path else ROOT / "sorted"
    updated = []

    for ev in events:
        # Only process served events that haven't been rewarded yet
        if ev.get("event_type") != "served" or ev.get("tfeedback") is not None:
            updated.append(ev)
            continue

        if now - int(ev.get("timestamp", 0)) < GRACE_SECONDS:
            updated.append(ev)
            continue

        filename = ev.get("filename")
        if not filename:
            ev["feedback_note"] = "no_filename"
            updated.append(ev)
            continue

        path = find_file_by_name(filename, sorted_dir)
        if not path:
            ev["feedback_note"] = "file_not_found"
            updated.append(ev)
            continue

        current_label = path.parent.name
        predicted = ev.get("predicted_label")
        retries = int(ev.get("retries") or 0)
        manual = bool(ev.get("manual_labeled", False))

        ev["tfeedback"] = reward_event(
            current_label=current_label,
            predicted=predicted,
            retries=retries,
            manual_labelled=manual,
        )
        ev["tfeedback_timestamp"] = int(time.time())

        updated.append(ev)

    rl.overwrite_events(updated)


if __name__ == "__main__":
    run_feedback()
