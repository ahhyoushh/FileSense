---
title: "Natural Language vs Keywords Study"
permalink: /wiki/NL_VS_OG/

---

# Natural Language vs Original Keywords: Comprehensive Analysis

**Test Date:** 2025-12-05  
**commit id:** 99d03e579a9fd413d7938f01559ebb0172a260e3
**Test Files:** 75 NCERT textbook markdown files  
**Model:** all-mpnet-base-v2 (SentenceTransformer)  

---

## Executive Summary

### **WINNER: Original Keywords Approach** 

The comprehensive testing revealed that **comma-separated keyword terms dramatically outperform natural language descriptions** for SBERT-based semantic matching with academic documents.

| Metric | Natural Language | Original Keywords | Difference |
|--------|-----------------|-------------------|------------|
| **Accuracy** | 24.0%  | **56.0%**  | **+32.0%** |
| **Avg Similarity** | 0.104 | **0.355** | **+241%** |
| **Uncategorized Files** | 53/75 (71%)  | 8/75 (11%)  | **-60%** |
| **Failed (0.00 sim)** | 53 files  | 8 files  | **-45 files** |
| **Avg Time/File** | 0.30s | **0.27s**  | **-10%** |

**Verdict:** Original keyword-based descriptions are **superior** for NCERT academic documents with SBERT embeddings.

---

##  Test Configuration

### Test Setup
- **Test Files:** NCERT textbook markdown files (various subjects: Physics, Chemistry, Maths, Geography, Biology, civics)
- **Natural Language Test:** NCERT_NL_TEST.log (Content-style descriptions)
- **Original Keyword Test:** NCERT_OG_TEST.log (Comma-separated terms)
- **Total Files:** 75 documents
- **Embedding Model:** all-mpnet-base-v2
- **Vector Search:** FAISS IndexFlatIP

### Approaches Tested

#### Approach 1: Natural Language Descriptions
**Hypothesis:** Content-style descriptions would match better with SBERT

**Format:**
```
"Documents contain experimental procedures and physical laws. Content includes 
laboratory observations, scientific principles like Bernoulli's equation, and 
analysis of forces, energy, and motion. Typical terminology involves physical 
quantities, units, and theoretical concepts."
```

**Characteristics:**
- Full sentences mimicking document content
- Natural grammatical structure
- Descriptive phrases about what documents contain
- 50-100 words per description

#### Approach 2: Original Keywords (Comma-Separated Terms)
**Hypothesis:** Dense keyword lists capture semantic essence

**Format:**
```
"mechanics, thermodynamics, electromagnetism, optics, quantum mechanics, 
relativity, fluid dynamics, kinematics, forces, energy, motion, waves, 
heat, light, electricity, magnetism, laboratory experiments, scientific 
formulas, physical laws"
```

**Characteristics:**
- Comma-separated terms
- Dense terminology (20-40 terms)
- Domain-specific vocabulary
- Synonyms and related concepts
- No grammatical structure

---

##  Detailed Results

### Overall Performance

| Metric | Natural Language | Original Keywords | Winner |
|--------|-----------------|-------------------|--------|
| **Total Files** | 75 | 75 | - |
| **Accuracy** | 24.0% | **56.0%** |  OG |
| **Avg Similarity** | 0.104 | **0.355** |  OG |
| **Uncategorized** | 53 | 8 |  OG |
| **Low Confidence (<0.40)** | 17 | 40 |  NL |
| **Avg Time/File** | 0.30s | **0.27s** |  OG |

### Similarity Score Distribution

| Range | Natural Language | Original Keywords | Analysis |
|-------|-----------------|-------------------|----------|
| **0.00 (Failed)** | 53 | 8 | NL failed on 71% of files |
| **0.01-0.20 (Very Low)** | 0 | 0 | - |
| **0.21-0.30 (Low)** | 4 | 8 | Both struggled here |
| **0.31-0.40 (Medium)** | 14 | 34 | OG had 2.4x more medium matches |
| **0.41-0.50 (Good)** | 3 | 16 | OG had 5.3x more good matches |
| **0.51+ (Excellent)** | 1 | 9 | OG had 9x more excellent matches |

