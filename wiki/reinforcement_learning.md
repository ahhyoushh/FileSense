---
title: "Reinforcement Learning Architecture"
permalink: /wiki/rl/
---

# Reinforcement Learning & The Rate Limit Bottleneck
 
 ## 🚨 Critical Analysis: Why the API Approach Failed
 
 ### 1. The Bottleneck: API Quotas & Latency
 Despite implementing an intelligent RL agent (Epsilon-Greedy Bandit) to minimize API calls (Policy C), the dependency on Google Gemini's API proved fatal for the project's scalability.
 
 **Evidence from Logs (`RL_init.log`, `RL_RATE_LIMIT_RAGEBAIT.log`):**
 *   **Severe Rate Limiting (429 RESOURCE_EXHAUSTED):**
     > `Error: 429 RESOURCE_EXHAUSTED ... limit: 20 requests/day ... Please retry in 43.82s`
     The free/standard tier limits are far too low for a file organizer that might process hundreds of files. A limit of ~20 requests forces the system to sleep more than it works.
 
 *   **Service Unavailability (503 UNAVAILABLE):**
     > `Error: 503 UNAVAILABLE ... The model is overloaded.`
     Even within the quota, the model frequently failed to respond, triggering retry loops that added 10-20 seconds of delay per file.
 
 *   **Unacceptable Latency:**
     The retry logic and backoff strategies blew up processing times:
     *   `file_005.txt`: **57.45s**
     *   `file_003.txt`: **70.12s**
     *   `file_004.txt`: **96.77s**
     *   `file_007.txt`: **123.44s**
     
     *Compare this to Vector Search (Policy C):* `~0.50s` per file.
 
 ### 2. Failure of the RL "Fix"
 The RL agent correctly identified **Policy C (No GenAI)** as the optimal policy because it had the highest reward (speed + no errors). However, when the system *did* need to generate a new label (Exploration or Low Confidence), the API failure broke the entire loop.
 
 *   **The "Gap":** We cannot rely on the API even for the 10% "Explore" cases without risking a 60-second freeze.
 *   **Manual Fallback:** The logs show the system constantly asking the user for manual input (`Please manually input the folder label`), essentially defeating the purpose of an *automatic* organizer.
 
 ---
 
 ## 🛑 Strategic Shift: Supervised Fine-Tuning (SFT)
 
 **Problem:** We need the intelligence of an LLM to generate labels for unknown files, but we cannot afford the latency or rate limits of an API.
 **Solution:** **Supervised Fine-Tuning (SFT)** a local Small Language Model (SLM).
 
 ### Why SFT?
 1.  **Zero Latency:** A local model (e.g., Llama-3-8B-Quantized or TinyLlama) running on the GPU/CPU has no network overhead.
 2.  **No Rate Limits:** We can classify 10,000 files in a row without asking permission or waiting for quotas.
 3.  **Privacy:** File contents never leave the user's machine.
 
 ### The Plan
 1.  **Data Collection:** We have collected high-quality "Event" data in `rl_events.jsonl` (Input Text -> Predicted Label).
 2.  **Dataset Creation:** Format these events into an SFT dataset (Instruction Tuning format).
     *   *Input:* "Classify this text: {content_summary}"
     *   *Output:* "{label}"
 3.  **Fine-Tuning:** Train a small, efficient model to replicate the decision-making of the larger Gemini model.
 4.  **Deployment:** Replace the `generate_label.py` API calls with a local inference function.
 
 ---
 
 ## 📜 Original Architecture (Reference)
 
 ### Strategy: Epsilon-Greedy Bandit
 *   **Action:** Choose a Policy (A, B, or C).
 *   **Reward:** 1 (Success/Correct Sort) or 0 (Failure/Manual Fix).
 *   **Goal:** Maximize cumulative reward over time.
 
 ### Policies
 | Policy | Threshold | Allow GenAI? | Description |
 |:---:|:---:|:---:|---|
 | **A** | 0.45 | **Yes** | Conservative. High overlap required. |
 | **B** | 0.40 | **Yes** | Balanced. |
 | **C** | 0.35 | **No**  | **Efficient.** Aggressive matching. Pure Vector Search. |
 
 *(Note: While logical, this architecture is currently paused in favor of the SFT migration.)*
