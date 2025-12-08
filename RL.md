# Reinforcement Learning

## Events:
### classification: action chosen, prediction done.(null reward )(served)
### feedback: Fill reward on previous event by user action(audit)
---
## Action: Chosen policy by the system
---
### Policy: configuration 
rl_config.py
```bash
POLICIES = {
    "policy_A": {"THRESHOLD": 0.45, "LOW_CONF": 0.40, "FILENAME_BOOST": 0.15, "TEXT_BOOST": 0.08, "ALLOW_GENERATION": True},
    "policy_B": {"THRESHOLD": 0.40, "LOW_CONF": 0.30, "FILENAME_BOOST": 0.20, "TEXT_BOOST": 0.10, "ALLOW_GENERATION": True},
    "policy_C": {"THRESHOLD": 0.35, "LOW_CONF": 0.25, "FILENAME_BOOST": 0.25, "TEXT_BOOST": 0.12, "ALLOW_GENERATION": False},
}```
---
## State: (optional at v1) Features recorded at first serve 
---
### Features: file_ext, text length, file_name_labels,timestamps,et 
---
## Agent/Bandit: Simple decision maker **(epsilon-greedy)**
---
## Log store: rl_events.jsonl, rl_policy_status.jsonl , etc
---

# FLOW

                 ┌────────────────────┐
                 │ 1. Choose Policy   │
                 │  (ε-greedy bandit) │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │ 2. Run FileSense   │
                 │  Classification     │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │ 3. Get Prediction  │
                 │  (label + sim)     │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌──────────────────────────┐
                 │ 4. Log "served" event    │
                 │  (interaction_id,        │
                 │   policy, prediction,    │
                 │   reward = null)         │
                 └─────────┬───────────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │ 5. Move File       │
                 └─────────┬──────────┘
                           │
                           ▼
        ┌──────────────────────────────────────────┐
        │ 6. Audit Phase (later)                   │
        │   - Find current file location           │
        │   - Compare with predicted label         │
        │   - Compute reward (1 or 0)              │
        └─────────┬────────────────────────────────┘
                  │
                  ▼
        ┌──────────────────────────────────────────┐
        │ 7. Update Event + Policy Stats           │
        │   - Write reward back to log             │
        │   - Update bandit stats for policy       │
        └─────────┬────────────────────────────────┘
                  │
                  ▼
        ┌──────────────────────────────────────────┐
        │ 8. Next Classification Uses Updated Stats │
        │   → Better policies chosen more often     │
        └──────────────────────────────────────────┘

---

## PSUEDO CODE
```bash
# serve time
interaction_id = f"{filename}|{now}"
policy = choose_policy()             # ε-greedy
cfg = POLICIES[policy]
predicted, sim = classify_with_cfg(text, filename, cfg)
log_event({..., "interaction_id": interaction_id, "policy_id": policy, "predicted_label": predicted, "similarity": sim, "reward": None})
move_file_to_sorted(file_path, predicted)

# audit (periodic)
events = load_events()
for ev in events with ev["reward"] is None and now - ev["timestamp"] > GRACE:
    path_found = find_file(ev["filename"])
    if not found: continue
    current_label = parent_folder(path_found)
    reward = 1.0 if current_label == ev["predicted_label"] else 0.0
    ev["reward"] = reward
    update_policy(ev["policy_id"], reward)
save_events(events)
```

---

## EPSILON GREEDY
### What is ε-Greedy? (Simple Explanation)

#### ε-greedy (epsilon-greedy) is the simplest and most practical reinforcement learning strategy for real apps like FileSense.

### It works like this:

#### At each decision:

#### With probability ε (epsilon):
```
→ Explore → pick a random policy
```
### With probability 1 - ε:
```
→ Exploit → pick the best-performing policy so far
```
### Example:
```
If ε = 0.10 (10%):

10% of the time you try a random policy

90% of the time you pick the policy with the highest average reward
```
### Why it works:
```
Exploration ensures you don’t get stuck using a suboptimal policy

Exploitation ensures you use the best-known policy most of the time

Over time, the system learns which policies work best

In FileSense:

ε-greedy controls:

How aggressive or conservative the classification should be

Which threshold/boost configuration produces the most accurate results

Continual improvement with zero developer tuning
```