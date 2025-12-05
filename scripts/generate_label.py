from google import genai
from google.genai.errors import APIError
import json
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("API_KEY"))
MODEL = "gemini-2.5-flash"

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

examples = """
--- EXAMPLE 1 (Physics) ---
Document: "EXPERIMENT 4: BERNOULLI'S PRINCIPLE AND FLUID DYNAMICS. Abstract: This experiment investigates the relationship between fluid speed and pressure in a horizontal pipe. According to Bernoulli's equation, P + 1/2pv^2 + pgh = constant. As the cross-sectional area of the pipe decreases, the velocity of the fluid increases..."
Output: {"folder_label": "Physics", "description": "mechanics, fluid dynamics, thermodynamics, electromagnetism, optics, quantum physics, relativity, kinematics, forces, energy, laboratory experiments, scientific formulas", "keywords": "fluids, pressure, flow, laminar, turbulent, reynolds, physics, mechanics, experiment, laboratory"}

--- EXAMPLE 2 (Chemistry) ---
Document: "SYNTHESIS OF ACETYLSALICYLIC ACID (ASPIRIN). Objective: To synthesize aspirin via the esterification of salicylic acid with acetic anhydride using sulfuric acid as a catalyst. Reaction Mechanism: The hydroxyl group on the salicylic acid attacks the carbonyl carbon..."
Output: {"folder_label": "Chemistry", "description": "organic chemistry, inorganic chemistry, physical chemistry, chemical reactions, molecular structure, stoichiometry, titration, lab reports, synthesis, bonding, compounds", "keywords": "synthesis, organic, reaction, purification, acid, chemical, chemistry, lab, aspirin, yield"}

--- EXAMPLE 3 (Maths) ---
Document: "MATH 201: CALCULUS II - MIDTERM EXAM. Problem 1: Evaluate the indefinite integral of f(x) = x^2 * e^x dx using integration by parts. Let u = x^2 and dv = e^x dx. Problem 2: Determine if the series sum(1/n^2) from n=1 to infinity converges..."
Output: {"folder_label": "Maths", "description": "algebra, calculus, geometry, trigonometry, statistics, probability, linear algebra, differential equations, mathematical proofs, theorems, numerical analysis, formulas", "keywords": "calculus, derivative, integral, equation, math, function, algebra, geometry, series, convergence"}

--- EXAMPLE 4 (Finance - Invoice) ---
Document: "INVOICE #INV-2024-001. Issued Date: Oct 15, 2024. Description of Services: 1. Q3 Financial Audit - Comprehensive review of balance sheets. 2. Tax Advisory Services. Subtotal: $4,500.00. VAT (10%): $450.00."
Output: {"folder_label": "Finance", "description": "invoices, receipts, tax documents, bank statements, investment portfolios, budgeting, accounting, audits, financial reports, payroll, expenses, assets, liabilities", "keywords": "invoice, payment, tax, bill, banking, amount, finance, accounting, audit, budget"}

--- EXAMPLE 5 (English/Literature) ---
Document: "ESSAY: THE ILLUSION OF THE AMERICAN DREAM IN THE GREAT GATSBY. F. Scott Fitzgerald's masterpiece serves as a biting critique of the Jazz Age. The protagonist, Jay Gatsby, embodies the relentless pursuit of wealth and status, symbolized by the green light..."
Output: {"folder_label": "English", "description": "essays, book reviews, literary analysis, poetry, creative writing, novel summaries, character studies, themes, metaphors, linguistic analysis, grammar, humanities", "keywords": "essay, analysis, theme, novel, book, symbolism, literature, english, fitzgerald, writing"}

--- EXAMPLE 6 (Computer Science - Code) ---
Document: "PYTHON PROJECT: BINARY SEARCH TREE IMPLEMENTATION. class Node: def __init__(self, key): self.left = None. Time Complexity Analysis: The average case time complexity for search, insert, and delete operations in a BST is O(log n)."
Output: {"folder_label": "Computer Science", "description": "programming, algorithms, data structures, software development, coding, python, java, machine learning, artificial intelligence, database management, cyber security", "keywords": "code, algorithm, python, function, sorting, programming, development, cs, data structures, complexity"}

--- EXAMPLE 7 (Legal) ---
Document: "NON-DISCLOSURE AGREEMENT (NDA). This Agreement is made between 'Disclosing Party' and 'Receiving Party'. 1. Confidential Information: Shall include all data, materials, products, technology..."
Output: {"folder_label": "Legal", "description": "contracts, agreements, non-disclosure agreements, wills, deeds, court documents, litigation, affidavits, intellectual property, regulations, statutes, legal advice", "keywords": "contract, agreement, nda, confidential, parties, legal, law, term, clause, obligation"}

--- EXAMPLE 8 (Medical) ---
Document: "CLINICAL DISCHARGE SUMMARY. Diagnosis: Acute Bacterial Pneumonia. Treatment Course: Started on IV Ceftriaxone. Oxygen saturation improved from 88% to 98%. Discharge Medications: Amoxicillin 500mg PO TID."
Output: {"folder_label": "Medical", "description": "medical reports, prescriptions, lab results, patient records, diagnosis, treatment plans, insurance claims, vaccinations, clinical notes, health summary, doctor visits", "keywords": "patient, diagnosis, prescription, doctor, health, treatment, medical, clinical, hospital, medicine"}

--- EXAMPLE 9 (History) ---
Document: "CHAPTER 5: THE TREATY OF VERSAILLES (1919). The Treaty of Versailles officially ended World War I between the Allied Powers and Germany. Key Provisions: Germany lost 13% of its European territory. War Guilt Clause: Germany was forced to accept full responsibility."
Output: {"folder_label": "History", "description": "historical events, timelines, civilizations, wars, revolutions, biographies, archival documents, primary sources, cultural heritage, anthropology, sociology, treaties", "keywords": "war, treaty, history, event, date, revolution, past, world war, germany, allied"}

--- EXAMPLE 13 (Finance - News Format Content) ---
Document: "BREAKING NEWS: GLOBAL MARKETS RALLY AS INFLATION COOLS. New York - Stock markets surged on Friday following the release of the latest Consumer Price Index (CPI) report. The Dow Jones Industrial Average gained 400 points. Federal Reserve Chairman Jerome Powell hinted that interest rate hikes may be paused."
Output: {"folder_label": "Finance", "description": "market analysis, stock exchange, inflation rates, economic indicators, federal reserve, monetary policy, investment trends, corporate earnings, global economy, consumer price index", "keywords": "stocks, market, inflation, economy, rate, federal reserve, finance, dow jones, cpi, investment"}

--- EXAMPLE 14 (Computer Science - Tech News Format) ---
Document: "TECH DAILY: NVIDIA REVEALS NEW AI CHIP ARCHITECTURE. Silicon Valley - Nvidia today announced its latest Blackwell GPU architecture, promising a 4x increase in training speed for Large Language Models (LLMs). The new chip features 208 billion transistors and aims to revolutionize generative AI data centers."
Output: {"folder_label": "Computer Science", "description": "hardware innovation, artificial intelligence, gpu architecture, semiconductors, machine learning, large language models, tech industry news, computing power, data centers", "keywords": "nvidia, ai, chip, gpu, processor, tech, computer, hardware, llm, technology"}

--- EXAMPLE 15 (International Relations - Politics News Format) ---
Document: "WORLD NEWS: DIPLOMATS GATHER FOR CLIMATE SUMMIT IN PARIS. Delegates from 190 nations arrived today to discuss the new carbon emission protocols. The geopolitical tensions between major industrial powers threatened to stall negotiations, but a last-minute draft treaty suggests a compromise on renewable energy funding."
Output: {"folder_label": "International Relations", "description": "diplomacy, geopolitics, treaties, summits, united nations, foreign policy, international law, climate accords, global politics, state negotiations", "keywords": "diplomacy, summit, treaty, nations, global, politics, negotiation, paris, international, policy"}
"""


