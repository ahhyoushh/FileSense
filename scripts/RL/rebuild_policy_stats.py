import requests
from collections import defaultdict

SUPABASE_URL = "https://qesgmphseahmbeglltls.supabase.co"
SUPABASE_KEY = "sb_publishable_Gb4ZaeOsZZOvxsctFaFrjA_q0CXpaQV"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

EVENTS_TABLE = "rl_events"
STATS_TABLE = "rl_policy_stats"


def fetch_events():
    rows = []
    offset = 0

    while True:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/{EVENTS_TABLE}",
            headers=HEADERS,
            params={
                "select": "payload",
                "payload->>tfeedback": "not.is.null",
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
    print("[DEBUG] rewarded events fetched:", len(rows))

    if not rows:
        print("[ERROR] no rewarded events found")
        return

    stats = defaultdict(lambda: {"count": 0, "total": 0.0})

    for r in rows:
        payload = r["payload"]

        reward = float(payload["tfeedback"])
        policy_id = payload.get("policy_id", "unknown")

        stats[policy_id]["count"] += 1
        stats[policy_id]["total"] += reward

    # wipe old stats
    requests.delete(
        f"{SUPABASE_URL}/rest/v1/{STATS_TABLE}",
        headers=HEADERS,
        params={"policy_id": "not.is.null"},
        timeout=10,
    ).raise_for_status()

    payload_rows = [
        {
            "policy_id": pid,
            "count": s["count"],
            "avg_reward": round(s["total"] / s["count"], 4),
        }
        for pid, s in stats.items()
    ]

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{STATS_TABLE}",
        headers=HEADERS,
        json=payload_rows,
        timeout=10,
    )
    r.raise_for_status()

    print("[RL] policy stats rebuilt:", payload_rows)


if __name__ == "__main__":
    rebuild_policy_stats()
