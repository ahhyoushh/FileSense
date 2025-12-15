import os
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import re
import shutil
import json
import time
import threading

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from generate_label import generate_folder_label
from create_index import create_faiss_index, MODEL_NAME
from extract_text import extract_text
import concurrent
from dotenv import load_dotenv
load_dotenv()

# Use the module that uploads to Supabase (you named it rl_supabase)
from scripts.RL.rl_supabase import sync_local_to_supabase, upload_event

print("[rl] RL Supabase uploader loaded.")
def _startup_sync():
    try:
        uploaded, failed = sync_local_to_supabase()
        print(f"[rl] Synced local events to Supabase: {uploaded} uploaded, {failed} failed.")
    except Exception as e:
        print("[rl] startup sync error:", e)

# Run startup sync in background to avoid blocking import/startup
# Run startup sync in background to avoid blocking import/startup
def _bg_startup():
    # sleep briefly to let main thread initialization proceed
    time.sleep(1)
    _startup_sync()

threading.Thread(target=_bg_startup, daemon=True).start()


from scripts.logger.rl_logger import get_rl_logger
from scripts.RL.rl_policy import choose_policy, update_policy
from scripts.RL.rl_config import POLICIES


BASE_DIR = Path(__file__).resolve().parent.parent
FAISS_INDEX_FILE = BASE_DIR / "folder_embeddings.faiss"
LABELS_FILE = BASE_DIR / "folder_labels.json"
THRESHOLD = 0.4
low_confidence_threshold = 0.3
index = None
folder_data = {}
FOLDER_LABELS = []
model = None

# Rlock for thread safety - was fun to debug
CLASSIFICATION_LOCK = threading.RLock()
# Executor for background uploads to avoid spawning unlimited threads
UPLOAD_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=2)


def load_index_and_labels():
    global index, folder_data, FOLDER_LABELS, model
    try:
        if model is None:
            print("[*] Initialising model...")
            model = SentenceTransformer(MODEL_NAME, device="cpu")
            print("[*] Model Loaded.")

        if not FAISS_INDEX_FILE.exists() or not LABELS_FILE.exists():
            print(f"[!] Warning: Index or Labels file missing. Starting with empty knowledge.")
            folder_data = {}
            FOLDER_LABELS = []
            index = None
            return True

        index = faiss.read_index(str(FAISS_INDEX_FILE))
        with open(LABELS_FILE, "r", encoding="utf-8") as f:
            folder_data = json.load(f)
        FOLDER_LABELS = list(folder_data.keys())
        return True
    except Exception as e:
        print(f"[!] An error occurred while loading index or labels: {e}")
        return False


def _ret(label: str, sim: float, retries: int = 0, top3=None, manual: bool = False):
    if top3 is None:
        top3 = [round(float(sim), 4)] if sim is not None else []
    # ensure top3 length exactly 3
    top3 = (top3 + [0.0, 0.0])[:3]
    return label, float(sim if sim is not None else 0.0), int(retries), [float(x) for x in top3], bool(manual)


