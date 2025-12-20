---
title: "Lessons Learned"
permalink: /wiki/lessons-learned/

---

# Lessons Learned

Key insights and discoveries from developing FileSense.

---

## Major Discoveries

### 1. Keyword Descriptions >> Natural Language

**Hypothesis:** Natural language descriptions mimicking document content would match better with SBERT embeddings.

**Result:** **Completely Wrong**

| Approach | Accuracy | Avg Similarity | Uncategorized |
|----------|----------|----------------|---------------|
| **Natural Language** | 24% | 0.104 | 71% |
| **Keywords** | 56% | 0.355 | 11% |
| **Difference** | **+32%** | **+241%** | **-60%** |

**Why Keywords Won:**

1. **Maximum Semantic Density**
   ```
   Keywords: "mechanics, thermodynamics, optics, quantum, forces, energy"
   → 100% meaningful tokens
   
   Natural Language: "Documents contain experimental procedures investigating..."
   → ~15% meaningful tokens (rest is grammatical noise)
   ```

2. **SBERT Embedding Alignment**
   - SBERT clusters keyword lists more effectively
   - Grammatical structure adds variance without value
   - Academic terminology works better as isolated terms

3. **Broader Coverage**
   - Keywords cover more concepts per character
   - Natural language is overly specific
   - Synonyms naturally included in keyword lists

> **Lesson:** For SBERT-based classification, **simpler is better**. Don't overthink it.

**Full analysis:** [NL vs Keywords Study](/FileSense/wiki/NL_VS_OG/)

---

### 2. Lighter Models = Worse Performance

**Hypothesis:** Smaller embedding models would provide acceptable accuracy with better speed.

**Result:** **Significantly Worse**

**Tested Models:**
- `all-MiniLM-L6-v2` (384 dims, 80MB) - Poor accuracy
- `BAAI/bge-base-en-v1.5` (768 dims, 440MB) - Best performance
- `multi-qa-mpnet-base-dot-v1` (768 dims) - Moderate

> **Lesson:** The performance drop from lighter models is **not worth** the size/speed gains. Now using `BAAI/bge-base-en-v1.5`.

---

### 3. AG News Dataset Performed Poorly

**Hypothesis:** FileSense would work well across different document types.

**Result:** **Domain-Specific Performance**

**Findings:**
- **Academic documents:** Good (56% accuracy)
- **News articles:** Poor (see evaluation logs)
- **Professional documents:** Acceptable

**Why News Failed:**
- Different linguistic structure
- Time-sensitive content
- Informal language patterns
- Topic diversity vs academic consistency

> **Lesson:** FileSense is optimized for **structured, academic/professional documents**. Not a one-size-fits-all solution.

---

### 4. Text Classification is Hard

**Reality Check:**

> "Might be the most inefficient way to text classification, learning experience"
> — Development notes

**What This Means:**
- Text classification is inherently challenging
- Vector embeddings + LLM is one approach, not the only one
- Trade-offs exist between accuracy, speed, and complexity
- FileSense works well for specific use cases, not all scenarios

> **Lesson:** Be realistic about limitations. This is a **learning project** that works well for certain document types.

---

## Technical Insights

### SBERT Behavior

**Discovery:** SBERT embeddings have specific characteristics that affect classification.

**Key Findings:**

1. **Keyword Clustering**
   - Keyword lists create denser semantic clusters
   - Natural sentences introduce variance
   - Isolated terms align better in embedding space

2. **Synonym Proximity**
   - Related terms cluster naturally
   - "electricity, electrical, electromagnetism" are close in embedding space
   - Keyword lists leverage this automatically

3. **Grammatical Noise**
   - Articles ("the", "a", "an") dilute semantic signal
   - Verbs ("contains", "includes") add no classification value
   - Prepositions create unnecessary variance

**Lesson:** Understand your embedding model's behavior. Don't assume natural language is always better.

---

### FAISS Performance

**Discovery:** FAISS is incredibly efficient for this use case.

**Benchmarks:**
- **Search time:** ~0.02s for 10 labels
- **Index size:** ~3KB per label
- **Scaling:** Linear with number of labels
- **Memory:** Minimal overhead

> **Lesson:** FAISS is perfect for local, offline vector search. No need for complex vector databases.

---

### Gemini Integration

**Discovery:** Structured output with JSON schema is powerful but has quirks.

**Best Practices:**

1. **Clear Schemas**
   ```python
   schema = {
       "type": "object",
       "properties": {
           "folder_label": {"type": "string", "description": "..."},
           "description": {"type": "string", "description": "..."}
       },
       "required": ["folder_label", "description"]
   }
   ```

2. **Focused Examples**
   - 15 examples covering edge cases
   - Concise format (not verbose)
   - Diverse subject coverage

3. **Temperature Tuning**
   - 0.5 for generation (balanced creativity)
   - 0.2 for merging (more deterministic)

**Lesson:** Structured LLM output requires careful prompt engineering and schema design.

---

## Development Challenges

### Challenge 1: Merging Metadata

**Problem:** When a new file matches an existing label, how to update the description without losing information?

**Solution:** Hard-merge logic that preserves ALL unique terms.

```python
# Old → LLM → New
# Ensures no terms are dropped
for term_list in (old_terms, llm_terms, new_terms):
    for term in term_list:
        if term.lower() not in seen:
            final_terms.append(term)
```

**Lesson:** When dealing with user-generated data, **never lose information**. Always append, never replace.

---

### Challenge 2: Threshold Tuning

**Problem:** What similarity threshold balances precision and recall?

**Tested Thresholds:**
- **0.30:** Too many false positives
- **0.35:** Acceptable fallback
- **0.40:** Sweet spot (current default)
- **0.50:** Too strict, many uncategorized

