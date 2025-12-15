---
title: "Reinforcement Learning Architecture"
permalink: /wiki/rl/
---

# Reinforcement Learning Integration

## 🧠 The Epsilon-Greedy Bandit Agent
FileSense has permanently evolved from a static script to an **adaptive intelligent system**. Integrated a **Reinforcement Learning (RL)** agent based on the **Epsilon-Greedy Bandit** algorithm.

### Core Logic
The agent's goal is to maximize **Accuracy** while minimizing **Latency** and **API Costs**. It achieves this by dynamically choosing between three operating policies for every file it encounters:

| Policy | Threshold | Allow GenAI? | Description |
|:---:|:---:|:---:|---|
| **A** | 0.45 | **Yes** | **Conservative.** Requires high similarity to exist. Uses API frequently for new concepts. |
| **B** | 0.40 | **Yes** | **Balanced.** A middle ground between strictness and autonomy. |
| **C** | 0.35 | **No**  | **Efficient.** Aggressive vector matching. Strictly forbids API calls to ensure speed. |

### The Learning Loop
1.  **State:** The system observes a new file.
2.  **Action:** The Agent selects a policy (A, B, or C).
    *   *Exploration:* Tries random policies to discover new efficiencies (Epsilon = 10%).
    *   *Exploitation:* Chooses the best-known policy for reliability (90%).
3.  **Reward:** 
    *   **+1 (Success):** File was sorted correctly without manual intervention.
    *   **0 (Failure):** File required manual sorting or API failed.

---

## 🚧 The Rate Limit Bottleneck (Why paused)

While the RL architecture is sound and fully implemented, I hit a **hard external constraint** during real-world testing.

### The Conflict: RL Speed vs. API Limits
Reinforcement Learning requires rapid feedback loops (trial and error) to converge on an optimal policy. However, the **free tier of Google Gemini API** imposes severe rate limits (~15 RPM or fewer depending on load).

**Evidence from Logs:**
> `Error: 429 RESOURCE_EXHAUSTED ... limit: 20 requests/day ... Please retry in 43.82s`

When the RL agent attempted to "Explore" (use GenAI) or when valid files needed labeling, the API would block the request for 40-60 seconds. This destroyed the reward signal:
*   The Agent successfully prioritized **Policy C** (No API) because it was the only one that didn't crash.
*   However, I *need* GenAI for that 10% of unknown files. Can't simply turn it off.

### Conclusion: The Architecture works, the Infrastructure failed.
The RL implementation works perfectly: it correctly identified that API calls were "expensive" (in time). The problem is that the "cost" (60s wait) was too high for a production application.

---

## 🛑 Strategic Shift: Local SFT

To unblock the RL capabilities, I'm removing the bottleneck.

**The Solution: Supervised Fine-Tuning (SFT)**
Moving the intelligence from the Cloud (Gemini) to the Edge (Local LLM).
1.  **Fine-Tune a Local Model (Llama-3-8B):** Using the data collected by the RL agent.
2.  **Remove API Dependency:** Local models have no rate limits.
3.  **Re-Activate RL:** Once the "cost" of generation drops from 60s to 2s, the RL Agent will be fully re-enabled to manage local compute resources instead of API quotas.

**The RL module remains a permanent, core part of FileSense's codebase, awaiting the local model integration.**
