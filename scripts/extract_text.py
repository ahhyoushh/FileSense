import os, re

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
        if re.match(r'^[\W_]+$', l):
            continue
        if re.match(r'^\s*\d+\s*$', l):
            continue
        if len(l) < MIN_LINE_LENGTH:
            if len(l) >= MIN_TITLE_LINE_LENGTH and re.search(r'[A-Za-z0-9]', l):
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
    for page_txt in enumerate(pages_text[:3]):
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

    # ---- PDF ----
    if ext.endswith(".pdf"):
        try:
            import pdfplumber
            import pytesseract
        except Exception as e:
            print("Required PDF/OCR libraries missing:", e)
            return os.path.basename(file_path)

        pages = []
        pdf_meta_title = None
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    try:
                        pt = page.extract_text() or ""
                    except Exception:
                        pt = ""
                    pages.append(pt)

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
            print(f"Failed to open/read PDF {os.path.basename(file_path)} — {e}")
            try:
                from pdf2image import convert_from_path
                pages = []
                imgs = convert_from_path(file_path, first_page=1, last_page=3)
                for img in imgs:
                    txt = pytesseract.image_to_string(img, config="--psm 1", lang="eng")
                    pages.append(txt)
            except Exception as ex:
                print("Fallback OCR failed:", ex)
                return os.path.basename(file_path)

        if not any(pages):
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages[:3]:
                        try:
                            img = page.to_image(resolution=300).original
                            ocr_text = pytesseract.image_to_string(img, config="--psm 1", lang="eng")
                            pages.append(ocr_text or "")
                        except Exception as e:
                            pages.append("")
            except Exception:
                pass

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


        return os.path.basename(file_path)

    # ---- DOCX ----
    elif ext.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(file_path)
            raw = "\n".join([p.text for p in doc.paragraphs if p.text])
            if not raw.strip():
                return os.path.basename(file_path)
            return clean_and_trim(raw)
        except Exception as e:
            print(f"Failed to read DOCX {os.path.basename(file_path)} — {e}")
            return os.path.basename(file_path)

    # ---- TXT ----
    elif ext.endswith(".txt"):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
                if not raw.strip():
                    return os.path.basename(file_path)
                return clean_and_trim(raw)
        except Exception as e:
            print(f"Failed to read TXT {os.path.basename(file_path)} — {e}")
            return os.path.basename(file_path)

    # ---- Other formats ----
    else:
        return os.path.basename(file_path)

