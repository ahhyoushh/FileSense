from google import genai
from google.genai.errors import APIError
import json
from dotenv import load_dotenv
import os
from pathlib import Path
import time  # Added for sleep

load_dotenv()
client = genai.Client(api_key=os.getenv("API_KEY"))
MODEL = "gemini-2.5-flash"

# Configuration for Retries
MAX_RETRIES = 3
INITIAL_BACKOFF = 2  # Seconds

schema = {
    "type": "object",
    "properties": {
        "folder_label": {
            "type": "string",
            "description": "A concise, 1-2 word BROAD category label (e.g., Physics, Finance)."
        },
        "description": {
            "type": "string",
            "description": "A dense, comma-separated list of 20-30 synonyms, sub-topics, and related vocabulary."
        },
        "keywords": {
            "type": "string",
            "description": "A comma-separated list of 8-12 broad search keywords."
        }
    },
    "required": [
        "folder_label",
        "description",
        "keywords"
    ]
}

merge_schema = {
    "type": "object",
    "properties": {
        "merged_description": {
            "type": "string",
            "description": "A single, consolidated description containing a dense list of sub-topics and synonyms from both inputs. No conversational filler."
        },
        "merged_keywords": {
            "type": "string",
            "description": "A single, comma-separated string of unique, high-value keywords combining both lists without duplicates."
        }
    },
    "required": ["merged_description", "merged_keywords"]
}

