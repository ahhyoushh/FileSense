import os
from pathlib import Path

POLICIES = {
    "policy_A": {"THRESHOLD": 0.45, "LOW_CONF": 0.40, "FILENAME_BOOST": 0.15, "TEXT_BOOST": 0.08, "ALLOW_GENERATION": True},
    "policy_B": {"THRESHOLD": 0.40, "LOW_CONF": 0.30, "FILENAME_BOOST": 0.20, "TEXT_BOOST": 0.10, "ALLOW_GENERATION": True},
    "policy_C": {"THRESHOLD": 0.35, "LOW_CONF": 0.25, "FILENAME_BOOST": 0.25, "TEXT_BOOST": 0.12, "ALLOW_GENERATION": False},
}

# runtime settings
EPSILON = float(os.getenv("RL_EPSILON", 0.10))
MIN_SAMPLES_PER_ARM = int(os.getenv("RL_MIN_SAMPLES", 5))
GRACE_SECONDS = int(os.getenv("RL_GRACE_SECONDS", 3600))

# Logging paths
BASE = Path(__file__).resolve().parent.parent  
LOGS_DIR = BASE / "logs"
LOGS_DIR.mkdir(exist_ok=True)

SUPABASE_POLICY_STATS_TABLE = os.getenv("SUPABASE_POLICY_STATS_TABLE", "rl_policy_stats") #Later pushing stats to supabase

RL_EVENTS_JSONL = LOGS_DIR / "rl_events.jsonl"
RL_POLICY_STATS_FILE = LOGS_DIR / "rl_policy_stats.json"
