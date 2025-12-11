# scripts/RL/debug_rl_feedback.py
import json, time, os, sys
from pathlib import Path
# ensure project root on path when running directly
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.logger.rl_logger import get_rl_logger
from scripts.RL.rl_config import GRACE_SECONDS

now = int(time.time())
print("DEBUG RL FEEDBACK")
print("Now (epoch):", now)
print("GRACE_SECONDS:", GRACE_SECONDS)
print("Logs file exists:", (ROOT / "logs" / "rl_events.jsonl").exists())
print()

rl = get_rl_logger()
events = rl.load_events()
print("Total events loaded:", len(events))
print()

# show summary of latest 50 events (or fewer)
for i, ev in enumerate(events[-50:]):
    idx = len(events) - 50 + i if len(events) > 50 else i
    eid = ev.get("interaction_id")
    fname = ev.get("filename")
    evtype = ev.get("event")
    reward = ev.get("reward")
    ts = ev.get("timestamp", 0)
    age = now - ts
    path = ev.get("file_path")
    pred = ev.get("predicted_label")
    retries = ev.get("retries", 0)
    manual = bool(ev.get("manual_labeled", False))
    notes = ev.get("note", "")
    # existence check
    exists = False
    if path:
        try:
            exists = Path(path).exists()
        except Exception:
            exists = False

    print(f"[{idx}] id={eid} file={fname} event={evtype} reward={reward} ts={ts} age={age}s retries={retries} manual={manual} pred={pred} exists={exists} note={notes}")

print("\nNow checking which events WOULD be processed and WHY skipped:")
skipped_reasons = {}
for ev in events:
    # only served events
    if ev.get("event") != "served":
        skipped_reasons.setdefault("not_served", 0)
        skipped_reasons["not_served"] += 1
        continue
    if ev.get("reward") is not None:
        skipped_reasons.setdefault("already_has_reward", 0)
        skipped_reasons["already_has_reward"] += 1
        continue
    ts = ev.get("timestamp", 0)
    if now - ts < GRACE_SECONDS:
        skipped_reasons.setdefault("too_new_grace", 0)
        skipped_reasons["too_new_grace"] += 1
        continue
    # file lookup
    path = ev.get("file_path")
    found = False
    if path and Path(path).exists():
        found = True
    else:
        # brute force search under sorted/
        sorted_dir = ROOT / "sorted"
        if sorted_dir.exists():
            for p in sorted_dir.rglob(ev.get("filename") or ""):
                found = True
                break
    if not found:
        skipped_reasons.setdefault("file_not_found", 0)
        skipped_reasons["file_not_found"] += 1
        continue
    skipped_reasons.setdefault("would_process", 0)
    skipped_reasons["would_process"] += 1

print(json.dumps(skipped_reasons, indent=2))