def merge_folder_metadata(folder_label, old_desc, old_kw, new_desc, new_kw):
    """
    Uses LLM to intelligently merge existing folder metadata with new metadata.
    Includes retry logic for API failures.
    """
    prompt = f"""You are an expert semantic data organizer. Your task is to MERGE metadata
for the file category: "{folder_label}".

You have Existing metadata (from the database) and New metadata (from a new file).
Combine them into a unified, comprehensive representation.

--- INPUT DATA ---
Existing Description: {old_desc}
Existing Keywords: {old_kw}

New Description: {new_desc}
New Keywords: {new_kw}

--- HARD CONSTRAINTS (DO NOT VIOLATE) ---
1. You MUST preserve all distinct topics, concepts, and subject areas present in the Existing metadata.
   - You MAY rephrase words (e.g., "stock market" -> "equity markets"), but you MUST NOT drop the concept.
   - If a topic appears in Existing but not in the final merge, that's WRONG.
2. New metadata can ADD extra topics, but cannot REMOVE concepts that were already present.
3. Stay consistent with the broad category "{folder_label}".

--- DESCRIPTION MERGING RULES ---
1. Output `merged_description` as a **dense, comma-separated list** of sub-topics and synonyms.
2. NO sentences like "This folder contains..." or "These are topics about...".
3. Merge unique concepts from Existing + New:
   - remove exact duplicates and near-duplicates,
   - keep related items grouped logically.
4. Aim for 25–40 items (not fewer than 20 unless impossible).

--- KEYWORD MERGING RULES ---
1. Output `merged_keywords` as a **comma-separated list**.
2. Combine Existing + New keywords.
3. Remove duplicates and trivial variants (e.g., "finance" vs "finances" – keep one).
4. Focus on **high-value, broad search terms**.
5. Limit to about 15–20 strong keywords.
"""

    # RETRY LOGIC START
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            res = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": merge_schema,
                    "temperature": 0.2,
                }
            )

            merged = json.loads(res.text)

            # Safety net: if model returns something empty
            if not merged.get("merged_description") or not merged.get("merged_keywords"):
                raise ValueError("Empty merged fields from LLM")

            return merged

        except (APIError, Exception) as e:
            print(f"[!] Warning: Merge API attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                sleep_time = INITIAL_BACKOFF * (2 ** (attempt - 1))
                print(f"    Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                print("[!] All retry attempts failed for merging. Falling back to simple concatenation.")
    
    # Fallback: Simple string concatenation if AI fails after retries
    return {
        "merged_description": f"{old_desc}, {new_desc}",
        "merged_keywords": f"{old_kw}, {new_kw}"
    }


def generate_folder_label(target_text: str, forced_label: str = None):
    LABELS_FILE = Path(__file__).resolve().parent.parent / "folder_labels.json"
    
    # Load existing labels safely
    try:
        if LABELS_FILE.exists():
            with open(LABELS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                existing_labels_content = content if content.strip() else "{}"
        else:
            existing_labels_content = "{}"
    except (OSError, json.JSONDecodeError):
        existing_labels_content = "{}"

    # Prepare Prompt
    if forced_label:
        prompt = f"""You are an expert file organization system.
The user has MANUALLY assigned the label "{forced_label}" to this document.
Your task is to generate a description and keywords for this SPECIFIC label based on the document text.

--- CRITICAL RULE: USE FORCED LABEL ---
*   **OUTPUT LABEL MUST BE:** "{forced_label}"
*   Do NOT change the label.
*   Generate a description and keywords that fit both the document AND the label "{forced_label}".

--- USER DOCUMENT ---
{target_text}
"""
    else:
        prompt = f"""You are an expert file organization system. Analyze the provided document text and generate a classification JSON.

--- CRITICAL RULE 1: BANNED WORDS (NEGATIVE CONSTRAINTS) ---
*   **NEVER** include generic document types in `description` or `keywords`.
*   **BANNED WORDS:** "project", "assignment", "work", "synopsis", "investigatory", "pdf", "file", "document", "class 12", "student", "report", "presentation", "news report", "article", "clipping".
*   **FOCUS ONLY** on the Subject Matter (e.g., "Optics", "Poetry", "Algebra").

--- CRITICAL RULE 2: EXISTING LABELS ---
Below is a list of folders that ALREADY EXIST. 
1. Check if the document fits into one of these existing `folder_labels`.
2. If it fits a BROAD category (e.g., document is "Fluids", label "Physics" exists), YOU MUST USE THE EXISTING LABEL.
3. If it is a DISTINCT FIELD (e.g., document is "Literature", only "Physics" exists), generate a NEW LABEL.
4. PREFER academic labels (Maths, Physics, Chemistry, English, Computer Science, History, Economics, Psychology) over niche labels.

--- CRITICAL RULE 3: BROAD CATEGORIZATION ---
*   **DO NOT** create specific labels like "Fluid Dynamics". Group under "Physics".
*   Distinct subjects (Maths vs Physics vs Chemistry vs English) MUST remain separate.

--- CRITICAL RULE 4: CONTENT OVER FORMAT (NEWS & ARTICLES) ---
*   **IGNORE** the format of the text. If the text looks like a News Article, Blog, or Email, **DO NOT** classify it as "News" or "Email" unless it has no specific topic.
*   **CLASSIFY BY TOPIC:**
    *   Stock market, inflation, corporate earnings -> **Finance** or **Economics**.
    *   New software, AI, gadgets, cyberattacks -> **Computer Science**.
    *   Wars, treaties, diplomacy, elections -> **International Relations** or **Politics** (or **History** if past).
    *   Football match, olympics, scores -> **Sports**.
*   **ONLY** use "News" if the content is general daily events with no dominant domain or specifically about the journalism industry.

EXISTING LABELS: 
{existing_labels_content}

--- USER DOCUMENT ---
{target_text}
"""

    response = None

    # RETRY LOGIC START for Main Generation
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            res = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": schema,
                    "temperature": 0.5,
                }
            )
            response = json.loads(res.text)
            # If successful, break loop
            break
        except APIError as e:
            print(f"[!] Warning: Generation API attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                sleep_time = INITIAL_BACKOFF * (2 ** (attempt - 1))
                print(f"    Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                print(f"[!] Critical Error: Failed to generate label after {MAX_RETRIES} attempts.")
                return False
        except Exception as e:
            print(f"[!] Unexpected error during generation: {e}")
            return False

    # If we reached here without a response, return False
    if not response:
        return False

    # --- Process Successful Response ---
    new_label = response.get("folder_label")
    new_desc = response.get("description")
    new_keywords_str = response.get("keywords")

    try:
        # Now read/merge into folder_labels.json
        with open("folder_labels.json", "r+", encoding="utf-8") as f:
            try:
                folder_data = json.load(f)
            except json.JSONDecodeError:
                folder_data = {}

            if new_label not in folder_data:
                # New label: just store as-is
                folder_data[new_label] = f"{new_desc} Keywords: {new_keywords_str}"
                print(f"Generated new folder label: {new_label}")
            else:
                # Existing label: merge metadata
                print(f"Label '{new_label}' exists. Merging description and keywords via gemini...")

                existing_full_text = folder_data[new_label]

                if " Keywords: " in existing_full_text:
                    existing_desc, existing_kw_str = existing_full_text.split(" Keywords: ", 1)
                else:
                    existing_desc = existing_full_text
                    existing_kw_str = ""

                # This calls the helper function which ALSO has retry logic now
                merged_data = merge_folder_metadata(
                    folder_label=new_label,
                    old_desc=existing_desc,
                    old_kw=existing_kw_str,
                    new_desc=new_desc,
                    new_kw=new_keywords_str
                )

                llm_desc = merged_data.get("merged_description", "") or ""
                llm_kws = merged_data.get("merged_keywords", "") or ""

                def split_terms(s: str):
                    return [t.strip() for t in s.split(",") if t.strip()]

                # --- Description hard-merge (old → LLM → new) ---
                old_desc_terms = split_terms(existing_desc)
                new_desc_terms = split_terms(new_desc)
                llm_desc_terms = split_terms(llm_desc)

                seen_desc = set()
                final_desc_terms = []

                for term_list in (old_desc_terms, llm_desc_terms, new_desc_terms):
                    for term in term_list:
                        key = term.lower()
                        if key not in seen_desc:
                            seen_desc.add(key)
                            final_desc_terms.append(term)

                final_desc = ", ".join(final_desc_terms)

                # --- Keyword hard-merge (old → LLM → new) ---
                old_kw_terms = split_terms(existing_kw_str)
                new_kw_terms = split_terms(new_keywords_str)
                llm_kw_terms = split_terms(llm_kws)

                seen_kw = set()
                final_kw_terms = []

                for term_list in (old_kw_terms, llm_kw_terms, new_kw_terms):
                    for term in term_list:
                        key = term.lower()
                        if key not in seen_kw:
                            seen_kw.add(key)
                            final_kw_terms.append(term)

                final_kws = ", ".join(final_kw_terms)

                folder_data[new_label] = f"{final_desc} Keywords: {final_kws}"

            f.seek(0)
            json.dump(folder_data, f, indent=2)
            f.truncate()

        return response

    except Exception as e:
        print(f"An error occurred while updating JSON: {e}")
        return False