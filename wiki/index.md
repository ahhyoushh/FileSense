---
title: "FileSense Documentation"
layout: splash
permalink: /wiki/
header:
  overlay_color: "#000"
  overlay_filter: "0.5"
  actions:
    - label: "🚀 Get Started"
      url: "/wiki/getting-started/"
    - label: "📺 Watch Demo"
      url: "https://youtu.be/f27I2L7uoC8"
excerpt: "Intelligent semantic file organizer powered by SBERT embeddings and Gemini AI"
---

**Semantic document classifier that understands meaning, not just filenames.**

FileSense uses **SentenceTransformers (SBERT)** and **FAISS vector search** to organize files by their actual content. When it encounters unknown file types, it leverages **Google Gemini** to generate new categories automatically.

---

## ⚡ Quick Links

<div class="feature__wrapper">
  <div class="feature__item">
    <div class="archive__item">
      <div class="archive__item-teaser">
        <i class="fas fa-rocket fa-3x"></i>
      </div>
      <div class="archive__item-body">
        <h2 class="archive__item-title">Getting Started</h2>
        <div class="archive__item-excerpt">
          <p>Install and run FileSense in 5 minutes</p>
        </div>
        <p><a href="/FileSense/wiki/getting-started/" class="btn btn--primary">Start Here →</a></p>
      </div>
    </div>
  </div>

  <div class="feature__item">
    <div class="archive__item">
      <div class="archive__item-teaser">
        <i class="fas fa-book fa-3x"></i>
      </div>
      <div class="archive__item-body">
        <h2 class="archive__item-title">User Guide</h2>
        <div class="archive__item-excerpt">
          <p>Learn how to use all features effectively</p>
        </div>
        <p><a href="/FileSense/wiki/user-guide/" class="btn btn--primary">Read Guide →</a></p>
      </div>
    </div>
  </div>

  <div class="feature__item">
    <div class="archive__item">
      <div class="archive__item-teaser">
        <i class="fas fa-chart-line fa-3x"></i>
      </div>
      <div class="archive__item-body">
        <h2 class="archive__item-title">Performance</h2>
        <div class="archive__item-excerpt">
          <p>See benchmarks and optimization studies</p>
        </div>
        <p><a href="/FileSense/wiki/metrics/" class="btn btn--primary">View Metrics →</a></p>
      </div>
    </div>
  </div>
</div>

---

## 🎯 Core Features

| Feature | Description |
|---------|-------------|
| 🧠 **Semantic Sorting** | Classifies by meaning (e.g., "Newton's Laws" → Physics) |
| 🤖 **AI-Powered Labeling** | Uses Gemini to generate new categories automatically |
| ⚡ **FAISS Vector Search** | Lightning-fast similarity matching with embeddings |
| 🔄 **Self-Updating** | Automatically rebuilds index when new labels are created |
| 👀 **OCR Support** | Extracts text from scanned PDFs and images |
| 🧩 **Keyword Boosting** | Hybrid approach: Vector similarity + keyword matching |
| 🖥️ **GUI & CLI** | Desktop app with system tray + command-line interface |
| 🧵 **Multithreading** | Process hundreds of files in parallel |

---

## 📊 How It Works

```mermaid
flowchart TD
    A[📄 Input File] --> B[📝 Extract Text]
    B --> C[🔢 Generate Embedding<br/>SBERT all-mpnet-base-v2]
    C --> D{🎯 Similarity ≥ 0.40?}
    D -->|Yes| E[✅ Classify to Existing Folder]
    D -->|No| F[🤖 Ask Gemini for Label]
    F --> G[💾 Update folder_labels.json]
    G --> H[🔄 Rebuild FAISS Index]
    H --> I[🔁 Re-classify File]
    I --> E
    E --> J[📁 Move to Sorted Folder]
```

---

## 🚀 Quick Start

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

## 📚 Documentation Sections

### 🎓 For Users
- **[Getting Started](/FileSense/wiki/getting-started/)** - Installation and setup
- **[User Guide](/FileSense/wiki/user-guide/)** - How to use FileSense effectively
- **[FAQ](/FileSense/wiki/faq/)** - Common questions and troubleshooting

### 🔧 For Developers
- **[Architecture](/FileSense/wiki/pipeline/)** - System design and data flow
- **[API Reference](/FileSense/wiki/api-reference/)** - Function documentation
- **[Code Structure](/FileSense/wiki/code-structure/)** - Project organization

### 📊 Research & Analysis
- **[Performance Metrics](/FileSense/wiki/metrics/)** - Benchmarks and accuracy
- **[NL vs Keywords Study](/FileSense/wiki/NL_VS_OG/)** - Comprehensive comparison
- **[Lessons Learned](/FileSense/wiki/lessons-learned/)** - Key insights from development

---

## 🎓 Key Insights

**Important discoveries from testing:**
{: .notice--warning}

1. **Keyword-based descriptions outperform natural language** for SBERT embeddings (+32% accuracy)
2. **Semantic descriptions performed worse** than expected (24% vs 56% accuracy)
3. **Lighter models significantly reduced performance** - stick with all-mpnet-base-v2
4. **AG News dataset showed poor results** - academic documents work best

See the [NL vs Keywords Study](/FileSense/wiki/NL_VS_OG/) for detailed analysis.

---

## 📈 Performance Highlights

| Metric | Value |
|--------|-------|
| **Accuracy (NCERT Test)** | 56% with keywords |
| **Avg Similarity Score** | 0.355 |
| **Categorization Rate** | 89% (11% uncategorized) |
| **Processing Speed** | ~0.27s per file |
| **Embedding Model** | all-mpnet-base-v2 (768 dims) |

---

## 🤝 Contributing

FileSense is an open-source project. Contributions are welcome!

- **GitHub:** [ahhyoushh/FileSense](https://github.com/ahhyoushh/FileSense)
- **Issues:** Report bugs or request features
- **Pull Requests:** Submit improvements

---

## 📝 License

MIT License © 2025 Ayush Bhalerao

---

**Ready to get started?** → [Installation Guide](/FileSense/wiki/getting-started/)
{: .notice--success}
