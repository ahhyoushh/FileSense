import time
import random
import requests

SUPABASE_URL = "https://qesgmphseahmbeglltls.supabase.co"
SUPABASE_KEY = "sb_publishable_Gb4ZaeOsZZOvxsctFaFrjA_q0CXpaQV"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

_CACHE = {"data": None, "ts": 0}
_TTL = 60
EPSILON = 0.1


def _load_policy_stats():
    now = time.time()
    if _CACHE["data"] and now - _CACHE["ts"] < _TTL:
        return _CACHE["data"]

    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/rl_policy_stats",
            headers=HEADERS,
            params={"select": "policy_id,avg_reward"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print("[RL] WARN: policy stats unavailable:", e)
        return []

    _CACHE["data"] = data
    _CACHE["ts"] = now
    return data


def choose_policy():
    stats = _load_policy_stats()
    if not stats:
        return "policy_A"

    if random.random() < EPSILON:
        return random.choice([s["policy_id"] for s in stats])

    return max(stats, key=lambda s: s["avg_reward"])["policy_id"]