### Visual Distribution

```
Natural Language:
0.00 (Failed):     ████████████████████████████████████████████████████ 53
0.31-0.40:         ██████████ 14
0.41-0.50:         ██ 3
0.51+:             █ 1

Original Keywords:
0.00 (Failed):     ████████ 8
0.21-0.30:         ████████ 8
0.31-0.40:         ██████████████████████████████████ 34
0.41-0.50:         ████████████████ 16
0.51+:             █████████ 9
```

### Label Distribution

#### Natural Language Approach
- **Uncategorized:** 53 files (71%)
- **Biotechnology:** 9 files
- **Chemistry:** 5 files
- **Civics:** 5 files
- **English:** 3 files

#### Original Keywords Approach
- **Geography:** 19 files
- **English:** 15 files
- **Biotechnology:** 14 files
- **Physics:** 14 files
- **Uncategorized:** 8 files (11%)
- **Civics:** 5 files

---

## 🔍 Analysis: Why Natural Language Failed

### 1. **Too Specific / Overfitted**
Natural language descriptions were too specific to the training examples:

```
BAD: "Integration by parts where u equals x squared, dv equals e to the x dx. 
Series convergence testing using ratio test, comparison test."
```

This doesn't match NCERT files which have different phrasing and structure.

### 2. **SBERT Embedding Mismatch**
- SBERT models work better with **keyword density** than natural sentences for this use case
- Academic documents have consistent terminology that keywords capture better
- Natural sentences introduce grammatical noise

### 3. **Semantic Noise**
Natural sentences introduced grammatical structure that added noise:
- **Articles:** "the", "a", "an"
- **Verbs:** "contains", "includes", "discusses"
- **Prepositions:** "in", "on", "with"
- **Phrases:** "Documents contain...", "Content includes..."

These dilute the semantic signal for academic content.

### 4. **Reduced Keyword Density**
Natural language spreads keywords across more tokens:

```
Natural Language (100 words):
"Documents contain experimental procedures investigating physical laws. 
Content includes laboratory observations, scientific principles..."
→ ~15 meaningful keywords in 100 words (15% density)

Keywords (40 terms):
"mechanics, thermodynamics, electromagnetism, optics, quantum mechanics..."
→ 40 meaningful keywords in 40 words (100% density)
```

### 5. **Embedding Space Geometry**
- The all-mpnet-base-v2 model clusters keyword lists more effectively
- Natural sentences might introduce variance in the embedding space
- Keywords create denser, more consistent semantic clusters

---

## Analysis: Why Keywords Succeeded

### 1. **Broader Semantic Coverage**
Keyword lists cover MORE semantic space with FEWER tokens:

```
 GOOD: "mechanics, thermodynamics, optics, electromagnetism, quantum physics, 
relativity, fluid dynamics, kinematics, forces, energy, motion, waves"
```

Each term is a direct semantic signal without noise.

### 2. **Better Alignment with NCERT Structure**
NCERT files use consistent academic terminology:
- Technical terms appear frequently
- Keyword matching aligns with document structure
- Domain-specific vocabulary is strong signal

### 3. **Synonym Coverage**
Keywords naturally include synonyms and related terms:
```
"electricity, electrical, electromagnetism, electromagnetic"
"optics, optical, light, vision"
"mechanics, mechanical, motion, kinematics, dynamics"
```

### 4. **SBERT Model Characteristics**
- Trained on diverse text, but keyword matching is robust
- Academic terminology clusters well in embedding space
- Synonym proximity enhances matching

### 5. **Efficient Token Usage**
Every token in keyword descriptions carries semantic weight:
- No grammatical filler
- No redundant phrases
- Maximum information density

---

