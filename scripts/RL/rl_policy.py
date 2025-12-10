import json
import random
import time
from pathlib import Path
from typing import Dict

from .rl_config import POLICIES, EPSILON, RL_POLICY_STATS_FILE

RL_POLICY_STATS_FILE.parent.mkdir(parents=True, exist_ok=True)

def _init_stats() -> Dict[str, Dict]:
    stats = {pid: {"count": 0, "total_reward": 0.0, "last_updated": None} for pid in POLICIES}
    RL_POLICY_STATS_FILE.write_text(json.dumps(stats))
    return stats

def _load_stats() -> Dict[str, Dict]:
    try:
        if not RL_POLICY_STATS_FILE.exists():
            return _init_stats()
        return json.loads(RL_POLICY_STATS_FILE.read_text())
    except Exception:
        return _init_stats()

def _save_stats(stats: Dict[str, Dict]) -> None:
    RL_POLICY_STATS_FILE.write_text(json.dumps(stats, indent=2))

def choose_policy() -> str:
    stats = _load_stats()
    if random.random() < EPSILON:
        return random.choice(list(POLICIES.keys()))
    best = None
    best_avg = -1.0
    for pid, s in stats.items():
        cnt = s.get("count", 0)
        avg = 0.0 if cnt == 0 else s.get("total_reward", 0.0) / cnt
        if avg > best_avg:
            best_avg = avg
            best = pid
    return best or list(POLICIES.keys())[0]

def update_policy(policy_id: str, reward: float) -> None:
    stats = _load_stats()
    if policy_id not in stats:
        stats[policy_id] = {"count": 0, "total_reward": 0.0, "last_updated": None}
    stats[policy_id]["count"] += 1
    stats[policy_id]["total_reward"] += float(reward)
    stats[policy_id]["last_updated"] = int(time.time())
    _save_stats(stats)
