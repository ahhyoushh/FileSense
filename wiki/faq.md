---
title: "Frequently Asked Questions"
permalink: /wiki/faq/
toc: true
toc_sticky: true
---

# ❓ Frequently Asked Questions

Common questions and answers about FileSense.

---

## 🎯 General Questions

### What is FileSense?

FileSense is an intelligent file organizer that classifies documents by their **semantic meaning** rather than just filenames or extensions. It uses:
- **SBERT** (Sentence-BERT) for text embeddings
- **FAISS** for fast vector similarity search
- **Google Gemini** for generating new categories automatically

### How is this different from traditional file organizers?

| Traditional Organizers | FileSense |
|----------------------|-----------|
| Rules-based (file extension, name patterns) | Semantic understanding (actual content) |
| Manual category creation | AI-powered auto-generation |
| Keyword matching only | Vector embeddings + keywords |
| Static classification | Self-learning system |

### Is my data sent to the cloud?

**Partially.** Here's what happens:
- ✅ **Local:** Text extraction, embedding generation, vector search
- ☁️ **Cloud:** Only when generating new labels (Gemini API)
- 🔒 **Privacy:** File content is sent to Gemini only for classification, not stored

**You can disable cloud features** with `--no-generation` flag.
{: .notice--info}

---

## 🔧 Technical Questions

### What file types are supported?

| Format | Support | Notes |
|--------|---------|-------|
| **PDF** | ✅ Full | Text-based and scanned (OCR) |
| **DOCX** | ✅ Full | Microsoft Word documents |
| **TXT** | ✅ Full | Plain text files |
| **MD** | ✅ Full | Markdown files |
| **Images** | ⚠️ Partial | OCR only (requires Tesseract) |
| **Others** | ❌ No | Filename-based classification only |

### How accurate is the classification?

**Current performance (NCERT test dataset):**
- **Accuracy:** 56% with keyword-based descriptions
- **Categorization rate:** 89% (only 11% uncategorized)
- **Average similarity:** 0.355

**Factors affecting accuracy:**
- Quality of text extraction
- Similarity to existing labels
- Document length and clarity
- Threshold settings (default: 0.40)

### What embedding model is used?

**Model:** `all-mpnet-base-v2` (SentenceTransformers)
- **Dimensions:** 768
- **Performance:** Best balance of speed and accuracy
- **Size:** ~420MB download on first run

**Why not use a lighter model?**
{: .notice--warning}

Testing showed that lighter models performed **significantly worse**. The all-mpnet-base-v2 model is optimal for this use case.

### Can I use a different embedding model?

Yes! Edit `scripts/create_index.py`:

```python
MODEL_NAME = "all-mpnet-base-v2"  # Change this
```

**Recommended alternatives:**
- `all-MiniLM-L6-v2` - Faster, less accurate
- `all-mpnet-base-v2` - **Best balance** (recommended)
- `multi-qa-mpnet-base-dot-v1` - Better for Q&A documents

---

## 🚀 Usage Questions

### How do I organize my Downloads folder?

**Option 1: One-time bulk sort**
```bash
python scripts/script.py --dir ~/Downloads --threads 8
```

**Option 2: Real-time monitoring**
```bash
python scripts/watcher_script.py --dir ~/Downloads
```

The watcher will automatically sort new files as they appear!

### Can I customize the categories?

**Yes!** Edit `folder_labels.json`:

```json
{
  "Custom Category": "keyword1, keyword2, keyword3, related terms, synonyms Keywords: key1, key2, key3"
}
```

Then rebuild the index:
```bash
python scripts/create_index.py
```

### How do I adjust classification thresholds?

Edit `scripts/classify_process_file.py`:

```python
THRESHOLD = 0.4              # Main threshold (increase for stricter)
low_confidence_threshold = 0.35  # Fallback threshold
```

**Guidelines:**
- **0.30-0.35:** More files categorized, less accurate
- **0.40-0.45:** Balanced (recommended)
- **0.50+:** Very strict, more uncategorized files

### What happens to uncategorized files?

Files that don't match any category (similarity < threshold) are moved to `sorted/Uncategorized/`.

**To reduce uncategorized files:**
1. Lower the threshold (e.g., 0.35)
2. Enable generation: Remove `--no-generation` flag
3. Add more diverse labels to `folder_labels.json`

---

## 🐛 Troubleshooting

### Files are not being classified correctly

**Possible causes:**

1. **Poor text extraction**
   - Check if PDF is scanned (needs OCR)
   - Verify Tesseract is installed for images
   - Try fallback extraction: `extract_text(file, fallback=True)`

2. **No matching labels**
   - Add relevant categories to `folder_labels.json`
   - Enable generation to create new labels
   - Check similarity scores in logs

