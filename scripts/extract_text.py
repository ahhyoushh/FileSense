import os
import re
import csv
import sys
from pathlib import Path

# Optional dependencies
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Processing configuration
PDF_CONFIG = {
    'MAX_INPUT_CHARS': 2000,        
    'QUALITY_THRESHOLD': 0.4,       
    'START_PAGE_ASSUMPTION': 3,     
    'HEADER_FOOTER_MARGIN': 70,     
    'MIN_LINE_LENGTH': 25,
    'MIN_TITLE_LINE_LENGTH': 10
}

PRINT_DEBUG = False

JUNK_PAGE_KEYWORDS = re.compile(
    r'\b(certificate|acknowledgement|declaration|submitted by|roll no|index|table of contents|bonafide|bibliography)\b',
    flags=re.I
)
RE_TABS_FF = re.compile(r'[\t\f]')
RE_BROKEN_LINES = re.compile(r'([a-z])\n([a-z])')
RE_UPPERCASE = re.compile(r'[A-Z]')

def score_page_quality(page_text):
    if not page_text:
        return 0.0

    if len(page_text) < 50: 
        return 0.0

    if JUNK_PAGE_KEYWORDS.search(page_text):
        return 0.0

    lines = [line.strip() for line in page_text.split('\n') if line.strip()]
    if not lines:
        return 0.0

    len_lines = len(lines)
    if len_lines < 5:
        return 0.1

    total_chars = sum(len(l) for l in lines)
    avg_line_length = total_chars / len_lines
    
    long_lines = sum(1 for line in lines if len(line) > 50)
    long_line_ratio = long_lines / len_lines

    score = (avg_line_length / 40) + (long_line_ratio * 1.5)
    return score


def clean_text_block(text):
    if not text:
        return ""

    text = RE_TABS_FF.sub(' ', text)
    text = RE_BROKEN_LINES.sub(r'\1 \2', text)
    
    lines = text.split('\n')
    good_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if len(stripped) < PDF_CONFIG['MIN_LINE_LENGTH'] and not RE_UPPERCASE.search(stripped):
            continue
        good_lines.append(stripped)
    
    return "\n".join(good_lines)


def extract_text_from_pdf(file_path, filename, fallback=False):
    if not PDFPLUMBER_AVAILABLE:
        print("pdfplumber library not found. Cannot process PDF.")
        return filename

    content_blocks = []
    total_chars = 0
    pdf_meta_title = None

    try:
        with pdfplumber.open(file_path) as pdf:
            if pdf.metadata and not fallback:
                title = pdf.metadata.get("Title") or pdf.metadata.get("title")
                if title and isinstance(title, str) and len(title.strip()) > 5:
                    pdf_meta_title = title.strip()

            total_pages = len(pdf.pages)
            
            if fallback and total_pages > 5:
                # Start from the document midpoint
                start_page_index = total_pages // 2
            else:
                # Default to page 3 (skipping cover/toc)
                start_page_index = min(PDF_CONFIG['START_PAGE_ASSUMPTION'], total_pages - 1)

            # Create iterator order
            page_order = list(range(start_page_index, total_pages)) + list(range(0, start_page_index))

            for page_index in page_order:
                page = pdf.pages[page_index]
                
                try:
                    core_page = page.crop((0, PDF_CONFIG['HEADER_FOOTER_MARGIN'], page.width, page.height - PDF_CONFIG['HEADER_FOOTER_MARGIN']))
                    page_text = core_page.extract_text(x_tolerance=2) or ""
                except ValueError:
                    page_text = page.extract_text() or ""
                
                quality = score_page_quality(page_text)
                
                threshold = PDF_CONFIG['QUALITY_THRESHOLD'] * 0.8 if fallback else PDF_CONFIG['QUALITY_THRESHOLD']

                if quality > threshold:
                    cleaned_block = clean_text_block(page_text)
                    if cleaned_block:
                        content_blocks.append(cleaned_block)
                        total_chars += len(cleaned_block)
                        if total_chars > PDF_CONFIG['MAX_INPUT_CHARS']:
                            break
            
    except Exception as e:
        print(f"Error reading PDF {filename}: {e}")
        return filename

    if not content_blocks:
        return filename

    final_text = "\n\n".join(content_blocks)
    
    if pdf_meta_title and not fallback:
        final_text = pdf_meta_title + "\n\n" + final_text

    return final_text[:PDF_CONFIG['MAX_INPUT_CHARS']]

