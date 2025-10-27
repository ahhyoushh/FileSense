import os, shutil, json, faiss
from sentence_transformers import SentenceTransformer
import numpy as np
from create_index import FAISS_INDEX_FILE, LABELS_FILE, MODEL_NAME

# -----------------------
# CONFIG
# -----------------------
files_dir = "files"
THRESHOLD = 0.45  # similarity threshold 

# load faiss index 
index = faiss.read_index(FAISS_INDEX_FILE)
with open(LABELS_FILE, "r", encoding="utf-8") as f:
    folder_data = json.load(f)

FOLDER_LABELS = list(folder_data.keys())
FOLDER_DESC = list(folder_data.values())

# load model
model = SentenceTransformer(MODEL_NAME, device="cpu")


# -----------------------
# TEXT EXTRACTION
# -----------------------
# OCR
def extract_text(file_path):
    if file_path.lower().endswith(".pdf"):
        import pdfplumber
        from PIL import Image
        import pytesseract
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if not page_text:
                        # try OCR if pdf is just scanned image
                        try:
                            img = page.to_image(resolution=300).original
                            ocr_text = pytesseract.image_to_string(img)
                            text += ocr_text + "\n"
                        except Exception as e:
                            print(f"OCR failed on page {i+1} of {os.path.basename(file_path)} — {e}")
                    else:
                        text += page_text + "\n"
            if not text.strip():
                print(f"No readable text in {os.path.basename(file_path)} (even after OCR)")
                return os.path.basename(file_path)
            return text.strip()
        except Exception as e:
            print(f"Failed to process PDF {os.path.basename(file_path)} — {e}")
            return os.path.basename(file_path)

    elif file_path.lower().endswith(".docx"):
        import docx
        try:
            doc = docx.Document(file_path)
            return " ".join([p.text for p in doc.paragraphs])
        except Exception as e:
            print(f"Failed to read DOCX {os.path.basename(file_path)} — {e}")
            return os.path.basename(file_path)

    elif file_path.lower().endswith(".txt"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Failed to read TXT {os.path.basename(file_path)} — {e}")
            return os.path.basename(file_path)

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
    text = extract_text(file_path)
    if not text.strip():
        print(f"No readable text in {os.path.basename(file_path)} — skipping semantic match.")
        text = os.path.basename(file_path)

    predicted_folder, similarity = classify_file(text)

    os.makedirs(predicted_folder, exist_ok=True)
    shutil.move(file_path, os.path.join(predicted_folder, os.path.basename(file_path)))

    print(f"{os.path.basename(file_path)} -> {predicted_folder} (sim={similarity:.2f})")



files = [os.path.join(files_dir, f) for f in os.listdir(files_dir) if os.path.isfile(os.path.join(files_dir, f))]
for file_path in files:
    process_file(file_path)