3. **Threshold too high**
   - Lower `THRESHOLD` in `classify_process_file.py`
   - Check average similarities in your dataset

### Gemini API errors

**"API key not valid"**
- Verify `.env` file exists and contains valid key
- Check for extra spaces or quotes in `.env`
- Regenerate key at [Google AI Studio](https://makersuite.google.com/)

**"Rate limit exceeded"**
- Gemini has usage limits on free tier
- Add delays between requests
- Consider upgrading to paid tier

**"Model not found"**
- Ensure you're using `gemini-2.5-flash` (current model)
- Check Google AI Studio for model availability

### FAISS index errors

**"Index file not found"**
```bash
python scripts/create_index.py
```

**"Dimension mismatch"**
- Delete `folder_embeddings.faiss`
- Rebuild index with correct model

**"Empty index"**
- Ensure `folder_labels.json` has at least one label
- Check JSON file is valid (no syntax errors)

### Performance issues

**Slow processing**
- Increase threads: `--threads 12`
- Use SSD for faster file I/O
- Disable logging: `--no-logs`

**High memory usage**
- Reduce concurrent threads
- Process files in smaller batches
- Use `--single-thread` for large files

**Embedding model download stuck**
- Check internet connection
- Manually download from [HuggingFace](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)
- Place in `~/.cache/torch/sentence_transformers/`

---

## 📊 Performance Questions

### Why do keyword descriptions work better than natural language?

**Comprehensive testing showed:**
- **Keywords:** 56% accuracy
- **Natural Language:** 24% accuracy

**Reasons:**
1. SBERT embeddings cluster keyword lists more effectively
2. Natural language adds grammatical noise
3. Keywords provide broader semantic coverage
4. Academic documents align well with keyword matching

See the [NL vs Keywords Study](/FileSense/wiki/NL_VS_OG/) for detailed analysis.

### What's the processing speed?

**Benchmarks (NCERT dataset, 75 files):**
- **Average:** 0.27s per file
- **Total:** ~20s for 75 files (6 threads)
- **Bottleneck:** Text extraction (especially OCR)

**Optimization tips:**
- Use more threads for I/O-bound tasks
- Pre-extract text for repeated processing
- Use SSD storage
- Disable fallback extraction if not needed

### How much disk space does it need?

**Minimal:**
- **Embedding model:** ~420MB (one-time download)
- **FAISS index:** <1MB per 100 labels
- **Dependencies:** ~500MB total
- **Logs:** Varies (can be disabled)

---

## 🔒 Privacy & Security

### Is my data safe?

**Local processing:**
- Text extraction happens locally
- Embeddings generated locally
- Vector search is local

**Cloud processing:**
- Only when generating new labels
- File content sent to Gemini API
- Not stored by Google (per their policy)

**Recommendations:**
- Use `--no-generation` for sensitive files
- Review `folder_labels.json` before sharing
- Keep `.env` file private

### Can I use FileSense offline?

**Partially:**
- ✅ Classification works offline (after initial setup)
- ❌ New label generation requires internet (Gemini API)

**Offline workflow:**
1. Pre-generate all labels online
2. Use `--no-generation` flag
3. All classification happens locally

---

## 🚧 Known Limitations

### Current Limitations

1. **Natural language descriptions perform worse** than keywords
   - Tested extensively, keywords are superior
   - See [NL vs OG study](/FileSense/wiki/NL_VS_OG/)

2. **Lighter models reduce accuracy significantly**
   - Stick with all-mpnet-base-v2
   - Don't use smaller models for production

3. **AG News dataset showed poor results**
   - FileSense works best with academic/professional documents
   - News articles may need different approach

4. **Text classification is inherently challenging**
   - This might be an inefficient approach for some use cases
   - Consider as a learning experience

**These insights are from real testing and development.**
{: .notice--warning}

---

## 🤝 Contributing

### How can I contribute?

1. **Report bugs:** [GitHub Issues](https://github.com/ahhyoushh/FileSense/issues)
2. **Suggest features:** Open a discussion
3. **Submit PRs:** Fork, improve, and submit
4. **Improve docs:** Help expand this wiki

### Where can I get help?

- **GitHub Issues:** Technical problems
- **Discussions:** General questions
- **Email:** Contact the maintainer

---

## 📚 Additional Resources

- **[Getting Started](/FileSense/wiki/getting-started/)** - Installation guide
- **[User Guide](/FileSense/wiki/user-guide/)** - Detailed usage
- **[Architecture](/FileSense/wiki/pipeline/)** - How it works
- **[Performance Metrics](/FileSense/wiki/metrics/)** - Benchmarks

---

**Still have questions?** Open an issue on [GitHub](https://github.com/ahhyoushh/FileSense/issues)!
{: .notice--info}

---

[← Back to Home](/FileSense/wiki/)