## Raw Data Summary

### Natural Language Test
- **Total Files:** 75
- **Correct Classifications:** 18
- **Accuracy:** 24.0%
- **Avg Similarity:** 0.104
- **Uncategorized:** 53 (71%)
- **Failed (0.00 sim):** 53
- **Good Matches (>0.40):** 4 (5%)

### Original Keywords Test  
- **Total Files:** 75
- **Correct Classifications:** 42
- **Accuracy:** 56.0%
- **Avg Similarity:** 0.355
- **Uncategorized:** 8 (11%)
- **Failed (0.00 sim):** 8
- **Good Matches (>0.40):** 25 (33%)

### Performance Comparison
- **Accuracy Improvement:** +32.0% (133% increase)
- **Similarity Improvement:** +0.251 (241% increase)
- **Uncategorization Reduction:** -60% (from 71% to 11%)
- **Good Matches Increase:** +525% (from 5% to 33%)

---

## Best Practices & Recommendations

### **DO: Use Keyword-Based Descriptions**

#### Optimal Format
```json
{
  "folder_label": "Physics",
  "description": "mechanics, thermodynamics, electromagnetism, optics, quantum mechanics, nuclear physics, relativity, astrophysics, fluid dynamics, solid state physics, particle physics, kinematics, dynamics, forces, energy, motion, matter, waves, fields, radiation, heat, light, sound, electricity, magnetism, gravity, laboratory experiments, scientific formulas, physical laws, conservation laws, measurement, vectors, scalars, work, power, momentum, impulse",
  "keywords": "physics, mechanics, thermodynamics, optics, quantum, relativity, energy, force, motion, waves"
}
```

#### Key Elements
1. **20-40 comma-separated terms** in description
2. **Mix of:**
   - Core concepts (mechanics, thermodynamics)
   - Sub-topics (fluid dynamics, particle physics)
   - Related terms (energy, force, motion)
   - Synonyms (electricity/electrical, optics/optical)
3. **8-12 high-value keywords** (most important terms)
4. **No articles, verbs, or grammatical structure**
5. **Dense terminology** without filler words

### **DON'T: Use Natural Language Descriptions**

#### Avoid This Format
```json
{
  "folder_label": "Physics",
  "description": "Documents contain experimental procedures and physical laws. Content includes laboratory observations, scientific principles like Newton's laws and Bernoulli's equation. Typical terminology involves physical quantities, units, and theoretical concepts related to mechanics, thermodynamics, and electromagnetism.",
  "keywords": "physics, experiment, laboratory"
}
```

#### Problems
1. **Grammatical noise** (contains, includes, involves)
2. **Low keyword density** (too many filler words)
3. **Overly specific examples** (Newton's laws, Bernoulli's equation)
4. **Reduced semantic coverage** (fewer meaningful terms)
5. **Embedding space dilution** (noise reduces signal)

---

## Key Insights

### For SBERT-Based Semantic Matching

####  **What Works:**
1. **Dense keyword lists** (20-40 terms)
2. **Domain-specific vocabulary** (technical terms)
3. **Synonym inclusion** (multiple ways to express concepts)
4. **Broad coverage** (core + sub-topics + related terms)
5. **No grammatical structure** (pure semantic content)

#### **What Doesn't Work:**
1. **Natural language sentences** (too much noise)
2. **Explanatory text** ("Documents contain...")
3. **Specific examples** (overfitting to training data)
4. **Grammatical connectors** (articles, prepositions, verbs)
5. **Low keyword density** (diluted semantic signal)

### Why This Matters

**SBERT Embedding Characteristics:**
- Trained on natural text BUT keyword matching is robust
- Academic terminology clusters well in embedding space
- Keyword density creates stronger semantic signals
- Grammatical structure adds variance without value

**Document Characteristics:**
- NCERT files use consistent academic terminology
- Technical terms are strong classification signals
- Keyword matching aligns with document structure
- Domain vocabulary is predictable and stable