def extract_text_from_docx(file_path, filename, fallback=False):
    if not DOCX_AVAILABLE:
        return filename
    try:
        doc = docx.Document(file_path)
        content_list = []
        current_length = 0
        
        all_paras = doc.paragraphs
        total_paras = len(all_paras)

        if fallback and total_paras > 20:
            start_index = total_paras // 2
        else:
            start_index = 0
        
        for i in range(start_index, total_paras):
            text = all_paras[i].text
            if text:
                content_list.append(text)
                current_length += len(text)
                if current_length > PDF_CONFIG['MAX_INPUT_CHARS'] * 1.2:
                    break
        
        raw = "\n".join(content_list)
        return clean_text_block(raw)[:PDF_CONFIG['MAX_INPUT_CHARS']] if raw.strip() else filename
    except Exception as e:
        print(f"Failed to read DOCX {filename} — {e}")
        return filename

def extract_text_from_txt(file_path, filename, fallback=False):
    try:
        file_size = os.path.getsize(file_path)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            if fallback and file_size > PDF_CONFIG['MAX_INPUT_CHARS']:
                f.seek(file_size // 2)
                f.readline()
            
            raw = f.read(PDF_CONFIG['MAX_INPUT_CHARS'] * 2) 
            return clean_text_block(raw)[:PDF_CONFIG['MAX_INPUT_CHARS']] if raw.strip() else filename
    except Exception as e:
        print(f"Failed to read TXT {filename} — {e}")
        return filename

# --- Dispatcher ---
def extract_text(file_path, fallback=False):
    """
    Main function to dispatch file processing.
    """
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path, filename, fallback=fallback)

    elif ext == ".docx":
        return extract_text_from_docx(file_path, filename, fallback=fallback)

    elif ext == ".txt":
        return extract_text_from_txt(file_path, filename, fallback=fallback)
            
    return filename

# --- Dataset Generation ---
if __name__ == "__main__":
    # --- Paths Setup ---
    # Assuming script is in FileSense/scripts/
    # We want to scan FileSense/sorted/
    BASE_DIR = Path(__file__).resolve().parent.parent # Go up to FileSense root
    SORTED_DIR = BASE_DIR / "sorted"
    OUTPUT_CSV = BASE_DIR / "dataset.csv"

    # SFT Instruction
    SYSTEM_INSTRUCTION = (
        "Analyze the text and classify into JSON with keys: 'folder_label', 'description', 'keywords'. "
        "Banned words: project, assignment, file, pdf, report."
    )

    print(f"--- Scanning directory: {SORTED_DIR} ---")
    
    if not SORTED_DIR.exists():
        print(f"ERROR: The directory '{SORTED_DIR}' does not exist.")
        sys.exit(1)

    rows = []
    processed_count = 0
    
    # Walk through directory
    for root, dirs, files in os.walk(SORTED_DIR):
        # Determine the folder label from the directory name
        # root is 'FileSense/sorted/Physics', so label is 'Physics'
        current_folder_path = Path(root)
        
        # Skip the root 'sorted' folder itself if files are loose inside it
        if current_folder_path == SORTED_DIR:
            folder_label = "Unclassified" # Or skip files in root
        else:
            folder_label = current_folder_path.name
        
        for file in files:
            if file.lower().endswith(('.pdf', '.docx', '.txt')):
                full_path = os.path.join(root, file)
                print(f"Processing [{folder_label}]: {file}...", end="\r")
                
                extracted_text = extract_text(full_path)
                
                # Check quality
                if extracted_text and extracted_text != file and len(extracted_text) > 100:
                    # Pre-fill the JSON structure partially
                    partial_json = f'{{"folder_label": "{folder_label}", "description": "", "keywords": ""}}'
                    
                    rows.append({
                        "instruction": SYSTEM_INSTRUCTION,
                        "input": extracted_text.replace('"', "'"), # Escape quotes in text
                        "output": partial_json 
                    })
                    processed_count += 1
                else:
                    # Retry with fallback
                    extracted_text = extract_text(full_path, fallback=True)
                    if extracted_text and extracted_text != file and len(extracted_text) > 100:
                        partial_json = f'{{"folder_label": "{folder_label}", "description": "", "keywords": ""}}'
                        
                        rows.append({
                            "instruction": SYSTEM_INSTRUCTION,
                            "input": extracted_text.replace('"', "'"),
                            "output": partial_json
                        })
                        processed_count += 1

    print(f"\n\nProcessing complete. Found {processed_count} documents.")
    
    if rows:
        try:
            with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as csv_file:
                fieldnames = ['instruction', 'input', 'output']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(rows)
            
            print(f"SUCCESS: Dataset saved to '{OUTPUT_CSV}'.")
        except IOError as e:
            print(f"ERROR: Could not write to file. {e}")
    else:
        print("WARNING: No valid documents found.")