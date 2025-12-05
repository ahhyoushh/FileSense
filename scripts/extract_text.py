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
            
            # --- Fallback Logic ---
            if fallback and total_pages > 5:
                # Start from the absolute middle of the document
                start_page_index = total_pages // 2
                print(f"   -> [PDF Fallback] Starting extraction at page {start_page_index} (Middle)")
            else:
                # Standard Logic: Start around page 3
                start_page_index = min(PDF_CONFIG['START_PAGE_ASSUMPTION'], total_pages - 1)

            # Create iterator order
            # If fallback, we read from middle to end, then beginning to middle
            page_order = list(range(start_page_index, total_pages)) + list(range(0, start_page_index))

            for page_index in page_order:
                page = pdf.pages[page_index]
                
                try:
                    core_page = page.crop((0, PDF_CONFIG['HEADER_FOOTER_MARGIN'], page.width, page.height - PDF_CONFIG['HEADER_FOOTER_MARGIN']))
                    page_text = core_page.extract_text(x_tolerance=2) or ""
                except ValueError:
                    page_text = page.extract_text() or ""
                
                quality = score_page_quality(page_text)
                
                # In fallback mode, we might lower quality threshold slightly to ensure we get *something*
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
    
    # Only prepend metadata title on the standard attempt (avoid noise on fallback)
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

        # --- Fallback Logic ---
        if fallback and total_paras > 20:
            start_index = total_paras // 2
            print(f"   -> [DOCX Fallback] Starting extraction at paragraph {start_index}")
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
                # Seek to middle
                f.seek(file_size // 2)
                # Discard partial line
                f.readline()
                print(f"   -> [TXT Fallback] Starting extraction from middle of file")
            
            raw = f.read(PDF_CONFIG['MAX_INPUT_CHARS'] * 2) 
            return clean_text_block(raw)[:PDF_CONFIG['MAX_INPUT_CHARS']] if raw.strip() else filename
    except Exception as e:
        print(f"Failed to read TXT {filename} — {e}")
        return filename

# -----------------------
# MAIN DISPATCHER
# -----------------------
def extract_text(file_path, fallback=False):
    """
    Main function to dispatch file processing.
    :param fallback: If True, tries to extract text from the middle/end of the file 
                     to avoid table of contents/cover pages.
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