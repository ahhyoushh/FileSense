import requests
from collections import defaultdict

SUPABASE_URL = "https://qesgmphseahmbeglltls.supabase.co"
SUPABASE_KEY = "sb_publishable_Gb4ZaeOsZZOvxsctFaFrjA_q0CXpaQV"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}


def fetch_events():
    rows = []
    offset = 0

    while True:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/rl_events",
            headers=HEADERS,
            params={
                "select": "payload",
                "limit": 1000,
                "offset": offset,
            },
            timeout=30,
        )
        r.raise_for_status()

        batch = r.json()
        if not batch:
            break

        rows.extend(batch)
        offset += 1000

    return rows


def rebuild_policy_stats():
    print("[RL] rebuilding policy stats")

    rows = fetch_events()
    stats = defaultdict(lambda: {"count": 0, "total": 0.0})

    for r in rows:
        payload = r.get("payload") or {}

        reward = payload.get("tfeedback")
        if reward is None:
            continue

        policy_id = payload.get("policy_id", "unknown")
        stats[policy_id]["count"] += 1
        stats[policy_id]["total"] += float(reward)

    # 🔥 REST-safe table wipe (PostgREST requires a filter)
    requests.delete(
        f"{SUPABASE_URL}/rest/v1/rl_policy_stats",
        headers=HEADERS,
        params={"id": "not.is.null"},
        timeout=30,
    ).raise_for_status()

    payload_rows = [
        {
            "policy_id": pid,
            "count": s["count"],
            "avg_reward": round(s["total"] / s["count"], 4),
        }
        for pid, s in stats.items()
    ]

    if payload_rows:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/rl_policy_stats",
            headers=HEADERS,
            json=payload_rows,
            timeout=30,
        ).raise_for_status()

    print("[RL] rebuild complete")


if __name__ == "__main__":
    rebuild_policy_stats()
