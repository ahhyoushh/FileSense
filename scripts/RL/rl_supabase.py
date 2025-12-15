import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple

from dotenv import load_dotenv
load_dotenv()

import requests


# REPLACED ENV VARS WITH CONFIG CONSTANTS
SUPABASE_URL = "https://qesgmphseahmbeglltls.supabase.co"
SUPABASE_KEY = "sb_publishable_Gb4ZaeOsZZOvxsctFaFrjA_q0CXpaQV"
SUPABASE_TABLE = "rl_events"
SUPABASE_POLICY_STATS_TABLE = "rl_policy_stats"


BASE = Path(__file__).resolve().parent.parent
LOCAL_JSONL = BASE / "logs" / "rl_events.jsonl"

def _headers() -> Dict[str, str]:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

def _table_url(table: str) -> str:
    return f"{SUPABASE_URL}/rest/v1/{table}"

def upload_event(event: Dict[str, Any]) -> Tuple[bool, str | None]:
    """
    Upload a single event to Supabase. Maps event fields to table columns.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False, "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing"

    row = {
        "interaction_id": event.get("interaction_id"),
        "event_type": event.get("event"),
        "filename": event.get("filename"),
        "file_path": event.get("file_path"),
        "policy_id": event.get("policy_id"),
        "predicted_label": event.get("predicted_label"),
        "similarity": float(event.get("similarity_top1") or event.get("similarity") or 0.0),
        "top3_similarities": json.dumps(event.get("top3_similarities") or []),  # store as json string if using text column, or as jsonb if DB supports
        "retries": int(event.get("retries") or 0),
        "manual_labeled": bool(event.get("manual_labeled") or False),
        "payload": json.dumps(event, ensure_ascii=False)
    }

    try:
        resp = requests.post(_table_url(SUPABASE_TABLE), headers=_headers(), json=row, timeout=15)
        if resp.status_code in (200, 201, 204):
            return True, None
        return False, f"HTTP {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, str(e)


def upload_events_batch(events: List[Dict[str, Any]]) -> Tuple[int, int]:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return 0, len(events)

    rows = []
    for ev in events:
        rows.append({
            "interaction_id": ev.get("interaction_id"),
            "event_type": ev.get("event"),
            "filename": ev.get("filename"),
            "file_path": ev.get("file_path"),
            "policy_id": ev.get("policy_id"),
            "predicted_label": ev.get("predicted_label"),
            "similarity": float(ev.get("similarity_top1") or ev.get("similarity") or 0.0),
            "top3_similarities": json.dumps(ev.get("top3_similarities") or []),
            "retries": int(ev.get("retries") or 0),
            "manual_labeled": bool(ev.get("manual_labeled") or False),
            "payload": json.dumps(ev, ensure_ascii=False),
        })

    try:
        resp = requests.post(_table_url(SUPABASE_TABLE), headers=_headers(), json=rows, timeout=30)
        if resp.status_code in (200, 201, 204):
            return len(rows), 0
        return 0, len(rows)
    except Exception:
        return 0, len(rows)


def sync_local_to_supabase(local_jsonl_path: str | None = None) -> Tuple[int, int]:
    path = Path(local_jsonl_path) if local_jsonl_path else LOCAL_JSONL
    if not path.exists():
        return 0, 0
    events = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except Exception:
                pass
    if not events:
        return 0, 0
    return upload_events_batch(events)


def upload_policy_stats(stats: Dict[str, Any]) -> Tuple[bool, str | None]:
    """
    Insert current policy stats into SUPABASE_POLICY_STATS_TABLE.
    Table schema example: id bigserial, created_at timestamptz default now(), payload jsonb
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False, "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing"

    row = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "payload": json.dumps(stats, ensure_ascii=False),
    }

    try:
        resp = requests.post(_table_url(SUPABASE_POLICY_STATS_TABLE), headers=_headers(), json=row, timeout=15)
        if resp.status_code in (200, 201, 204):
            return True, None
        return False, f"HTTP {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, str(e)