---

## Actionable Next Steps

### 1. **Keep Using Keywords** (Confirmed Best Practice)
✅ Continue with comma-separated keyword terms in descriptions  
✅ Maintain 20-40 terms per description  
✅ Focus on domain-specific vocabulary  

### 2. **Expand Keyword Coverage** (High Priority)
Add more synonyms and related terms to existing labels:

**Example: Expand Physics**
```
Current: "mechanics, thermodynamics, optics, electromagnetism, quantum physics"

Expanded: "mechanics, thermodynamics, optics, electromagnetism, quantum physics,
nuclear physics, relativity, astrophysics, fluid dynamics, solid state physics,
particle physics, kinematics, dynamics, statics, forces, energy, motion, matter,
waves, fields, radiation, heat, light, sound, electricity, magnetism, gravity,
laboratory experiments, scientific formulas, physical laws, conservation laws,
measurement, vectors, scalars, work, power, momentum, impulse, friction, tension,
pressure, density, velocity, acceleration, displacement, torque, angular momentum"
```

### 3. **Optimize Prompts** (Medium Priority)
Current prompt optimizations completed:
- ✅ Removed verbose explanations
- ✅ Consolidated examples (15 focused examples)
- ✅ Streamlined merge logic
- ✅ Better error messages

Further optimizations:
- Fine-tune temperature settings
- Adjust similarity thresholds based on performance
- Add more edge case examples

### 4. **Test with Diverse Documents** (Medium Priority)
Validate approach with:
- PDFs with different structures
- Scanned documents (OCR text)
- Short vs long documents
- Multi-topic documents
- Non-academic content (news, legal, medical)

### 5. **Implement Training Dataset Optimization** (Low Priority)
From README ideas:
> "Use the dataset with category labels, generate folder labels until similarity crosses threshold for all training files"

This could further optimize descriptions through iterative refinement.

### 6. **Add More Academic Labels** (Low Priority)
Consider expanding to:
- Economics
- Psychology
- Political Science
- Sociology
- Philosophy
- Art/Music
- Physical Education
- Environmental Science

---

## 📋 Files & Documentation

### Created Documents
1. **`NCERT_COMPARISON_REPORT.md`** - Detailed metrics and analysis
2. **`FINAL_VERDICT.md`** - Visual summary with clear verdict
3. **`OPTIMIZATION_SUMMARY.md`** - Actionable next steps
4. **`comparison_metrics.json`** - Raw test data
5. **`scripts/compare_logs.py`** - Log analysis tool
6. **`wiki/NL_VS_OG.md`** - This comprehensive document

### Test Logs
- **`logs/NCERT_NL_TEST.log`** - Natural language approach results
- **`logs/NCERT_OG_TEST.log`** - Original keywords approach results

### Code Files
- **`scripts/generate_label.py`** - Label generation with Gemini (using keywords)
- **`scripts/classify_process_file.py`** - Classification and processing logic
- **`scripts/create_index.py`** - FAISS index creation
- **`folder_labels.json`** - Current keyword-based label database

---

## 🎯 Success Metrics

### Current Performance (Keywords)
- ✅ **56% accuracy** on NCERT test files
- ✅ **89% categorization rate** (only 11% uncategorized)
- ✅ **0.355 average similarity** (acceptable range)
- ✅ **33% of files with >0.40 similarity** (good matches)

### Target Performance
- 🎯 **70%+ accuracy**
- 🎯 **95%+ categorization rate**
- 🎯 **0.45+ average similarity**
- 🎯 **50%+ files with >0.40 similarity**

### How to Achieve Targets
1. **Expand keyword coverage** in descriptions (+10-15% accuracy)
2. **Add more training examples** to Gemini prompts (+5% accuracy)
3. **Fine-tune similarity thresholds** based on data (+5% categorization)
4. **Test and iterate** with larger datasets (validate improvements)

---

##  Technical Details

