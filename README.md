# 🗂️ FileSense - Smart File Organizer

## 🔍 Overview

Tired of your Downloads folder looking like a digital junkyard — random PDFs, reports, screenshots, and JSONs all over?  
**FileSense** is an AI-powered local file organizer that sorts documents **by meaning**, not just by name or type.

It uses **SentenceTransformers** and **FAISS** to understand what each file *means*, then moves it into the right folder automatically.  
For scanned documents, it even uses **OCR (Optical Character Recognition)** to read text from images and classify them correctly.

> 🎥 **Demo / Webpage:** [FileSense](https://ahhyoushh.github.io/FileSense)

---

## ⚙️ Core Features

| Feature | Description |
|----------|-------------|
| 🧠 **Semantic Sorting** | Understands file content instead of just names using transformer embeddings. |
| ⚡ **FAISS Indexing** | Builds a fast semantic search index for folder labels. |
| 👀 **OCR Fallback** | Extracts text from scanned or image-based PDFs using `pdfplumber + pytesseract`. |
| 🧩 **Keyword Boosting** | Gives small weight bonuses for subject-specific terms (like "newton" for folder label "physics", "sql" for folder label Informatic Practices, etc). |
| 🧵 **Multithreading** | Handles multiple files simultaneously for faster performance. |
| 🕵️ **Real-time Watcher** | Detects and organizes files automatically as soon as new ones appear. |
| 🖥️ **GUI Launcher** | Desktop interface with start/stop controls, logs, and tray icon. |
| 🔒 **Offline Privacy** | Works entirely offline — nothing leaves your device. |

---

## 📁 Folder Structure

```
FileSense/
│
├── scripts/                 # All runnable scripts live here
│   ├── create_index.py      # Builds FAISS index for folder labels
│   ├── process_file.py      # Extracts, classifies, and moves files
│   ├── script.py            # CLI runner (bulk organizer)
│   ├── watcher_script.py    # Watches directory for new files
│   ├── launcher.py          # GUI app to manage scripts (optional run from repo root)
│   └── multhread.py         # Multithreading handler
│
├── folder_labels.json       # Folder names and semantic descriptions
├── folder_embeddings.faiss  # (auto-generated) FAISS vector index
└── files/                   # Drop unorganized files here
```

---

## 🔬 How It Works

### 1️⃣ Create the FAISS Index (`scripts/create_index.py`)

- Reads folder names and descriptions from `folder_labels.json`.
- Enriches descriptions with extra keywords for better context.
- Uses **SentenceTransformer (`all-mpnet-base-v2`)** to encode them.
- Builds a FAISS index for fast similarity lookups.

```bash
python scripts/create_index.py
```
> Output: `folder_embeddings.faiss` + updated `folder_labels.json`

---

### 2️⃣ Process Files in Bulk (`scripts/script.py`)

- Scans your target folder (default: `./files`)
- For each file:
  - Extracts text via PDF/DOCX/TXT/OCR.
  - Encodes the text and finds the best-matching folder embedding.
  - If similarity ≥ 0.45 (default threshold), moves it there.
  - Otherwise, falls back to keyword matches.

**Supports multithreading** via `scripts/multhread.py`:
```bash
python scripts/script.py --dir ./files --threads 8
```

---

### 3️⃣ Watch Folder in Real-time (`scripts/watcher_script.py`)

Automatically monitors a directory and sorts files as soon as they appear.

```bash
python scripts/watcher_script.py --dir ./files
```

Uses `watchdog` to detect file creation events and passes each new file to `scripts/process_file.py`.

---

### 4️⃣ Launch with GUI (`scripts/launcher.py`)

Tired of the terminal? FileSense includes a full desktop launcher with buttons, logs, and tray control.

- Start/Stop the main processor (`scripts/script.py`)
- Start/Stop the real-time watcher
- View live logs directly in the window
- Minimize to system tray and keep running in the background

Run it like this from repo root:
```bash
python -m scripts.launcher
```
or directly:
```bash
python scripts/launcher.py
```

---

## 🧩 Configuration Options

| Setting | File | Description |
|----------|------|-------------|
| `--dir` / `-d` | scripts/script.py / scripts/watcher_script.py | Directory to scan or watch. |
| `--threads` / `-t` | scripts/script.py | Maximum number of concurrent threads. |
| `THRESHOLD` | scripts/process_file.py | Minimum similarity to accept match (default 0.45). |
| `MODEL_NAME` | scripts/create_index.py | SentenceTransformer model (default: `all-mpnet-base-v2`). |

---

## 🛠️ Installation

### Requirements
- Python 3.8+
- faiss-cpu
- sentence-transformers
- numpy
- pdfplumber
- pytesseract + Pillow
- python-docx
- watchdog
- pystray (for launcher GUI)

### Install All
```bash
pip install sentence-transformers faiss-cpu numpy pdfplumber pytesseract pillow python-docx watchdog pystray
sudo apt install tesseract-ocr   # (Linux)
```

---

## 🚀 Quick Start

1. Clone the repo:
```bash
git clone https://github.com/ahhyoushh/filesense.git
cd filesense
```

2. Edit `folder_labels.json` to define your folder names and descriptions.

3. Create the FAISS index:
```bash
python scripts/create_index.py
```

4. Drop unorganized files into `/files` and run:
```bash
python scripts/script.py
```
or
```bash
python scripts/launcher.py
```

---

## 💡 Future Plans
- Auto generated folder descriptions for folder names
- Faster embedding caching
- Incremental FAISS updates (no full rebuild needed)
- Better classification for image-only documents
- Undo/recovery feature for moved files
- Auto-renaming using extracted metadata
- Simple web dashboard for previews and control

---

## 🧠 What I Learned
- **How web browsers download:** Dealt with practical edge cases like .tmp files, file locks, and renames.
- **Natural Language Embeddings:** how to use `SentenceTransformer` for semantic similarity tasks.
- **FAISS Indexing:** building a local vector database for fast nearest-neighbor searches.
- **Threading:** managing concurrent file operations without blocking I/O.
- **OCR Processing:** extracting readable text from scanned or image-only PDFs.
- **Automation with Watchdog:** event-driven file monitoring in real time.
- **GUI Development:** building a full-featured Python launcher with Tkinter and pystray.
- **Modular Architecture:** clean separation between data prep, processing, and user interaction layers.

---


## 🧾 License

MIT License © 2025 Ayush Bhalerao

---

> “Built for chaos — made it make sense.” ✨
> The counter on gtihub.io is fake lmao...
