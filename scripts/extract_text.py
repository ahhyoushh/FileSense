import os
import re

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


MAX_INPUT_CHARS = 1500
MIN_LINE_LENGTH = 15  
MIN_TITLE_LINE_LENGTH = 4

# Keywords to identify and DISCARD irrelevant pages
JUNK_PAGE_KEYWORDS = re.compile(
    r'\b(certificate|acknowledgement|declaration|submitted by|roll no|index|table of contents|bonafide)\b',
    flags=re.I
)

def is_junk_page(page_text):
    """
    Determines if a page is likely a certificate, TOC, or other non-content page.
    """
    if not page_text or not page_text.strip():
        return True # Skip empty pages

    # Rule 1: Check for keywords
    if JUNK_PAGE_KEYWORDS.search(page_text):
        return True

    # Rule 2: Check for low text density 
    if len(page_text.strip()) < 200:
        return True

    return False


def clean_and_trim(text, max_chars=MAX_INPUT_CHARS):
    """
    Cleans the final combined text and trims it to the desired length.
    """
    text = text.replace("\r", "").strip()
    if not text:
        return ""

    lines = text.split("\n")
    good = []
    for line in lines:
        l = line.strip()
        if not l:
            continue
        # Remove lines that are just symbols or numbers
        if re.match(r'^[\W_]+$', l) or re.match(r'^\s*\d+\s*$', l):
            continue
        # Keep lines that have a decent length
        if len(l) >= MIN_LINE_LENGTH:
            good.append(l)
        # Keep shorter lines if they look like headings
        elif len(l) >= MIN_TITLE_LINE_LENGTH and re.search(r'[A-Za-z]', l):
             good.append(l)

    cleaned = "\n".join(good).strip()

    # If cleaning results in an empty string, fallback to a simpler clean
    if not cleaned:
        cleaned = re.sub(r'\n\s*\n', '\n', text).strip()

    return cleaned[:max_chars]


# -----------------------
# TEXT EXTRACTION
# -----------------------
def extract_text(file_path):
    ext = file_path.lower()
    filename = os.path.basename(file_path)

    # ---- PDF ----
    if ext.endswith(".pdf"):
        if not PDFPLUMBER_AVAILABLE:
            print("pdfplumber library not found. Please install it for PDF processing.")
            return filename

        all_pages_text = []
        pdf_meta_title = None
        try:
            with pdfplumber.open(file_path) as pdf:
                # Step 1: Extract text from ALL pages and metadata
                for page in pdf.pages:
                    all_pages_text.append(page.extract_text(x_tolerance=2) or "")
                try:
                    meta = pdf.metadata if hasattr(pdf, "metadata") else {}
                    if meta:
                        title = meta.get("Title") or meta.get("title") or meta.get("Author")
                        if title and isinstance(title, str) and len(title.strip()) > 5:
                            pdf_meta_title = title.strip()
                except Exception:
                    pass
        except Exception as e:
            print(f"Error reading PDF {filename}: {e}")
            return filename

        if not any(p.strip() for p in all_pages_text):
             print(f"No text could be extracted from {filename}.")
             return filename

        # Step 2: Filter out junk pages
        good_pages_text = [text for text in all_pages_text if not is_junk_page(text)]

        # Step 3: Combine text from the good pages
        # If filtering removed everything, fallback to using all pages to get some content
        pages_to_use = good_pages_text if good_pages_text else all_pages_text
        print(f"Using {len(pages_to_use)}/{len(all_pages_text)} content pages from {filename}.")
        combined_text = "\n\n".join(pages_to_use)

        # Prepend metadata title if available
        if pdf_meta_title:
            combined_text = pdf_meta_title + "\n" + combined_text

        # Step 4: Clean the final combined text and return it
        final_text = clean_and_trim(combined_text)

        # If the final text is too short, it means cleaning was too aggressive
        # Fallback to a less aggressive combination of the first few good pages
        if len(final_text) < 100 and pages_to_use:
             return "\n".join(pages_to_use[:5])[:MAX_INPUT_CHARS]

        return final_text if final_text else filename


    # ---- DOCX ----
    elif ext.endswith(".docx"):
        if not DOCX_AVAILABLE:
            print("Required DOCX library missing. Please install python-docx.")
            return filename
        try:
            doc = docx.Document(file_path)
            raw = "\n".join([p.text for p in doc.paragraphs if p.text])
            return clean_and_trim(raw) if raw.strip() else filename
        except Exception as e:
            print(f"Failed to read DOCX {filename} — {e}")
            return filename

    # ---- TXT ----
    elif ext.endswith(".txt"):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
                return clean_and_trim(raw) if raw.strip() else filename
        except Exception as e:
            print(f"Failed to read TXT {filename} — {e}")
            return filename

    # ---- Other formats ----
    else:
        return filename

# ==============================================================================
# for testing
# ==============================================================================
if __name__ == "__main__":
    files_dir = "./files/"
    if not os.path.exists(files_dir):
        print(f"Creating directory '{files_dir}' for testing.")
        os.makedirs(files_dir)

    files_to_process = [
        os.path.join(files_dir, f)
        for f in os.listdir(files_dir)
        if os.path.isfile(os.path.join(files_dir, f))
    ]

    if not files_to_process:
        print(f"The '{files_dir}' directory is empty. Please add some files to test the script.")

    for file_path in files_to_process:
        print("-" * 50)
        print(f"Processing: {os.path.basename(file_path)}")
        extracted_text = extract_text(file_path)

        output_filename = file_path + ".extracted.txt"
        with open(output_filename, "w", encoding="utf-8") as out_f:
            out_f.write(extracted_text)
        print(f"Extracted text saved to: {output_filename}")
        print(f"Character count: {len(extracted_text)}")