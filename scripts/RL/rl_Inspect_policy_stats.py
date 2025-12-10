import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rl_config import RL_POLICY_STATS_FILE as STATS_FILE

def print_stats():
    if not Path(STATS_FILE).exists():
        print("No stats file found.")
        return
    stats = json.loads(Path(STATS_FILE).read_text())
    for pid, s in stats.items():
        cnt = s.get("count", 0)
        total = s.get("total_reward", 0.0)
        avg = 0.0 if cnt == 0 else total / cnt
        print(f"{pid}: count={cnt}, total_reward={total}, avg={avg:.3f}")

if __name__ == "__main__":
    print_stats()
