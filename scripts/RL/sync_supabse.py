"""
Sync ALL local RL data (events + policy stats) to Supabase.

Expected layout:
FileSense/
└─ scripts/
   └─ logs/
      ├─ rl_events.jsonl
      └─ rl_policy_stats.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# ------------------------------------------------------------------
# Resolve project root: FileSense/
# sync_all.py -> scripts/RL/ -> parents[2]
# ------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ------------------------------------------------------------------
# Local paths (EXPLICIT, NO MAGIC)
# ------------------------------------------------------------------
LOGS_DIR = ROOT / "scripts" / "logs"
EVENTS_FILE = LOGS_DIR / "rl_events.jsonl"
POLICY_STATS_FILE = LOGS_DIR / "rl_policy_stats.json"

# ------------------------------------------------------------------
# Supabase helpers (your existing code)
# ------------------------------------------------------------------
from scripts.RL.rl_supabase import (
    upload_events_batch,
    upload_policy_stats,
)

# ------------------------------------------------------------------
# Loaders
# ------------------------------------------------------------------
def load_events(path: Path):
    events = []
    if not path.exists():
        return events

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except Exception:
                pass
    return events


def load_policy_stats(path: Path) -> Dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[ERROR] Failed to parse policy stats: {e}")
        return None


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main():
    print("\n[SYNC] FileSense → Supabase\n")

    # ---------------- events ----------------
    events = load_events(EVENTS_FILE)

    if not events:
        print("[EVENTS] No local events found")
    else:
        uploaded, failed = upload_events_batch(events)
        print("[EVENTS]")
        print(f"  Uploaded : {uploaded}")
        print(f"  Failed   : {failed}")

    # ---------------- policy stats ----------------
    stats = load_policy_stats(POLICY_STATS_FILE)

    if not stats:
        print("\n[POLICY STATS] No local policy stats found")
    else:
        ok, err = upload_policy_stats(stats)
        print("\n[POLICY STATS]")
        if ok:
            print("  Uploaded latest snapshot")
        else:
            print(f"  Upload failed: {err}")

    print("\n[SYNC] Done.\n")


if __name__ == "__main__":
    main()
