import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv()

from scripts.logger.rl_logger import get_rl_logger
from scripts.RL.rl_supabase import upload_event, sync_local_to_supabase
import time, json

rl = get_rl_logger()
ev = {
    "interaction_id": f"manual-{int(time.time())}",
    "event": "served",
    "timestamp": int(time.time()),
    "file_path": "/tmp/test.pdf",
    "filename": "test.pdf",
    "policy_id": "policy_B",
    "predicted_label": "math",
    "similarity_top1": 0.87,
    "top3_similarities": [0.87, 0.45, 0.22],
    "manual_labeled": False,
    "allowed_generation": True,
    "retries": 0,
    "file_ext": "pdf",
    "text_length": 123,
    "reward": None
}

print("Wrote event to local JSONL.")
rl.log_event(ev)

ok, err = upload_event(ev)
print("Immediate upload:", ok, err)

s, f = sync_local_to_supabase()
print("Sync result:", s, f)
