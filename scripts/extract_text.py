import os
import re

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

# --- Configuration ---
PDF_CONFIG = {
    'MAX_INPUT_CHARS': 2000,        
    'QUALITY_THRESHOLD': 0.4,       # Min score for a page to be considered good
    'START_PAGE_ASSUMPTION': 3,     # Assumes content starts around page 3-4
    'HEADER_FOOTER_MARGIN': 70,     # Pixels from top/bottom to ignore for ocr
    'MIN_LINE_LENGTH': 25,
    'MIN_TITLE_LINE_LENGTH': 10
}

PRINT_DEBUG = False

JUNK_PAGE_KEYWORDS = re.compile(
    r'\b(certificate|acknowledgement|declaration|submitted by|roll no|index|table of contents|bonafide|bibliography)\b',
    flags=re.I
)

def score_page_quality(page_text):
    if not page_text or not page_text.strip():
        return 0.0

    if JUNK_PAGE_KEYWORDS.search(page_text):
        return 0.0

    lines = [line.strip() for line in page_text.split('\n') if line.strip()]
    if not lines:
        return 0.0

    # Penalize pages with very few lines
    if len(lines) < 5:
        return 0.1

    # Calculate metrics
    total_chars = len("".join(lines))
    avg_line_length = total_chars / len(lines)
    
    # Reward long, paragraph-like lines
    long_lines = sum(1 for line in lines if len(line) > 50)
    long_line_ratio = long_lines / len(lines)

    # Calculate a score. This heuristic rewards pages that resemble paragraphs.
    score = (avg_line_length / 40) + (long_line_ratio * 1.5)

    return score


def clean_text_block(text):
    if not text:
        return ""

    text = re.sub(r'[\t\f]', ' ', text)
    
    # This heuristic looks for a lowercase letter followed by a newline and then another lowercase letter.
    text = re.sub(r'([a-z])\n([a-z])', r'\1 \2', text)
    
    lines = text.split('\n')
    good_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if len(stripped) < PDF_CONFIG['MIN_LINE_LENGTH'] and not re.search(r'[A-Z]', stripped):
            continue
        good_lines.append(stripped)
    
    return "\n".join(good_lines)


def extract_text_from_pdf(file_path, filename):
    if not PDFPLUMBER_AVAILABLE:
        print("pdfplumber library not found. Cannot process PDF.")
        return filename

    content_blocks = []
    total_chars = 0
    pdf_meta_title = None

    try:
        with pdfplumber.open(file_path) as pdf:
            # Attempt to get metadata title first
            try:
                meta = pdf.metadata or {}
                title = meta.get("Title") or meta.get("title")
                if title and isinstance(title, str) and len(title.strip()) > 5:
                    pdf_meta_title = title.strip()
            except Exception:
                pass

            total_pages = len(pdf.pages)
            start_page_index = min(PDF_CONFIG['START_PAGE_ASSUMPTION'], total_pages - 1)
            
            page_indices_pass1 = range(start_page_index, total_pages)
            page_indices_pass2 = range(0, start_page_index)

            for page_index in list(page_indices_pass1) + list(page_indices_pass2):
                page = pdf.pages[page_index]
                
                core_page = page.crop((0, PDF_CONFIG['HEADER_FOOTER_MARGIN'], page.width, page.height - PDF_CONFIG['HEADER_FOOTER_MARGIN']))
                
                page_text = core_page.extract_text(x_tolerance=2) or ""
                
                quality = score_page_quality(page_text)
                
                if quality > PDF_CONFIG['QUALITY_THRESHOLD']:
                    cleaned_block = clean_text_block(page_text)
                    if cleaned_block:
                        content_blocks.append(cleaned_block)
                        total_chars += len(cleaned_block)
                        if total_chars > PDF_CONFIG['MAX_INPUT_CHARS']:
                            print(f"Sufficient text gathered after processing page {page_index + 1}/{total_pages}.")
                            break
            
    except Exception as e:
        print(f"Error reading PDF {filename}: {e}")
        return filename

    if not content_blocks:
        print(f"Could not extract high-quality content from {filename}.")
        return filename

    final_text = "\n\n".join(content_blocks)
    if pdf_meta_title:
        final_text = pdf_meta_title + "\n\n" + final_text

    return final_text[:PDF_CONFIG['MAX_INPUT_CHARS']]

# -----------------------
# MAIN DISPATCHER
# -----------------------
def extract_text(file_path):
    """Main function to dispatch file processing based on extension."""
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path, filename)

    elif ext == ".docx":
        if not DOCX_AVAILABLE:
            return filename
        try:
            doc = docx.Document(file_path)
            raw = "\n".join([p.text for p in doc.paragraphs if p.text])
            return clean_text_block(raw)[:PDF_CONFIG['MAX_INPUT_CHARS']] if raw.strip() else filename
        except Exception as e:
            print(f"Failed to read DOCX {filename} — {e}")
            return filename

    elif ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
                return clean_text_block(raw)[:PDF_CONFIG['MAX_INPUT_CHARS']] if raw.strip() else filename
        except Exception as e:
            print(f"Failed to read TXT {filename} — {e}")
            return filename
            
    return filename # Fallback for other formats


# ==============================================================================
# for testing
# ==============================================================================
if __name__ == "__main__":
    files_dir = "./files/"
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)
        print(f"Created directory '{files_dir}'. Please add files to test.")

    files_to_process = [
        os.path.join(files_dir, f)
        for f in os.listdir(files_dir)
        if os.path.isfile(os.path.join(files_dir, f)) and not f.endswith('.extracted.txt')
    ]

    if not files_to_process:
        print(f"The '{files_dir}' directory is empty.")

    for file_path in files_to_process:
        print("-" * 60)
        print(f"Processing: {os.path.basename(file_path)}")
        
        extracted_text = extract_text(file_path)
        
        output_filename = file_path + ".extracted.txt"
        with open(output_filename, "w", encoding="utf-8") as out_f:
            out_f.write(extracted_text)
            
        print(f"Extracted text saved to: {output_filename}")
        print(f"Character count: {len(extracted_text)}")