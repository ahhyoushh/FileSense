import time
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import json

# Setup sys.path to include project root (FileSense)
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.logger.rl_logger import get_rl_logger
from scripts.RL.rl_policy import update_policy, _load_stats
from scripts.RL.rl_config import GRACE_SECONDS, RL_POLICY_STATS_FILE
from scripts.RL.rl_supabase import upload_policy_stats

def find_file_by_name(filename: str, sorted_dir: Path) -> Path | None:
    for p in sorted_dir.rglob(filename):
        return p
    return None


def reward_event(current_label: str, predicted: str, retries: int, manual_labelled) -> float:
    reward = 0.0
    if current_label == predicted:
        reward += 1.0
    if retries > 0:
        reward -= 0.1 * retries
    if manual_labelled:
        reward -= 0.3
    return max(0.0, reward)


def run_audit(sorted_dir_path: str | None = None) -> Tuple[int, int]:
    rl = get_rl_logger()
    events = rl.load_events()
    now = int(time.time())
    sorted_dir = Path(sorted_dir_path) if sorted_dir_path else Path(__file__).resolve().parent.parent / "sorted"
    updated: List[Dict] = []
    rewards_filled = 0

    for ev in events:
        if ev.get("event") != "served" or ev.get("reward") is not None:
            updated.append(ev)
            continue

        if now - ev.get("timestamp", 0) < GRACE_SECONDS:
            updated.append(ev)
            continue

        filename = ev.get("filename")
        if not filename:
            ev["note"] = "no_filename"
            updated.append(ev)
            continue

        path_found = None
        orig = ev.get("file_path")
        if orig:
            p = Path(orig)
            if p.exists():
                path_found = p

        if not path_found:
            path_found = find_file_by_name(filename, sorted_dir)

        if not path_found:
            ev["note"] = "file_not_found"
            updated.append(ev)
            continue

        current_label = path_found.parent.name
        predicted = ev.get("predicted_label")
        reward = reward_event(current_label, predicted, ev.get("retries", 0), ev.get("manual_labeled"))
        ev["reward"] = float(reward)
        ev["reward_timestamp"] = int(time.time())

        policy_id = ev.get("policy_id") or "policy_unknown"
        update_policy(policy_id, reward)
        rewards_filled += 1
        updated.append(ev)

    # write back updated events
    rl.overwrite_events(updated)

    # optionally push policy stats to Supabase
    try:
        stats = _load_stats()
        ok, err = upload_policy_stats(stats)
        if not ok:
            print("[supabase] upload_policy_stats failed:", err)
    except Exception as e:
        print("[rl_feedback] warning: failed to push stats to supabase:", e)

    return len(events), rewards_filled

if __name__ == "__main__":
    total, filled = run_audit()
    print(f"[rl_feedback] scanned={total}, rewards_filled={filled}")
