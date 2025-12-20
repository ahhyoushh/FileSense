---
title: "FileSense Documentation"
layout: page
permalink: /wiki/
excerpt: "Intelligent semantic file organizer powered by SBERT embeddings and Gemini AI"
---

**Semantic document classifier that understands meaning, not just filenames.**

FileSense uses **SentenceTransformers (SBERT)** and **FAISS vector search** to organize files by their actual content. When it encounters unknown file types, it leverages **Google Gemini** (or Local LLMs) to generate new categories automatically.

---

## UPDATE: Infrastructure Shift to SFT

**Integrated a Reinforcement Learning architecture.** However, due to Google Gemini's Free Tier Rate Limits, I am temporarily pivoting the *generation* backend to Local SFT.

### The Challenge
The **RL Agent** works as intended, optimizing for speed. However, effectively "training" the agent requires frequent API calls, which triggers Google's **429 Rate Limit**, forcing 60-second delays.

### The Solution
Not removing RL, just **removing the latency**.
By switching to **Supervised Fine-Tuning (SFT)** of a local model, I eliminate the API bottleneck. This will allow the RL Agent to function at full speed without external throttling.

See the full analysis: **[Reinforcement Learning Architecture](/FileSense/wiki/rl/)**

---

## Quick Links

*   **[Getting Started](/FileSense/wiki/getting-started/)**: Install and run FileSense in 5 minutes
*   **[Performance Metrics](/FileSense/wiki/metrics/)**: See benchmarks and optimization studies
*   **[RL Architecture](/FileSense/wiki/rl/)**: Deep dive into the Adaptive Agent

---

## Core Features

| Feature | Description |
|---------|-------------|
| Semantic Sorting | Classifies by meaning (e.g., "Newton's Laws" → Physics) |
| Reinforcement Learning | Adaptive agent that optimizes sorting policies over time |
| AI-Powered Labeling | Uses GenAI to create new categories automatically |
| FAISS Vector Search | Lightning-fast similarity matching with embeddings |
| Self-Updating | Automatically rebuilds index when new labels are created |
| OCR Support | Extracts text from scanned PDFs and images |
| Keyword Boosting | Hybrid approach: Vector similarity + keyword matching |
| GUI & CLI | Desktop app with system tray + command-line interface |

---

## How It Works

```mermaid
flowchart TD
    A[Input File] --> B[Extract Text]
    B --> C[Generate Embedding<br/>SBERT BAAI/bge-base-en-v1.5]
    C --> D{Similarity >= 0.40?}
    D -->|Yes| E[Classify to Existing Folder]
    D -->|No| F[Ask Agent (RL)]
    F --> G{Policy A/B/C?}
    G --> H[Update folder_labels.json]
    H --> I[Rebuild FAISS Index]
    I --> J[Move to Sorted Folder]
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up API key
echo "API_KEY=your_gemini_key" > .env

# 3. Create initial index
python scripts/create_index.py

# 4. Run FileSense
python scripts/script.py --dir ./files --threads 6
```

---

## Documentation Sections

### For Users
- **[Getting Started](/FileSense/wiki/getting-started/)** - Installation and setup
- **[FAQ](/FileSense/wiki/faq/)** - Common questions and troubleshooting

### For Developers
- **[Architecture](/FileSense/wiki/pipeline/)** - System design and data flow


### Research & Analysis
- **[Performance Metrics](/FileSense/wiki/metrics/)** - Benchmarks and accuracy
- **[Reinforcement Learning](/FileSense/wiki/rl/)** - Architecture & SFT Pivot
- **[NL vs Keywords Study](/FileSense/wiki/NL_VS_OG/)** - Comprehensive comparison
- **[Lessons Learned](/FileSense/wiki/lessons-learned/)** - Key insights from development

---

## Key Insights

> **Important discoveries from testing:**
> 
> 1. **Keyword-based descriptions outperform natural language** for SBERT embeddings (+32% accuracy)
> 2. **Semantic descriptions performed worse** than expected (24% vs 56% accuracy)
> 3. **Lighter models significantly reduced performance** - I recommend sticking with BAAI/bge-base-en-v1.5
> 4. **AG News dataset showed poor results** - academic documents work best

See the [NL vs Keywords Study](/FileSense/wiki/NL_VS_OG/) for detailed analysis.

---

## Performance Highlights

| Metric | Value |
|--------|-------|
| **Accuracy (NCERT Test)** | 56% with keywords |
| **Avg Similarity Score** | 0.355 |
| **Categorization Rate** | 89% (11% uncategorized) |
| **Processing Speed** | ~0.27s per file |
| **Embedding Model** | BAAI/bge-base-en-v1.5 (768 dims) |

---

## Contributing

FileSense is an open-source project. Contributions are welcome!

- **GitHub:** [ahhyoushh/FileSense](https://github.com/ahhyoushh/FileSense)
- **Issues:** Report bugs or request features
- **Pull Requests:** Submit improvements

---

## License

MIT License © 2025 Ayush Bhalerao

---

**Ready to get started?** → [Installation Guide](/FileSense/wiki/getting-started/)
