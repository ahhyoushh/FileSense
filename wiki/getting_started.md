---
title: "Getting Started"
permalink: /wiki/getting-started/

---

# 🚀 Getting Started with FileSense

Get FileSense up and running in **5 minutes**.

---

## 📋 Prerequisites

Before installing FileSense, ensure you have:

- **Python 3.8+** installed
- **pip** package manager
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))
- **(Linux only)** Tesseract OCR for scanned documents

> **Check your Python version:**

```bash
python --version
# Should show Python 3.8 or higher
```

---

## 📦 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/ahhyoushh/FileSense.git
cd FileSense
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- `sentence-transformers` - SBERT embeddings
- `faiss-cpu` - Vector similarity search
- `google-genai` - Gemini API client
- `pdfplumber` - PDF text extraction
- `python-docx` - DOCX file handling
- `pytesseract` - OCR support
- `watchdog` - File system monitoring
- `pystray` - System tray integration
- `python-dotenv` - Environment variables

### Step 3: Install Tesseract OCR (Linux)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download from [GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki)

---

## 🔑 API Key Setup

### Get Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

### Configure Environment

Create a `.env` file in the project root:

```bash
# .env
API_KEY=your_gemini_api_key_here
```

> **Security tip:** Never commit `.env` to version control!

---

## 🏗️ Initialize FileSense

### Create the Initial Index

Even with no labels, you need to create the FAISS index:

```bash
python scripts/create_index.py
```

**Expected output:**
```
[!] No folder labels found in the JSON file. Cannot create index.
```

This is normal for first-time setup. The index will be created automatically when you process your first file.

---

## ✅ Verify Installation

Test that everything is working:

```bash
# Check if all imports work
python -c "import sentence_transformers, faiss, google.genai; print('✓ All dependencies installed')"
```

---

## 🎯 First Run

### Option A: GUI Launcher (Recommended)

The easiest way to use FileSense:

```bash
python scripts/launcher.py
```

**Features:**
- Visual file processing
- Real-time logs
- System tray integration
- Process management

### Option B: Command Line

Process files from the command line:

```bash
# Basic usage
python scripts/script.py --dir ./files

# With custom settings
python scripts/script.py --dir ./files --threads 8 --no-generation
```

> **CLI Options:**

| Flag | Description | Default |
|------|-------------|---------|
| `--dir` | Directory to organize | `./files` |
| `--threads` | Number of concurrent threads | `6` |
| `--single-thread` | Disable multithreading | `False` |
| `--no-generation` | Don't generate new labels | `False` |
| `--train` | Enable training mode | `False` |
| `--auto-save-logs` | Auto-save logs | `False` |
| `--no-logs` | Disable logging | `False` |

### Option C: File Watcher

Monitor a directory and auto-sort new files:

```bash
python scripts/watcher_script.py --dir ./Downloads
```

Perfect for organizing downloads in real-time!

---

## 📁 Directory Structure

After installation, your project should look like this:

```
FileSense/
├── .env                          # API key (create this)
├── folder_labels.json            # Label database (auto-created)
├── folder_embeddings.faiss       # Vector index (auto-created)
├── scripts/
│   ├── script.py                 # Main CLI
│   ├── launcher.py               # GUI app
│   ├── watcher_script.py         # File watcher
│   ├── generate_label.py         # Gemini integration
│   ├── classify_process_file.py  # Classification logic
│   ├── create_index.py           # Index builder
│   └── extract_text.py           # Text extraction
├── files/                        # Input directory
├── sorted/                       # Output directory (auto-created)
└── logs/                         # Log files (auto-created)
```

---

## 🧪 Test with Sample Files

### Create Test Files

```bash
mkdir -p files
cd files

# Create sample files
echo "Newton's laws of motion describe force and acceleration" > physics_test.txt
echo "The mitochondria is the powerhouse of the cell" > biology_test.txt
echo "Calculate the derivative of x^2 using the power rule" > math_test.txt
```

### Run Classification

```bash
cd ..
python scripts/script.py --dir ./files
```

**What happens:**
1. FileSense extracts text from each file
2. Generates embeddings using SBERT
3. Asks Gemini to create labels (first run)
4. Builds FAISS index
5. Classifies and moves files to `sorted/`

---

## 🎓 Next Steps

> **Congratulations! FileSense is now installed.** 🎉

### Learn More:
- **[FAQ](/FileSense/wiki/faq/)** - Common questions and troubleshooting

### Advanced Topics:
- **[Architecture](/FileSense/wiki/pipeline/)** - How FileSense works internally
- **[API Reference](/FileSense/wiki/api-reference/)** - Function documentation
- **[Performance Metrics](/FileSense/wiki/metrics/)** - Benchmarks and optimization

---

## 🐛 Troubleshooting

### Common Issues

**Import Error: No module named 'sentence_transformers'**
```bash
pip install sentence-transformers
```

**FAISS installation fails**
```bash
# Try CPU version
pip install faiss-cpu

# Or GPU version (if you have CUDA)
pip install faiss-gpu
```

**Tesseract not found (Windows)**
- Install Tesseract from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- Add to PATH: `C:\Program Files\Tesseract-OCR`

**API Key not working**
- Check `.env` file exists in project root
- Verify API key is valid at [Google AI Studio](https://makersuite.google.com/)
- Ensure no extra spaces in `.env` file

---

## 📚 Additional Resources

- **GitHub Repository:** [ahhyoushh/FileSense](https://github.com/ahhyoushh/FileSense)
- **Demo Video:** [YouTube](https://youtu.be/f27I2L7uoC8)
- **Project Website:** [ahhyoushh.github.io/FileSense](https://ahhyoushh.github.io/FileSense)

---

[← Back to Home](/FileSense/wiki/) | [Next: FAQ →](/FileSense/wiki/faq/)
