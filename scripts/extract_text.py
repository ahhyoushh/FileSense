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
MIN_LINE_LENGTH = 25
MIN_TITLE_LINE_LENGTH = 4
KEYWORD_RE = re.compile(r'\b(ray|optics|refraction|reflection|chapter|contents|index|table of contents|lens|prism)\b', flags=re.I)

def clean_and_trim(text, max_chars=MAX_INPUT_CHARS, aggressive=True):
    text = text.replace("\r", "").strip()
    if not text:
        return ""

    lines = text.split("\n")
    good = []
    for line in lines:
        l = line.strip()
        if not l:
            continue
        if re.match(r'^[\W_]+$', l): #symbols and white spaces
            continue
        if re.match(r'^\s*\d+\s*$', l): #line with only a number
            continue
        if len(l) < MIN_LINE_LENGTH:
            if len(l) >= MIN_TITLE_LINE_LENGTH and re.search(r'[A-Za-z0-9]', l): # short but looks like a title
                good.append(l)
            else:
                continue
        else:
            good.append(l)

    cleaned = "\n".join(good).strip()
    if not cleaned and aggressive:
        return text[:max_chars].strip()
    return cleaned[:max_chars].strip()


def extract_key_context_from_pages(pages_text, lookahead=2, lookbehind=1):
    for page_txt in pages_text[:3]:
        if not page_txt:
            continue
        lines = [ln.strip() for ln in page_txt.splitlines() if ln.strip()]
        for i, ln in enumerate(lines):
            if KEYWORD_RE.search(ln):
                start = max(0, i - lookbehind)
                end = min(len(lines), i + lookahead + 1)
                ctx_lines = lines[start:end]
                ctx = "\n".join(ctx_lines).strip()
                if ctx:
                    return ctx
    return None


# -----------------------
# TEXT EXTRACTION
# -----------------------
def extract_text(file_path):
    ext = file_path.lower()
    filename = os.path.basename(file_path)

    # ---- PDF ----
    if ext.endswith(".pdf"):
        if not PDFPLUMBER_AVAILABLE and not OCR_AVAILABLE:
            print("Required PDF/OCR libraries missing. Please install pdfplumber, pytesseract, and pdf2image.")
            return filename

        pages = []
        pdf_meta_title = None
        # First attempt with pdfplumber
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        pages.append(page.extract_text() or "")
                    # try to read metadata/title
                    try:
                        meta = pdf.metadata if hasattr(pdf, "metadata") else {}
                        if meta:
                            title = meta.get("Title") or meta.get("title") or meta.get("Author")
                            if title and isinstance(title, str) and len(title.strip()) > 5:
                                pdf_meta_title = title.strip()
                    except Exception:
                        pdf_meta_title = None
            except Exception as e:
                print(f"pdfplumber failed to read {filename} — {e}")
                pages = [] # Reset pages if pdfplumber fails

        # Fallback to OCR if pdfplumber failed or text is empty
        if not any(p.strip() for p in pages) and OCR_AVAILABLE:
            print(f"No text from pdfplumber, attempting OCR for {filename}...")
            try:
                # Try direct OCR on images first
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages[:3]:
                        img = page.to_image(resolution=300).original
                        ocr_text = pytesseract.image_to_string(img, config="--psm 1", lang="eng")
                        pages.append(ocr_text or "")
            except Exception:
                # Fallback to pdf2image if direct imaging fails
                try:
                    imgs = convert_from_path(file_path, first_page=1, last_page=3)
                    for img in imgs:
                        txt = pytesseract.image_to_string(img, config="--psm 1", lang="eng")
                        pages.append(txt)
                except Exception as ex:
                    print("Fallback OCR failed:", ex)

        key_ctx = extract_key_context_from_pages(pages)
        if key_ctx:
            combined = (pdf_meta_title + "\n" if pdf_meta_title else "") + key_ctx
            return clean_and_trim(combined)

        first_pages_text = "\n\n".join([p or "" for p in pages[:3]])
        cleaned_first = clean_and_trim(first_pages_text, aggressive=False)
        if cleaned_first and len(cleaned_first) > 40:
            if pdf_meta_title:
                combined = pdf_meta_title + "\n" + cleaned_first
                return clean_and_trim(combined)
            return cleaned_first

        whole_text = "\n\n".join([p or "" for p in pages])
        cleaned_whole = clean_and_trim(whole_text)
        if cleaned_whole:
            if pdf_meta_title:
                return clean_and_trim(pdf_meta_title + "\n" + cleaned_whole)
            return cleaned_whole

        return filename

    # ---- DOCX ----
    elif ext.endswith(".docx"):
        if not DOCX_AVAILABLE:
            print("Required DOCX library missing. Please install python-docx.")
            return filename
        try:
            doc = docx.Document(file_path)
            raw = "\n".join([p.text for p in doc.paragraphs if p.text])
            if not raw.strip():
                return filename
            return clean_and_trim(raw)
        except Exception as e:
            print(f"Failed to read DOCX {filename} — {e}")
            return filename

    # ---- TXT ----
    elif ext.endswith(".txt"):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
                if not raw.strip():
                    return filename
                return clean_and_trim(raw)
        except Exception as e:
            print(f"Failed to read TXT {filename} — {e}")
            return filename

    # ---- Other formats ----
    else:
        return filename