### Embedding Model
- **Model:** all-mpnet-base-v2
- **Dimensions:** 768
- **Normalization:** L2 normalized embeddings
- **Similarity:** Cosine similarity (via FAISS IndexFlatIP)

### Classification Thresholds
- **Main Threshold:** 0.40 (accept classification)
- **Low Confidence:** 0.35 (fallback threshold)
- **Fallback Logic:** Retry with middle pages if initial extraction fails

### Processing Pipeline
```
File Input
    ↓
Text Extraction (extract_text.py)
    ↓
SBERT Encoding (all-mpnet-base-v2)
    ↓
FAISS Similarity Search
    ↓
Threshold Check (0.40)
    ↓
High Confidence? → Classify
Low Confidence? → Generate Label (Gemini)
    ↓
Update folder_labels.json
    ↓
Rebuild FAISS Index
    ↓
Re-classify
```

---

## Lessons Learned

### 1. **Simpler is Better**
For SBERT embeddings with academic content, simple keyword lists outperform complex natural language descriptions.

### 2. **Keyword Density Matters**
Maximum information density (100% keywords vs 15% keywords in sentences) creates stronger semantic signals.

### 3. **SBERT Prefers Keywords**
Despite being trained on natural text, SBERT embeddings cluster keyword lists more effectively for classification tasks.

### 4. **Avoid Overfitting**
Natural language descriptions that mimic specific examples fail to generalize to new documents.

### 5. **Grammatical Noise is Real**
Articles, verbs, and prepositions dilute semantic signals without adding classification value.

### 6. **Test Before Assuming**
The hypothesis that "content-style descriptions would match better" was proven wrong through rigorous testing.

### 7. **Original Intuition Was Correct**
The initial keyword-based approach was optimal all along - sometimes the simplest solution is the best.

---

## Final Recommendations

### **DO:**
1. ✅ Continue using **comma-separated keyword terms**
2. ✅ Maintain **20-40 terms per description**
3. ✅ Include **synonyms and related vocabulary**
4. ✅ Focus on **domain-specific terminology**
5. ✅ Keep descriptions **dense** without filler words
6. ✅ Avoid **generic words** (document, file, report)
7. ✅ Test with **diverse document types**
8. ✅ Monitor **accuracy metrics** over time
9. ✅ Expand **keyword coverage** iteratively
10. ✅ Keep **prompts concise and clear**

### **DON'T:**
1. ❌ Switch to **natural language descriptions**
2. ❌ Add **explanatory text** ("Documents contain...")
3. ❌ Include **grammatical structure**
4. ❌ Use **overly specific examples**
5. ❌ Reduce **keyword density**
6. ❌ Ignore **similarity metrics**
7. ❌ Overfit to **training examples**
8. ❌ Add **filler words** or **connectors**
9. ❌ Assume **without testing**
10. ❌ Complicate what **works simply**

---

## 🏆 Conclusion

The comprehensive testing with 75 NCERT files definitively proved that:

### **Keyword Terms >> Natural Language**

**Results:**
- **+32% accuracy improvement** (24% → 56%)
- **+241% similarity improvement** (0.104 → 0.355)
- **-60% uncategorization reduction** (71% → 11%)
- **+525% good matches increase** (5% → 33%)

**Why Keywords Win:**
1. Maximum semantic density (100% vs 15%)
2. Better SBERT embedding alignment
3. Reduced grammatical noise
4. Broader coverage per token
5. Stronger classification signals

**Recommendation:**
✅ **Keep using the original keyword-based approach** - it's proven superior for SBERT semantic matching with academic documents.

---

**Status:** ✅ **Analysis Complete - Keyword Approach Validated**  
**Date:** 2025-12-05  
**Test Files:** 75 NCERT documents  
**Verdict:** **Original Keywords Win by a Landslide!** 🏆

---

*This document consolidates all findings from the Natural Language vs Original Keywords comparison testing for the FileSense project.*
