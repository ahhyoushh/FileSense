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

    # Calculate metrics
    total_chars = sum(len(l) for l in lines)
    avg_line_length = total_chars / len_lines
    
    # Reward long, paragraph-like lines
    long_lines = sum(1 for line in lines if len(line) > 50)
    long_line_ratio = long_lines / len_lines

    score = (avg_line_length / 40) + (long_line_ratio * 1.5)
    return score


def clean_text_block(text):
    if not text:
        return ""

    # Use pre-compiled regex
    text = RE_TABS_FF.sub(' ', text)
    text = RE_BROKEN_LINES.sub(r'\1 \2', text)
    
    lines = text.split('\n')
    good_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Optimization: Combine checks
        if len(stripped) < PDF_CONFIG['MIN_LINE_LENGTH'] and not RE_UPPERCASE.search(stripped):
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
            # Metadata extraction
            if pdf.metadata:
                title = pdf.metadata.get("Title") or pdf.metadata.get("title")
                if title and isinstance(title, str) and len(title.strip()) > 5:
                    pdf_meta_title = title.strip()

            total_pages = len(pdf.pages)
            
            # Logic to check middle pages first (likely content), then start pages
            start_page_index = min(PDF_CONFIG['START_PAGE_ASSUMPTION'], total_pages - 1)
            
            # Create iterator order
            page_order = list(range(start_page_index, total_pages)) + list(range(0, start_page_index))

            for page_index in page_order:
                page = pdf.pages[page_index]
                
                # Crop header/footer
                try:
                    core_page = page.crop((0, PDF_CONFIG['HEADER_FOOTER_MARGIN'], page.width, page.height - PDF_CONFIG['HEADER_FOOTER_MARGIN']))
                    page_text = core_page.extract_text(x_tolerance=2) or ""
                except ValueError:
                    # Fallback if cropping fails (e.g., page too small)
                    page_text = page.extract_text() or ""
                
                quality = score_page_quality(page_text)
                
                if quality > PDF_CONFIG['QUALITY_THRESHOLD']:
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
    if pdf_meta_title:
        final_text = pdf_meta_title + "\n\n" + final_text

    return final_text[:PDF_CONFIG['MAX_INPUT_CHARS']]

def extract_text_from_docx(file_path, filename):
    if not DOCX_AVAILABLE:
        return filename
    try:
        doc = docx.Document(file_path)
        content_list = []
        current_length = 0
        
        # Optimization: Iterate and break early instead of joining all paragraphs
        for p in doc.paragraphs:
            text = p.text
            if text:
                content_list.append(text)
                current_length += len(text)
                if current_length > PDF_CONFIG['MAX_INPUT_CHARS'] * 1.2: # Small buffer
                    break
        
        raw = "\n".join(content_list)
        return clean_text_block(raw)[:PDF_CONFIG['MAX_INPUT_CHARS']] if raw.strip() else filename
    except Exception as e:
        print(f"Failed to read DOCX {filename} — {e}")
        return filename

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
        return extract_text_from_docx(file_path, filename)

    elif ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                # Optimization: Read only what we need plus a safety buffer for cleaning
                raw = f.read(PDF_CONFIG['MAX_INPUT_CHARS'] * 2) 
                return clean_text_block(raw)[:PDF_CONFIG['MAX_INPUT_CHARS']] if raw.strip() else filename
        except Exception as e:
            print(f"Failed to read TXT {filename} — {e}")
            return filename
            
    return filename 

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

    for file_path in files_to_process:
        print("-" * 60)
        print(f"Processing: {os.path.basename(file_path)}")
        
        extracted_text = extract_text(file_path)
        
        print(f"Extracted text length: {len(extracted_text)}")
        print(f"Preview: {extracted_text[:200]}...")