def classify_file(text, filename, allow_generation=True, retries=0, cfg=None):
    # --- SAFETY NET: MAX RETRIES ---
    MAX_RETRIES = 3

    # If retries exceeded -> non-interactive fallback (try auto-generation, else Uncategorized)
    if retries >= MAX_RETRIES:
        print(f"[!] Max retries reached for '{filename}'. Using non-interactive fallback.")
        # Try to auto-generate a label without user interaction
        # OUTSIDE LOCK: expensive generation
        try:
            new_label_info = generate_folder_label(text)
        except Exception as e:
            print(f"[!] generate_folder_label exception during fallback: {e}")
            new_label_info = None

        if new_label_info and new_label_info.get("folder_label"):
            forced_label = new_label_info.get("folder_label").strip()
            
            # INSIDE LOCK: Metadata updates
            with CLASSIFICATION_LOCK:
                # Persist label to LABELS_FILE if not present
                current_labels = {}
                if LABELS_FILE.exists():
                    try:
                        with open(LABELS_FILE, "r", encoding="utf-8") as f:
                            current_labels = json.load(f)
                    except Exception:
                        current_labels = {}

                if forced_label and forced_label not in current_labels:
                    # try to get a decent description if available
                    description = new_label_info.get("description") or f"{forced_label} Keywords: "
                    current_labels[forced_label] = description
                    try:
                        with open(LABELS_FILE, "w", encoding="utf-8") as f:
                            json.dump(current_labels, f, indent=2)
                    except Exception as e:
                        print(f"[!] Failed to write LABELS_FILE during fallback: {e}")

                # try to rebuild index and reload labels
                try:
                    if create_faiss_index():
                        load_index_and_labels()
                        return _ret(forced_label, 1.0, retries, [1.0, 0.0, 0.0], manual=True)
                except Exception as e:
                    print(f"[!] Failed to create/reload faiss index during fallback: {e}")

        # If auto-generation failed, return Uncategorized non-interactively
        print(f"[!] Fallback auto-generation failed for '{filename}'. Marking as 'Uncategorized'.")
        return _ret("Uncategorized", 0.0, retries, [0.0, 0.0, 0.0], manual=False)

    # ensure index/model loaded
    if model is None:
        load_index_and_labels()
        if model is None:
            return _ret("Uncategorized", 0.0, retries, [0.0, 0.0, 0.0], manual=False)

    # Use cfg overrides if provided
    if cfg is not None:
        current_threshold = cfg.get("THRESHOLD", THRESHOLD)
        current_low_threshold = cfg.get("LOW_CONF", low_confidence_threshold)
        FILENAME_BOOST = cfg.get("FILENAME_BOOST", 0.2)
        TEXT_BOOST = cfg.get("TEXT_BOOST", 0.1)
    else:
        current_threshold = THRESHOLD
        current_low_threshold = low_confidence_threshold
        FILENAME_BOOST = 0.2
        TEXT_BOOST = 0.1

    best_label = "Uncategorized"
    best_sim = 0.0
    top3 = [0.0, 0.0, 0.0]

    if index and FOLDER_LABELS:
        clean_filename = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
        combined_input = f"{clean_filename}\n\n{text}"
        text_clean = re.sub(r"\s+", " ", combined_input.strip().lower())

        text_emb = model.encode([text_clean], normalize_embeddings=True)
        D, I = index.search(text_emb, 10)

        all_sims = np.zeros(len(FOLDER_LABELS), dtype=np.float32)
        for i in range(len(I[0])):
            idx, sim = I[0][i], D[0][i]
            if idx != -1:
                all_sims[idx] = sim

        boosted, filename_lower = all_sims.copy(), filename.lower()

        for i, label in enumerate(FOLDER_LABELS):
            full_text = folder_data.get(label, "")
            keywords_str = ""
            if " Keywords: " in full_text:
                parts = full_text.split(" Keywords: ", 1)
                keywords_str = parts[1]
            keywords = [kw.strip().lower() for kw in keywords_str.split(',') if kw.strip()]

            if re.search(rf"\b{re.escape(label.lower())}\b", filename_lower):
                boosted[i] += FILENAME_BOOST
                continue
            for kw in keywords:
                if re.search(rf"\b{re.escape(kw)}\b", filename_lower):
                    boosted[i] += TEXT_BOOST
                    break

        # compute best and top3
        sorted_idxs = np.argsort(-boosted)  # descending
        best_idx = int(sorted_idxs[0])
        best_label = FOLDER_LABELS[best_idx]
        best_sim = float(boosted[best_idx])
        # top 3 sims
        top_vals = [float(boosted[int(sorted_idxs[i])]) if i < len(sorted_idxs) else 0.0 for i in range(3)]
        top3 = top_vals

    # If high enough confidence, return
    if best_sim >= current_threshold:
        return _ret(best_label, best_sim, retries, top3, manual=False)

    else:
        # determine whether generation is allowed for this cfg
        # CRITICAL FIX: If allow_generation argument corresponds to user flag (False), policy cannot override it.
        # We only apply policy restriction if user allowed it initially.
        policy_allows = cfg.get("ALLOW_GENERATION", True) if cfg else True
        allow_generation_local = allow_generation and policy_allows

        if not allow_generation_local:
            decrease_amount = 0.07
            current_threshold -= decrease_amount
            current_low_threshold -= decrease_amount

            if best_sim > current_low_threshold:
                if retries > 0:
                    print(f"[!] [RETRY SUCCESS] '{filename}' matched '{best_label}' ({best_sim:.2f}) after update.")
                else:
                    print(f"[!] [NO GEN] Low confidence ({best_sim:.2f}) but accepting '{best_label}' as fallback.")
                return _ret(best_label, best_sim, retries, top3, manual=False)
            else:
                return _ret("Uncategorized", 0.0, retries, [0.0, 0.0, 0.0], manual=False)

        if allow_generation_local:
            # first try a no-generation retry using cfg 
            if index:
                retry_label, retry_sim, retry_used, retry_top3, retry_manual = classify_file(
                    text, filename, allow_generation=False, retries=retries + 1, cfg=cfg
                )
                if retry_label != "Uncategorized":
                    return _ret(retry_label, retry_sim, retry_used, retry_top3, retry_manual)

            print(f"[?] Low confidence ({best_sim:.2f}) for '{filename}'. Generating label (Attempt {retries+1})...")
            
            # OUTSIDE LOCK: generation
            try:
                new_label_info = generate_folder_label(text)
            except Exception as e:
                print(f"[!] generate_folder_label exception: {e}")
                new_label_info = None

            if new_label_info and new_label_info.get("folder_label"):
                forced_label = new_label_info.get("folder_label").strip()
                
                # INSIDE LOCK: writes
                with CLASSIFICATION_LOCK:
                    # persist label if missing
                    current_labels = {}
                    if LABELS_FILE.exists():
                        try:
                            with open(LABELS_FILE, "r", encoding="utf-8") as f:
                                current_labels = json.load(f)
                        except Exception:
                            current_labels = {}

                    if forced_label and forced_label not in current_labels:
                        description = new_label_info.get("description") or f"{forced_label} Keywords: "
                        current_labels[forced_label] = description
                        try:
                            with open(LABELS_FILE, "w", encoding="utf-8") as f:
                                json.dump(current_labels, f, indent=2)
                        except Exception as e:
                            print(f"[!] Failed to write LABELS_FILE: {e}")

                    if create_faiss_index():
                        load_index_and_labels()
                        print(f"[1] [ONE-SHOT] Re-checking '{filename}'...")
                        # Recurse (lock is released now, so fine)
                        return classify_file(
                            text, filename, allow_generation=allow_generation, retries=retries + 1, cfg=cfg
                        )

                # If generation failed or produced no good label, fall back to no-generation path (increment retries)
                return classify_file(
                    text, filename, allow_generation=False, retries=retries + 1, cfg=cfg
                )


