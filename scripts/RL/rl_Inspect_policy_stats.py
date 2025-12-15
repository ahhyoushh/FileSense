import requests

SUPABASE_URL = "https://qesgmphseahmbeglltls.supabase.co"
SUPABASE_KEY = "sb_publishable_Gb4ZaeOsZZOvxsctFaFrjA_q0CXpaQV"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

def inspect_policy_stats():
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/rl_policy_stats",
        headers=HEADERS,
        params={
            "select": "policy_id,count,avg_reward,created_at",
            "order": "created_at.desc",
        },
        timeout=10,
    )
    r.raise_for_status()

    rows = r.json()
    if not rows:
        print("No policy stats.")
        return

    latest_ts = rows[0]["created_at"]
    latest = [r for r in rows if r["created_at"] == latest_ts]

    print(f"\nPolicy snapshot @ {latest_ts}\n")
    for r in latest:
        print(
            f"{r['policy_id']:10s} | "
            f"count={r['count']:4d} | "
            f"avg_reward={r['avg_reward']:.4f}"
        )


if __name__ == "__main__":
    inspect_policy_stats()
