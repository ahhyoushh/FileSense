# 📚 FileSense Wiki

Comprehensive documentation for the FileSense intelligent file organizer.

---

## 🎯 Quick Navigation

### 📖 For Users
- **[Home](index.md)** - Project overview and quick links
- **[Getting Started](getting_started.md)** - Installation and setup
- **[User Guide](user-guide.md)** - How to use FileSense (coming soon)
- **[FAQ](faq.md)** - Common questions and troubleshooting

### 🔧 For Developers
- **[Architecture](pipeline.md)** - System design and data flow
- **[API Reference](api-reference.md)** - Function documentation (coming soon)
- **[Code Structure](code-structure.md)** - Project organization (coming soon)

### 📊 Research & Analysis
- **[Performance Metrics](metrics.md)** - Benchmarks and accuracy
- **[NL vs Keywords Study](NL_VS_OG.md)** - Comprehensive comparison
- **[Lessons Learned](lessons-learned.md)** - Key insights from development

### 🛠️ Resources
- **[Template](template.md)** - Guide for creating new wiki pages
- **[Configuration](configuration.md)** - Settings and customization (coming soon)
- **[Roadmap](roadmap.md)** - Future plans (coming soon)

---

## 🌐 Viewing the Wiki

### Online (GitHub Pages)
Visit: [ahhyoushh.github.io/FileSense/wiki](https://ahhyoushh.github.io/FileSense/wiki/)

### Locally
1. Install Jekyll: `gem install jekyll bundler`
2. Navigate to wiki directory: `cd wiki`
3. Run: `bundle exec jekyll serve`
4. Open: `http://localhost:4000/FileSense/wiki/`

---

## 📝 Contributing to the Wiki

### Adding a New Page

1. **Create** a new `.md` file in `wiki/`
2. **Use the template** from `template.md`
3. **Add to navigation** in `_data/navigation.yml`
4. **Follow style guide** (see template.md)
5. **Submit PR** with your changes

### Updating Existing Pages

1. **Edit** the markdown file
2. **Test** locally if possible
3. **Submit PR** with clear description

---

## 🎨 Wiki Structure

```
wiki/
├── _config.yml              # Jekyll configuration
├── _data/
│   └── navigation.yml       # Sidebar navigation
├── index.md                 # Homepage
├── getting_started.md       # Installation guide
├── faq.md                   # FAQ
├── pipeline.md              # Architecture
├── metrics.md               # Performance benchmarks
├── NL_VS_OG.md             # Research study
├── lessons-learned.md       # Development insights
├── template.md              # Page template
└── README.md               # This file
```

---

## 🎯 Key Insights (from Development)

The wiki incorporates important lessons learned:

### ✅ What Works
1. **Keyword-based descriptions** outperform natural language (+32% accuracy)
2. **all-mpnet-base-v2** is the optimal embedding model
3. **FAISS vector search** is fast and efficient
4. **Academic documents** are the sweet spot for FileSense

### ❌ What Doesn't Work
1. **Natural language descriptions** performed worse (24% vs 56% accuracy)
2. **Lighter embedding models** significantly reduced performance
3. **AG News dataset** showed poor results
4. **One-size-fits-all** approach doesn't work

These insights are documented throughout the wiki, especially in:
- [Lessons Learned](lessons-learned.md)
- [Performance Metrics](metrics.md)
- [NL vs Keywords Study](NL_VS_OG.md)

---

## 🚀 Quick Start

**New to FileSense?** Start here:

1. Read the [Home](index.md) page for an overview
2. Follow the [Getting Started](getting_started.md) guide
3. Check the [FAQ](faq.md) for common questions
4. Explore [Architecture](pipeline.md) to understand how it works

**Want to contribute?** See the [Template](template.md) for guidelines.

---

## 📊 Wiki Statistics

- **Total Pages:** 10+ (and growing)
- **Last Updated:** 2025-12-05
- **Theme:** Minimal Mistakes (Dark Mode)
- **Format:** Markdown + Jekyll

---

## 🤝 Contributing

We welcome contributions to improve the documentation!

**Ways to contribute:**
- Fix typos or improve clarity
- Add missing documentation
- Create tutorials or guides
- Share your use cases
- Suggest improvements

**How to contribute:**
1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

---

## 📚 External Resources

- **GitHub Repository:** [ahhyoushh/FileSense](https://github.com/ahhyoushh/FileSense)
- **Demo Video:** [YouTube](https://youtu.be/f27I2L7uoC8)
- **Project Website:** [ahhyoushh.github.io/FileSense](https://ahhyoushh.github.io/FileSense)

---

## 📝 License

Documentation is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)  
Code is licensed under MIT License © 2025 Ayush Bhalerao

---

**Questions?** Open an issue on [GitHub](https://github.com/ahhyoushh/FileSense/issues)!