def process_file(file_path, testing=False, allow_generation=True, sorted_dir=None):
    start_time = time.time()
    filename = os.path.basename(file_path)

    # extract text
    text = extract_text(file_path, fallback=False)

    # choose policy for this file
    policy_id = choose_policy()
    cfg = POLICIES.get(policy_id, None)

    if not text or not text.strip() or text == filename:
        text = filename.replace("_", " ").replace("-", " ")

    # determine allow_generation from cfg or function arg
    # CRITICAL FIX: User preference (allow_generation arg) overrides policy if False.
    policy_allows = cfg.get("ALLOW_GENERATION", True) if cfg else True
    allow_generation_for_call = allow_generation and policy_allows

    # initial classification pass using policy cfg
    predicted_folder, similarity, retries_used, top3, manual_labeled = classify_file(
        text, filename, allow_generation=allow_generation_for_call, cfg=cfg
    )

    # fallback extraction if low confidence on first pass
    if (predicted_folder == "Uncategorized" or (similarity is not None and similarity < 0.35)) and os.path.exists(file_path):
        sim_display = similarity if similarity is not None else 0.0
        print(f"[!] Low confidence ({sim_display:.2f}) on first pass. Attempting Fallback Extraction...")

        fallback_text = extract_text(file_path, fallback=True)

        if fallback_text and len(fallback_text) > 50 and fallback_text != text:
            new_folder, new_sim, new_retries, new_top3, new_manual = classify_file(
                fallback_text, filename, allow_generation=False, cfg=cfg
            )

            # choose improved result if better similarity
            if new_sim > (similarity or 0.0):
                print(f"   -> Fallback improved result: {new_folder} ({new_sim:.2f})")
                text = fallback_text
                predicted_folder = new_folder
                similarity = new_sim
                retries_used = max(retries_used, new_retries)
                top3 = new_top3
                manual_labeled = manual_labeled or new_manual
            else:
                print(f"   -> Fallback did not improve result.")

    # final generation-allowed pass if configured and still low
    effective_threshold = cfg.get("THRESHOLD", THRESHOLD) if cfg else THRESHOLD

    if allow_generation_for_call and (
        predicted_folder == "Uncategorized" or (similarity is not None and similarity < effective_threshold)
    ):
        pf, sim2, r2, t2, m2 = classify_file(
            text, filename, allow_generation=True, cfg=cfg
        )
        # accept new result
        predicted_folder = pf
        similarity = sim2
        retries_used = max(retries_used, r2)
        top3 = t2
        manual_labeled = manual_labeled or m2

    rl_log = get_rl_logger()
    interaction_id = f"{filename}|{int(time.time())}"
    event = {
        "interaction_id": interaction_id,
        "event": "served",
        "timestamp": int(time.time()),
        "file_path": str(file_path),
        "filename": filename,
        "policy_id": policy_id,
        "predicted_label": predicted_folder,
        "similarity_top1": float(similarity) if similarity is not None else None,
        "top3_similarities": [float(x) for x in (top3 if 'top3' in locals() else [0.0, 0.0, 0.0])],
        "manual_labeled": bool(manual_labeled),
        "allowed_generation": bool(cfg.get("ALLOW_GENERATION", True)) if cfg else bool(allow_generation_for_call),
        "retries": int(retries_used),
        "file_ext": Path(filename).suffix.lstrip("."),
        "text_length": len(text) if text else 0,
        "reward": None
    }
    # local write
    rl_log.log_event(event)

    # async upload
    def _bg_upload(ev):
        try:
            ok, err = upload_event(ev)
            if not ok:
                print("[supabase] upload failed:", err)
        except Exception as e:
            print("[supabase] upload exception:", e)

    # async upload using shared executor
    UPLOAD_EXECUTOR.submit(_bg_upload, event)

    # move file to predicted folder
    if sorted_dir:
        destination_folder = Path(sorted_dir) / predicted_folder
    else:
        destination_folder = BASE_DIR / "sorted" / predicted_folder
    os.makedirs(destination_folder, exist_ok=True)

    if not testing:
        try:
            shutil.move(file_path, destination_folder / filename)
        except Exception as e:
            print(f"Error moving file {file_path} -> {predicted_folder}: {e}")

    time_taken = time.time() - start_time
    sim_display = similarity if similarity is not None else 0.0
    print(f"[1] Processed: {filename} -> {predicted_folder} (sim={sim_display:.2f}) in {time_taken:.2f}s")
