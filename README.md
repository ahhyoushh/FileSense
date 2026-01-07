# FileSense

An intelligent file organization system that leverages semantic understanding to categorize documents.

## Introduction

FileSense is a local file management utility that organizes documents based on their semantic content rather than relying on filename patterns or extensions. It utilizes SentenceTransformers for vector embeddings and FAISS for efficient similarity indexing.

Key capabilities include:
- **Semantic Classification**: Maps files to categories based on meaning (e.g., "thermodynamics_notes.pdf" → "Physics").
- **Automated Labeling**: Integrates with Google Gemini to propose new categories for documents that do not match existing templates.
- **OCR Integration**: Supports text extraction from images and scanned PDFs via `pdfplumber` and `Tesseract`.
- **Concurrency**: Parallel processing for handling large datasets.
- **Monitoring**: Real-time folder watching for automated sorting of new downloads.

## Technical Architecture

### Component Overview
- **Core Engine**: `classify_process_file.py` handles the main classification pipeline.
- **Vector Database**: Uses FAISS for high-performance similarity search.
- **Inference**: Supports various SentenceTransformer models (default: `bge-base-en-v1.5`).
- **RL Module**: Optional Reinforcement Learning module for policy-based classification improvement.

### Project Structure
```text
FileSense/
├── scripts/
│   ├── RL/                 # Reinforcement Learning & SFT logic
│   ├── logger/             # Unified logging system
│   ├── main.py             # CLI entry point (replaces script.py)
│   ├── watcher.py          # Filesystem monitor (replaces watcher_script.py)
│   ├── launcher.py         # Tkinter-based GUI
│   └── ...                 # Utility modules (OCR, Labelling, Indexing)
├── folder_labels.json      # Category definitions and keyword mappings
└── folder_embeddings.faiss # Pre-computed vector index
```

## Setup and Installation

### Prerequisites
- Python 3.8+
- Tesseract OCR (Optional, for OCR support)
- Google Gemini API Key (Optional, for automated category generation)

### Installation
```bash
pip install -r requirements.txt
```

### Environment Configuration
Create a `.env` file in the root directory:
```env
API_KEY=your_google_gemini_api_key
```

### Initialization
To initialize a knowledge base from preseeded data:
1. Copy `preseeded.json` to `folder_labels.json`.
2. Generate the vector index:
   ```bash
   python scripts/create_index.py
   ```

## Usage

### GUI Launcher
```bash
python scripts/launcher.py
```

### Command Line Interface
```bash
python scripts/main.py --dir ./path/to/files --threads 4
```

### Background Monitor
```bash
python scripts/watcher.py --dir ./Downloads
```

## Privacy and RL
FileSense operates strictly locally by default. The Reinforcement Learning (RL) features, which log classification metrics for policy optimization, are disabled by default. Use the `--enable-rl` flag to opt-in to these features.

## License
MIT License

## Roadmap & Future Enhancements
1. **Automated Knowledge Optimization**: Implement scripts to iteratively refine category descriptions until semantic similarity thresholds are met across training datasets.
2. **Self-Optimizing Prompts**: Enable the model to return revised instructions after each classification update to improve zero-shot accuracy.
3. **Reinforcement Learning Feedback**: Allow users to contribute manual classification corrections to optimize the underlying RL policy.
4. **Model Comparative Analysis**: Document the specific advantages of using SentenceTransformers versus traditional text classifiers for cross-domain file sorting.
