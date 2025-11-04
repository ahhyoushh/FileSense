# 🗂️ FileSense - Smart File Organizer

## 🔍 Overview

I got sick of the Downloads chaos: random JSONs, reports, scanned PDFs, and screenshots all mixed up.  
**FileSense** is a practical Python tool that automatically organizes your files by *meaning*, not just extension.

It blends semantic embeddings (SentenceTransformers) with a FAISS index to map a file’s content to human-readable folder labels. For scanned PDFs it even falls back to OCR.
I found it weirdly satisfying using this script lol.
I am still working on this project...

## ⚙️ Core Idea (what makes it smart)

- **Semantic matching**: instead of relying only on filenames or extensions, FileSense encodes folder *descriptions* and file *content* into embeddings and compares them. That means files get grouped by intent: invoices with invoices, lab reports with lab reports, config files with other configs.
- **FAISS index**: pre-builds embeddings for your folder labels (fast nearest-neighbour lookups).
- **OCR fallback for PDFs**: if a PDF has no extracted text, FileSense runs OCR (pdfplumber → PIL → pytesseract) so scanned documents still get classified.
- **Keyword boosting**: subject-specific keywords (physics, chemistry, python, etc.) give a small similarity boost so short filenames don't get lost.
- **Local-first**: runs on your machine (desktop or an old phone/Termux if you want), nothing needs to leave your disk.

## 🔧 What’s inside

- `files/` — the folder you point FileSense at (configurable).
- `script.py` — main processor: extracts text, classifies, and moves files.
- `create_index.py` — builds a FAISS index from `folder_labels.json`.
- `folder_labels.json` — human-friendly folder labels + descriptions used for semantic indexing.
- `folder_embeddings.faiss` — (generated) FAISS index file.

## 🔬 How it works (detailed)

1. **Index creation** (`create_index.py`)
   - Loads `folder_labels.json` (label → description).
   - Appends a few extra keyword examples per label to strengthen signal.
   - Uses `SentenceTransformer` (`all-mpnet-base-v2` by default) to generate normalized embeddings for each folder label description.
   - Writes a FAISS index (`folder_embeddings.faiss`) for fast dot-product similarity lookups.

2. **Processing files** (`script.py`)
   - Walk `files/` directory and handle each file:
     - **Text extraction**:
       - `.pdf`: try `pdfplumber` text extraction. If a page returns no text, convert page to image and run `pytesseract` OCR on it. If all fails, fallback to filename.
       - `.docx`: read with `python-docx`.
       - `.txt`: read as UTF-8 text.
       - Other file types: fallback to filename (so images or binaries are still handled).
     - **Embed & classify**:
       - Clean and normalize text.
       - Use the same SentenceTransformer model to encode the file text.
       - Compute cosine similarity between file embedding and precomputed folder description embeddings.
       - Apply a small boost if keywords (from `keyword_map`) are found in the text.
       - If the best similarity ≥ `THRESHOLD` (0.45 by default), move the file to that folder. Otherwise, try keyword-only match or move to `Unsorted`.
     - **Move**: create predicted folder and `shutil.move()` the file.

3. **Why OCR matters**
   - Many real-world docs (photos of receipts, scanned lab reports) have zero extractable text. Without OCR, a scanned invoice looks like an image and would end up unsorted. The PDF → page image → `pytesseract` flow gives FileSense the ability to classify scanned documents by their actual text — huge win for real downloads.

## 📦 Requirements

- Python 3.8+
- `faiss` (CPU version)
- `sentence-transformers`
- `numpy`
- `pandas` (optional if you use logging/analysis)
- `pdfplumber` (for PDFs)
- `pytesseract` + `Pillow` (OCR)
- `python-docx` (for .docx)
- `scikit-learn` (optional; current code uses cosine via numpy but you may want metrics)
- System: `tesseract-ocr` installed (for `pytesseract` to work)

Install example:

```bash
pip install sentence-transformers faiss-cpu numpy pdfplumber pytesseract pillow python-docx
# plus system-level: sudo apt install tesseract-ocr
```

## 🛠️ Quick start

Clone:
```bash
git clone https://github.com/ahhyoushh/filesense.git
cd filesense
```


### Edit folder_labels.json to match the folders you want (labels → descriptions).

### Create FAISS index:
``` bash 
python create_index.py
# outputs folder_embeddings.faiss and updates folder_labels.json
```

### Drop files into files/ and run:
```bash
python script.py
```

Check output folders created in repo root (e.g. Physics/, Invoices/, Unsorted/).

## ⚙️ Config you should know

- files_dir in script.py — folder to scan.

- THRESHOLD — minimum similarity score to accept a semantic match. Lower = more aggressive sorting; higher = more conservative.

- MODEL_NAME in create_index.py — change to a different SentenceTransformer if you want a lighter/heavier model.

## 🔮 Future additions

- Improve image classification for purely visual docs (screenshots with very little text).

- Add file renaming suggestions using detected metadata (dates, invoice numbers).

- Add a small web UI for preview + undo moves.

- Add incremental indexing so adding a new label doesn’t require rebuilding everything.

## 💡 Notes & design thoughts

- The OCR fallback is intentionally aggressive, many real-world documents are scans or photos. That “extra step” is what makes FileSense actually useful instead of just neat.

- FAISS + SentenceTransformers lets you use meaning rather than brittle filename heuristics. That combination is small and local but powerful.

- Built keeping privacy and speed in mind, you can run this on an old phone via Termux or on a laptop. No cloud required.

