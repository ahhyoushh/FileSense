---
title: "Documentation Home"
permalink: /wiki/
---

# FileSense Documentation

Welcome to the internal research and development wiki for FileSense.

---

## Quick Navigation

### For Users
- **[Getting Started](/FileSense/wiki/getting-started/)** - Installation and first run
- **[FAQ](/FileSense/wiki/faq/)** - Common questions and troubleshooting

### For Developers
- **[Architecture](/FileSense/wiki/pipeline/)** - How the classification pipeline works
- **[RL Integration](/FileSense/wiki/reinforcement-learning/)** - Reinforcement Learning details
- **[Wiki Template](/FileSense/wiki/template/)** - Guidelines for contributing to this wiki

### Research & Metrics
- **[Evaluation Metrics](/FileSense/wiki/metrics/)** - Performance benchmarks and datasets
- **[NL vs Keywords Study](/FileSense/wiki/NL_VS_OG/)** - Comprehensive analysis of description strategies
- **[Lessons Learned](/FileSense/wiki/lessons-learned/)** - Key insights from development

---

## Project Overview

FileSense is a semantic file organizer designed for academic and professional documents. It uses SBERT embeddings and FAISS vector search to classify files into meaningful categories.

### Key Features
- **Semantic Classification:** Matches file content to topic labels using vector similarity.
- **Auto-Labeling:** Uses Google Gemini to generate new categories for unknown files.
- **RL-Driven Policy:** Adaptive agent that balances accuracy and API costs.
- **Multithreaded:** Scales across CPU cores for high-speed processing.
- **Privacy-Focused:** Local processing for embeddings and search.

---

## How to View the Wiki

### Online (GitHub Pages)
The wiki is automatically deployed to:
**[ahhyoushh.github.io/FileSense](https://ahhyoushh.github.io/FileSense)**

### Locally (Jekyll)
If you have Ruby and Jekyll installed:

```bash
cd wiki
bundle install
bundle exec jekyll serve
```

---

## Contributing to the Wiki

I encourage documenting everything—from minor bug fixes to major architectural changes.

### Guidelines
1. **Be Honest:** Document what doesn't work (see Lessons Learned).
2. **Use Data:** Support claims with metrics and logs.
3. **Stay Minimal:** Use the [Contrast Theme](https://github.com/niklasbuschmann/contrast) aesthetics.
4. **Follow the Template:** See the [Wiki Template](/FileSense/wiki/template/) for styling rules.

---

## Wiki Structure

```
wiki/
├── index.md             # Landing page
├── metrics.md           # Benchmark data
├── NL_VS_OG.md          # Research study
├── pipeline.md          # Architecture docs
├── getting_started.md   # Installation guide
├── faq.md               # Troubleshooting
├── lessons-learned.md   # Key insights
└── template.md          # Writing guide
```

---

## Key Development Insights

I've learned several critical lessons during development:

1. **Keywords > Natural Language:** Comma-separated keyword lists outperform full sentence descriptions by **32% accuracy**.
2. **Model Selection:** `BAAI/bge-base-en-v1.5` provides the best balance of speed and accuracy.
3. **Domain Focus:** FileSense is optimized for academic documents; performance on news articles (AG News) is significantly lower.
4. **API Management:** RL agents are effective at managing Gemini rate limits by prioritizing vector search.

---

## Quick Start (CLI)

```bash
# Install
pip install -r requirements.txt

# Process
python scripts/script.py --dir ./files
```

---

[← Back to Home](/FileSense/wiki/)
