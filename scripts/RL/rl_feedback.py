import time
import sys
from pathlib import Path
from typing import Optional
import requests

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.RL.rl_config import GRACE_SECONDS

# ---------------- Supabase ----------------
SUPABASE_URL = "https://qesgmphseahmbeglltls.supabase.co"
SUPABASE_KEY = "sb_publishable_Gb4ZaeOsZZOvxsctFaFrjA_q0CXpaQV"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

EVENTS_TABLE = "rl_events"


# ---------------- Helpers ----------------
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


def patch_event(interaction_id: str, reward: float):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{EVENTS_TABLE}",
        headers=HEADERS,
        params={"interaction_id": f"eq.{interaction_id}"},
        json={
            "payload": {
                "tfeedback": reward,
                "tfeedback_timestamp": int(time.time()),
            }
        },
        timeout=10,
    )
    r.raise_for_status()


# ---------------- Main ----------------
def run_feedback(sorted_dir_path: Optional[str] = None):
    # Pull unrewarded events DIRECTLY from Supabase
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/{EVENTS_TABLE}",
        headers=HEADERS,
        params={
            "select": "interaction_id,payload",
            "payload->>tfeedback": "is.null",
        },
        timeout=15,
    )
    r.raise_for_status()

    rows = r.json()
    if not rows:
        print("[RL] no unrewarded events found")
        return

    now = int(time.time())
    sorted_dir = Path(sorted_dir_path) if sorted_dir_path else ROOT / "sorted"

    updated = 0

    for row in rows:
        interaction_id = row["interaction_id"]
        payload = row.get("payload") or {}

        if payload.get("event_type") != "served":
            continue

        ts = int(payload.get("timestamp", 0))
        if now - ts < GRACE_SECONDS:
            continue

        filename = payload.get("filename")
        if not filename:
            continue

        path = find_file_by_name(filename, sorted_dir)
        if not path:
            continue

        reward = reward_event(
            current_label=path.parent.name,
            predicted=payload.get("predicted_label"),
            retries=int(payload.get("retries") or 0),
            manual_labelled=bool(payload.get("manual_labeled", False)),
        )

        patch_event(interaction_id, reward)
        updated += 1

    print(f"[RL] rewarded events patched: {updated}")


if __name__ == "__main__":
    run_feedback()
