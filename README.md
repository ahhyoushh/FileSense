# 🗂️ FileSense - File Sorter

## 🔍 Overview

**FileSense** is an intelligent, local file organizer that sorts documents by **meaning**, not just by name or extension.

Unlike standard organizers that rely on hardcoded rules, FileSense uses **SentenceTransformers** and **FAISS** to understand the semantic context of your files. 

**✨ New :** It is now **Self-Organizing**. If FileSense encounters a document that doesn't fit any existing folder, it uses **Google Gemini (GenAI)** to analyze the content, generate a new specific category, create the folder, and update its own sorting logic automatically.

> 📺 **Overview Video**: [FileSense Demo](https://youtu.be/f27I2L7uoC8)
> 
> 🎥 **Webpage:** [ahhyoushh.github.io/FileSense](https://ahhyoushh.github.io/FileSense)

---

## ⚙️ Core Features

| Feature | Description |
|----------|-------------|
| 🧠 **Semantic Sorting** | Sorts by meaning (e.g., "Newton's Laws" → "Physics"), not just keywords. |
| 🤖 **Generative Labeling** | **(New)** Uses Google Gemini to auto-generate new categories/folders for unknown file types. |
| ⚡ **FAISS Indexing** | Uses vector databases for lightning-fast similarity searches. |
| 🔄 **Self-Updating** | When a new label is generated, the AI creates the folder and rebuilds the index automatically. |
| 👀 **OCR Support** | Extracts text from scanned PDFs and images using `pdfplumber` and `pytesseract`. |
| 🧩 **Keyword Boosting** | Hybrid search approach: Vector Similarity + Keyword weighting for maximum accuracy. |
| 🖥️ **GUI Launcher** | Desktop interface with real-time logs, system tray support, and process management. |
| 🧵 **Multithreading** | Sorts massive directories in parallel for high performance. |

---

## 📁 Folder Structure
```
FileSense/
│
├── scripts/
│   ├── RL/                       # Reinforcement Learning Module
│   ├── RL/                       # Reinforcement Learning & SFT
│   │   ├── rl_policy.py          # Epsilon-Greedy Agent
│   │   ├── rl_feedback.py        # Feedback & Rewards
│   │   ├── rl_config.py          # Hyperparameters
│   │   ├── rl_supabase.py        # Cloud Logging
│   │   └── rl_audit_safe.py      # Safety Audits
│   ├── logger/                   # Logging System
│   │   ├── logger.py             # Main Logger
│   │   └── rl_logger.py          # RL-Specific Logger
│   ├── classify_process_file.py  # Core Logic: Embedding & Classification
│   ├── generate_label.py         # GenAI Interface (Gemini)
│   ├── create_index.py           # FAISS Index Manager
│   ├── extract_text.py           # OCR & Text Extraction
│   ├── multhread.py              # Multithreading Manager
│   ├── launcher.py               # System Tray GUI
│   ├── script.py                 # CLI Entry Point
│   └── watcher_script.py         # Real-time Monitor
│
├── folder_labels.json            # Semantic Knowledge Base
├── folder_embeddings.faiss       # Vector Index
├── evaluation/                   # Metrics & Logs
└── files/                        # Default Input Directory
```

---

## 🔬 How It Works

### 1️⃣ Text Extraction
FileSense reads the file. If it's a text-based PDF/DOCX, it extracts raw text. If it's a scanned document, it applies OCR/Image processing to read the content.

### 2️⃣ Semantic Search
It converts the document text into a vector embedding and searches the local `folder_embeddings.faiss` index.
- **High Confidence (≥ 0.5):** The file is moved to the matching folder.
- **Low Confidence:** The system assumes no suitable folder exists.

### 3️⃣ Generative Classification (The "AI" Step)
If confidence is low:
1. The text is sent to **Google Gemini**.(Optional)
2. Gemini analyzes the content and determines a broad category (e.g., "Quantum Mechanics") and specific keywords.
3. It updates `folder_labels.json` (merging with existing data if needed).
4. FileSense **rebuilds the FAISS index** on the fly and classifies the file again with the new knowledge.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.8+
- A Google Cloud API Key (for Gemini)

### 2. Install Dependencies
```bash
pip install sentence-transformers faiss-cpu numpy pdfplumber pytesseract pillow python-docx watchdog pystray google-genai python-dotenv
```
## Linux Users
Install Tesseract OCR:
```bash
sudo apt install tesseract-ocr
```
---

## 3. Environment Setup
Create a `.env` file in the root directory and add your Google API key:
```bash
API_KEY=your_google_gemini_api_key_here
```
---

## 4. Initialization
Create the initial index (even if empty):
```bash
python scripts/create_index.py
```
---

# 🚀 Usage

## Option A: GUI Launcher (Recommended)
Run the desktop app to manage everything visually.
```bash
python scripts/launcher.py
```
## Option B: Real-Time Watcher
Keep it running in the background to sort files as you download them.
```bash
python scripts/watcher_script.py --dir ./Downloads
```
## Option C: Bulk Sort
Sort an existing mess of files once.
```bash
python scripts/script.py --dir ./Downloads --threads 8
```
---

## 🧾 License
MIT License © 2025 Ayush Bhalerao


# IDEAS TO IMPLEMENT
1. Use the dateset with category labels for the data, make a script to general folder labels until the similarity crosses a certain threshold for all files in the train dataset. In this way the description and folders_labels.json would be most optimised.
2. After the last update with gemini, make the model return the revised prompt and use the revised prompt so that the prompt self optimises.
3. Setup RL: let the user upload logs that include text from the file and folder label given.
4. explain why i used Sentence transformers rather than just using a tezt classifier