**Solution:** Dual-threshold system
- Main: 0.40 (high confidence)
- Fallback: 0.35 (acceptable with warning)

**Lesson:** One threshold doesn't fit all. Use tiered thresholds for better UX.

---

### Challenge 3: Text Extraction Quality

**Problem:** PDFs often have table of contents, headers, footers that skew classification.

**Solution:** Multi-layered extraction
1. Start from page 3 (skip TOC)
2. Crop headers/footers (70px margins)
3. Quality scoring (filter low-quality pages)
4. Fallback: Extract from middle pages

**Lesson:** Text extraction quality directly impacts classification accuracy. Invest time in preprocessing.

---

## Unexpected Findings

### 1. Filename Boosting is Effective

**Discovery:** Adding +0.2 similarity when label appears in filename significantly improves accuracy.

**Example:**
- File: `physics_chapter_1.pdf`
- Label: "Physics"
- Boost: +0.2 to similarity score

**Impact:** ~10% improvement in correct classifications

**Lesson:** Don't ignore simple heuristics. They can complement ML approaches effectively.

---

### 2. Multithreading Scales Well

**Discovery:** Near-linear speedup up to 8 threads for I/O-bound workload.

| Threads | Speedup |
|---------|---------|
| 1 | 1.0x |
| 2 | 1.8x |
| 4 | 3.3x |
| 6 | 4.0x |
| 8 | 4.4x |

**Lesson:** For I/O-bound tasks, multithreading provides excellent performance gains.

---

### 3. Fallback Extraction Helps

**Discovery:** Extracting from middle pages (avoiding TOC) improves classification for ~15% of files.

**When It Helps:**
- Academic papers with long introductions
- Books with extensive front matter
- Documents with cover pages

**Lesson:** Don't give up after first extraction attempt. Fallback strategies can recover many edge cases.

---

## What Would I Do Differently?

### 1. Start with Keywords

**Mistake:** Spent time implementing natural language descriptions first.

**Better Approach:** Test both approaches early with small dataset.

**Time Saved:** ~2 days of implementation + testing

---

### 2. Benchmark Models Earlier

**Mistake:** Assumed lighter models would work acceptably.

**Better Approach:** Test all candidate models on representative dataset before committing.

**Time Saved:** ~1 day of optimization attempts

---

### 3. Focus on Academic Documents

**Mistake:** Tried to make it work for all document types (news, emails, etc.)

**Better Approach:** Specialize for academic/professional documents from the start.

**Time Saved:** ~3 days of testing and tuning

---

### 4. Simpler Prompts from Start

**Mistake:** Verbose, complex prompts with many rules.

**Better Approach:** Start simple, add complexity only when needed.

**Lesson:** Prompt engineering benefits from iteration, not upfront complexity.

---

## Future Improvements

### Based on Lessons Learned

1. **Domain-Specific Models**
   - Fine-tune SBERT on academic documents
   - Create specialized embeddings
   - Improve accuracy by 10-15%

2. **Active Learning**
   - User feedback loop
   - Correct misclassifications
   - Iteratively improve labels

3. **Hybrid Approaches**
   - Combine SBERT with traditional ML
   - Use rule-based fallbacks
   - Ensemble methods

4. **Better Text Extraction**
   - ML-based page quality scoring
   - Smarter fallback strategies
   - Enhanced OCR preprocessing

---

## Key Takeaways

### Do This

1. **Use keyword-based descriptions** for SBERT
2. **Stick with proven models** (BAAI/bge-base-en-v1.5)
3. **Test early and often** with real data
4. **Focus on specific use cases** (academic docs)
5. **Implement fallback strategies** (extraction, thresholds)
6. **Never lose user data** (append, don't replace)

### Don't Do This

1. **Assume natural language is better** - Test first!
2. **Use lighter models** - Performance drop is real
3. **Try to solve all problems** - Specialize
4. **Overcomplicate prompts** - Start simple
5. **Ignore simple heuristics** - Filename boosting works
6. **Skip preprocessing** - Text quality matters

---

## Meta-Lessons

### On Machine Learning

**Lesson:** ML is not magic. It's a tool with specific strengths and weaknesses.

- **Strengths:** Pattern recognition, semantic understanding
- **Weaknesses:** Requires quality data, domain-specific tuning
- **Reality:** 56% accuracy is good for this problem, not 95%

### On Development

**Lesson:** Iterate quickly, test assumptions, learn from failures.

- Natural language approach failed → Learned about SBERT behavior
- Lighter models failed → Understood model trade-offs
- News dataset failed → Recognized domain specificity

**Every failure taught something valuable.**

### On Documentation

**Lesson:** Document what doesn't work, not just what does.

This wiki includes:
- Failed approaches (NL descriptions)
- Limitations (news articles)
- Lessons learned (model selection)

**Honest documentation helps future developers avoid the same mistakes.**

---

## Recommended Reading

### For Understanding SBERT
- [Sentence-BERT Paper](https://arxiv.org/abs/1908.10084)
- [HuggingFace Documentation](https://huggingface.co/sentence-transformers)

### For Vector Search
- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [Vector Search Best Practices](https://www.pinecone.io/learn/vector-search/)

### For Prompt Engineering
- [Google AI Studio](https://makersuite.google.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

## Contributing Your Lessons

Have you learned something new while using FileSense?

**Share your insights:**
1. Open an issue on [GitHub](https://github.com/ahhyoushh/FileSense/issues)
2. Submit a PR to this wiki page
3. Start a discussion

**Your experience helps everyone!**

---

[← Back to Home](/FileSense/wiki/)
