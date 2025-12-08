import os
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

import requests

# read env vars (use dotenv in your main to load .env)
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET", "")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "rl_events")

BASE = Path(__file__).resolve().parent.parent
LOCAL_JSONL = BASE / "logs" / "rl_events.jsonl"

def _headers() -> Dict[str, str]:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

def _table_url() -> str:
    return f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"

def upload_event(event: Dict[str, Any]) -> Tuple[bool, str | None]:
    """
    Upload a single event to Supabase.
    Returns (success, error_message_or_none).
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False, "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing in env"

    row: Dict[str, Any] = {
        "interaction_id": event.get("interaction_id"),
        "event_type": event.get("event"),
        "filename": event.get("filename"),
        "file_path": event.get("file_path"),
        "policy_id": event.get("policy_id"),
        "predicted_label": event.get("predicted_label"),
        "similarity": event.get("similarity_top1") or event.get("similarity"),
        "payload": json.dumps(event, ensure_ascii=False)
    }

    try:
        resp = requests.post(_table_url(), headers=_headers(), json=row, timeout=15)
        if resp.status_code in (200, 201, 204):
            return True, None
        return False, f"HTTP {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, str(e)

def upload_events_batch(events: List[Dict[str, Any]]) -> Tuple[int, int]:
    """
    Upload multiple events in a single request.
    Returns (success_count, fail_count).
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return 0, len(events)

    rows: List[Dict[str, Any]] = []
    for ev in events:
        rows.append({
            "interaction_id": ev.get("interaction_id"),
            "event_type": ev.get("event"),
            "filename": ev.get("filename"),
            "file_path": ev.get("file_path"),
            "policy_id": ev.get("policy_id"),
            "predicted_label": ev.get("predicted_label"),
            "similarity": ev.get("similarity_top1") or ev.get("similarity"),
            "payload": json.dumps(ev, ensure_ascii=False)
        })

    try:
        resp = requests.post(_table_url(), headers=_headers(), json=rows, timeout=30)
        if resp.status_code in (200, 201, 204):
            return len(rows), 0
        return 0, len(rows)
    except Exception:
        return 0, len(rows)

def sync_local_to_supabase(local_jsonl_path: str | None = None) -> Tuple[int, int]:
    path = Path(local_jsonl_path) if local_jsonl_path else LOCAL_JSONL
    if not path.exists():
        return 0, 0

    events: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except Exception:
                pass

    if not events:
        return 0, 0

    success, fail = upload_events_batch(events)
    return success, fail
