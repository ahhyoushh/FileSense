import json
import requests
from pathlib import Path
from typing import Tuple

SUPABASE_URL = "https://qesgmphseahmbeglltls.supabase.co"
SUPABASE_KEY = "sb_publishable_Gb4ZaeOsZZOvxsctFaFrjA_q0CXpaQV"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCAL_EVENTS_FILE = PROJECT_ROOT / "scripts" / "logs" / "rl_events.jsonl"


def _headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }


# -------------------------------------------------
# Upload a single event (ASCII-safe logging)
# -------------------------------------------------

def upload_event(event: dict):
    interaction_id = event.get("interaction_id")
    if not interaction_id:
        raise ValueError("event missing interaction_id")

    print(f"[supabase] uploading event: {interaction_id}")

    row = {
        "interaction_id": interaction_id,
        "payload": {k: v for k, v in event.items() if k != "interaction_id"},
    }

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/rl_events",
        headers=_headers(),
        json=row,
        timeout=10,
    )

    if r.status_code in (200, 201, 204):
        print(f"[supabase] upload success: {interaction_id}")
        return

    if "duplicate key value" in r.text.lower():
        print(f"[supabase] duplicate ignored: {interaction_id}")
        return

    print(f"[supabase] upload failed: {interaction_id} | {r.text}")
    raise RuntimeError(r.text)


# -------------------------------------------------
# Sync local JSONL -> Supabase
# -------------------------------------------------

def sync_local_to_supabase() -> Tuple[int, int]:
    if not LOCAL_EVENTS_FILE.exists():
        print("[supabase] no local events to sync")
        return 0, 0

    print("[supabase] syncing local events to Supabase")

    uploaded = 0
    failed = 0

    with open(LOCAL_EVENTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                event = json.loads(line)
            except Exception:
                failed += 1
                continue

            try:
                upload_event(event)
                uploaded += 1
            except Exception:
                failed += 1

    print(
        f"[supabase] sync complete | uploaded={uploaded} failed={failed}"
    )

    return uploaded, failed
