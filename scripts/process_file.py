import os, shutil, json, faiss,re
import time
from sentence_transformers import SentenceTransformer
import numpy as np
from create_index import MODEL_NAME
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # main FileSense folder
FAISS_INDEX_FILE = BASE_DIR / "folder_embeddings.faiss"
LABELS_FILE = BASE_DIR / "folder_labels.json"

THRESHOLD = 0.45  # similarity threshold

index = faiss.read_index(str(FAISS_INDEX_FILE))
with open(LABELS_FILE, "r", encoding="utf-8") as f:
    folder_data = json.load(f)

FOLDER_LABELS = list(folder_data.keys())
FOLDER_DESC = list(folder_data.values())
model = SentenceTransformer(MODEL_NAME, device="cpu")


MAX_INPUT_CHARS = 1500  # ideal range for SFT
MIN_LINE_LENGTH = 25    # avoid junk lines (OCR garbage etc)

def clean_and_trim(text, max_chars=MAX_INPUT_CHARS):
    # normalize whitespace
    text = text.replace("\r", "").strip()
    
    # split lines and keep only meaningful ones
    lines = text.split("\n")
    good = []
    for line in lines:
        line = line.strip()
        if len(line) < MIN_LINE_LENGTH:
            continue  # skip tiny garbage lines
        if re.match(r"^[\W_]+$", line):
            continue  # skip lines that are only symbols
        good.append(line)

    cleaned = "\n".join(good)
    return cleaned[:max_chars].strip() or text[:max_chars].strip()
    

# -----------------------
# TEXT EXTRACTION
# -----------------------

def extract_text(file_path):
    ext = file_path.lower()

    # ---- PDF ----
    if ext.endswith(".pdf"):
        import pdfplumber
        from PIL import Image
        import pytesseract

        text = ""
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if not page_text:
                        # fallback OCR
                        img = page.to_image(resolution=300).original
                        ocr_text = pytesseract.image_to_string(img)
                        text += ocr_text + "\n"
                    else:
                        text += page_text + "\n"
                except Exception as e:
                    print(f"PDF read error (page {i+1}): {e}")

        if not text.strip():
            return os.path.basename(file_path)

        return clean_and_trim(text)

    # ---- DOCX ----
    elif ext.endswith(".docx"):
        import docx
        try:
            doc = docx.Document(file_path)
            raw = "\n".join([p.text for p in doc.paragraphs])
            return clean_and_trim(raw)
        except:
            return os.path.basename(file_path)

    # ---- TXT ----
    elif ext.endswith(".txt"):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
                return clean_and_trim(raw)
        except:
            return os.path.basename(file_path)

    # ---- Other formats ----
    else:
        return os.path.basename(file_path)

# -----------------------
# CLASSIFIER
# -----------------------
def classify_file(text):
    import re

    # clean text
    text_clean = re.sub(r"\s+", " ", text.strip().lower())

    # gen embeddings
    text_emb = model.encode([text_clean])[0]
    folder_embs = model.encode(FOLDER_DESC)


    sims = np.dot(folder_embs, text_emb) / (
        np.linalg.norm(folder_embs, axis=1) * np.linalg.norm(text_emb)
    )

    keyword_map = {
        "physics": ["physics", "experiment", "newton", "motion", "electric field", "ohm", "lab"],
        "chemistry": ["chemistry", "reaction", "acid", "base", "salt", "titration", "molecule"],
        "informatic practices": ["python", "program", "csv", "database", "pandas", "sql", "ip", "informat"],
        "english": ["essay", "literature", "story", "poem", "writing", "english", "play", "report"],
        "math": ["math", "algebra", "geometry", "calculus", "function", "equation"],
    }

    # boost similarity if keywords found
    boosted = sims.copy()
    for i, label in enumerate(FOLDER_LABELS):
        for kw in keyword_map.get(label.lower(), []):
            if re.search(rf"\b{kw}\b", text_clean):
                boosted[i] += 0.1
                break

    best_idx = int(np.argmax(boosted))
    best_label = FOLDER_LABELS[best_idx]
    best_sim = boosted[best_idx]

    if best_sim >= THRESHOLD:
        return best_label, round(float(best_sim), 2)

    for label, kws in keyword_map.items():
        for kw in kws:
            if re.search(rf"\b{kw}\b", text_clean):
                return label.title(), round(float(best_sim), 2)

    return "Unsorted", round(float(best_sim), 2)




def process_file(file_path):
    start_time = time.time()
    text = extract_text(file_path)
    if not text.strip():
        print(f"No readable text in {os.path.basename(file_path)} — skipping semantic match.")
        text = os.path.basename(file_path)

    predicted_folder, similarity = classify_file(text)

    os.makedirs(BASE_DIR / "sorted" / predicted_folder, exist_ok=True)
    shutil.move(file_path, os.path.join(BASE_DIR / "sorted" / predicted_folder, os.path.basename(file_path)))
    
    time_taken = time.time() - start_time             
    
    print(f"{os.path.basename(file_path)} -> {predicted_folder} (sim={similarity:.2f}) in {time_taken:.2f} seconds")