def merge_folder_metadata(folder_label, old_desc, old_kw, new_desc, new_kw):
    """
    Uses LLM to intelligently merge existing folder metadata with new metadata.

    Hard requirement: NO important topic from old_desc/old_kw is lost.
    The model can rephrase but should not drop them.
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

        # Safety net: if model returns something empty, fall back to simple concat
        if not merged.get("merged_description") or not merged.get("merged_keywords"):
            raise ValueError("Empty merged fields from LLM")

        return merged

    except Exception as e:
        print(f"[!] Error merging metadata: {e}")
        # Fallback: Simple string concatenation if AI fails
        return {
            "merged_description": f"{old_desc}, {new_desc}",
            "merged_keywords": f"{old_kw}, {new_kw}"
        }


def generate_folder_label(target_text: str, forced_label: str = None):
    try:
        try:
            with open("folder_labels.json", "r", encoding="utf-8") as f:
                existing_labels_content = f.read()
                if not existing_labels_content.strip():
                    existing_labels_content = "{}"
        except (FileNotFoundError, json.JSONDecodeError):
            existing_labels_content = "{}"

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
        new_label = response.get("folder_label")
        new_desc = response.get("description")
        new_keywords_str = response.get("keywords")

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

                # Optional cap:
                # final_desc_terms = final_desc_terms[:40]
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

                # Optional cap:
                # final_kw_terms = final_kw_terms[:20]
                final_kws = ", ".join(final_kw_terms)

                folder_data[new_label] = f"{final_desc} Keywords: {final_kws}"

            f.seek(0)
            json.dump(folder_data, f, indent=2)
            f.truncate()

        return response

    except APIError as e:
        print(f"An API error occurred: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
