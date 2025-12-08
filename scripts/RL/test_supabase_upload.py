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
    "reward": None
}

# write local
rl.log_event(ev)
print("Wrote event to local JSONL.")

# immediate upload
ok, err = upload_event(ev)
print("Immediate upload:", ok, err)

# batch sync
s, f = sync_local_to_supabase()
print("Sync result:", s, f)
