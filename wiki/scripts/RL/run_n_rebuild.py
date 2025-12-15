def main():
    print("[RUN] starting feedback + policy rebuild")

    # Step 1: run feedback locally
    print("[RUN] running feedback on local events")
    from scripts.RL.rl_feedback import run_feedback
    run_feedback()

    # Step 2: rebuild policy stats from Supabase
    print("[RUN] rebuilding policy stats")
    from scripts.RL.rebuild_policy_stats import rebuild_policy_stats
    rebuild_policy_stats()

    print("[RUN] feedback + policy rebuild complete")


if __name__ == "__main__":
    main()
