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

def merge_folder_metadata(folder_label, old_desc, old_kw, new_desc, new_kw):
    """
    Uses LLM to intelligently merge existing folder metadata with new metadata.
    """
    prompt = f"""You are an expert semantic data organizer. Your task is to merge metadata for the file category: "{folder_label}".

    You have Existing metadata (from the database) and New metadata (from a new file).
    Combine them into a unified, comprehensive representation.

    --- INPUT DATA ---
    Existing Description: {old_desc}
    Existing Keywords: {old_kw}

    New Description: {new_desc}
    New Keywords: {new_kw}

    --- RULES ---
    1. **Description Merging:** 
       - The output description must be a **dense list of sub-topics and synonyms** (Bag-of-Words style).
       - **DO NOT** use sentences like "This folder contains...".
       - Combine unique concepts from both descriptions.
       - Remove duplicates and overlapping terms.
    
    2. **Keyword Merging:**
       - Combine both keyword lists.
       - Remove exact duplicates and near-duplicates (e.g., "finance" and "finances").
       - Keep the list comma-separated.
       - Limit to the top 15-20 most relevant terms.

    3. **Consistency:** Ensure the final output strongly relates to the main Category Label: "{folder_label}".
    """

    try:
        res = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": merge_schema,
                "temperature": 0.3, # Low temp for consistent merging
            }
        )
        
        return json.loads(res.text)

    except Exception as e:
        print(f"[!] Error merging metadata: {e}")
        # Fallback: Simple string concatenation if AI fails
        return {
            "merged_description": f"{old_desc}, {new_desc}",
            "merged_keywords": f"{old_kw}, {new_kw}"
        }
examples = """
--- EXAMPLE 1 (Physics) ---
Document: "EXPERIMENT 4: BERNOULLI'S PRINCIPLE AND FLUID DYNAMICS. Abstract: This experiment investigates the relationship between fluid speed and pressure in a horizontal pipe. According to Bernoulli's equation, P + 1/2pv^2 + pgh = constant. As the cross-sectional area of the pipe decreases, the velocity of the fluid increases, leading to a corresponding drop in static pressure. We utilized a Venturi meter to measure these pressure differentials. Data Analysis: The flow rate Q was maintained at 5.0 L/min. At Section A (diameter 5cm), velocity was 0.4 m/s. At Section B (diameter 2cm), velocity increased to 2.5 m/s. The manometer readings confirmed a pressure drop of 150 Pa. We also calculated the Reynolds number (Re = pvd/u) to characterize the flow regime. With Re > 4000, the flow was determined to be turbulent. Error analysis suggests minor friction losses were neglected. Conclusion: The experiment successfully verified the inverse relationship between velocity and pressure in fluid dynamics."
Output: {"folder_label": "Physics", "description": "mechanics, fluid dynamics, thermodynamics, electromagnetism, optics, quantum physics, relativity, kinematics, forces, energy, laboratory experiments, scientific formulas, Newton's laws, wave theory, hydrodynamics, pressure, velocity, viscosity, turbulence, aerodynamics, engineering physics", "keywords": "fluids, pressure, flow, laminar, turbulent, reynolds, physics, mechanics, experiment, laboratory"}

--- EXAMPLE 2 (Chemistry) ---
Document: "SYNTHESIS OF ACETYLSALICYLIC ACID (ASPIRIN). Objective: To synthesize aspirin via the esterification of salicylic acid with acetic anhydride using sulfuric acid as a catalyst. Reaction Mechanism: The hydroxyl group on the salicylic acid attacks the carbonyl carbon of the acetic anhydride. Procedure: 3.0g of salicylic acid was mixed with 6mL of acetic anhydride. 5 drops of H2SO4 were added. The mixture was heated in a water bath at 50°C for 15 minutes. Upon cooling, crystals began to form. Recrystallization: The crude product was dissolved in minimal hot ethanol and cooled slowly to purify the crystals. Characterization: The melting point of the purified product was found to be 135°C (Lit: 136°C). Ferric chloride test was negative, indicating no unreacted salicylic acid. Yield Calculation: Theoretical yield = 3.9g. Actual yield = 2.8g. Percent yield = 71.8%."
Output: {"folder_label": "Chemistry", "description": "organic chemistry, inorganic chemistry, physical chemistry, chemical reactions, molecular structure, stoichiometry, titration, lab reports, synthesis, bonding, compounds, periodic table, acids, bases, polymers, biochemistry, analytical chemistry, spectroscopy, elements, solutions", "keywords": "synthesis, organic, reaction, purification, acid, chemical, chemistry, lab, aspirin, yield"}

--- EXAMPLE 3 (Maths) ---
Document: "MATH 201: CALCULUS II - MIDTERM EXAM. Problem 1: Evaluate the indefinite integral of f(x) = x^2 * e^x dx using integration by parts. Let u = x^2 and dv = e^x dx. Problem 2: Determine if the series sum(1/n^2) from n=1 to infinity converges using the p-series test. Since p=2 > 1, the series converges. Problem 3: Find the volume of the solid generated by rotating the region bounded by y = x^2 and y = 4 about the x-axis using the washer method. V = pi * integral((4)^2 - (x^2)^2) dx. Problem 4: Solve the differential equation dy/dx + 2y = 4. This is a linear first-order ODE. The integrating factor is e^(2x). Multiplying through, we get d/dx(y*e^2x) = 4e^2x. Integrating both sides yields y = 2 + Ce^(-2x)."
Output: {"folder_label": "Maths", "description": "algebra, calculus, geometry, trigonometry, statistics, probability, linear algebra, differential equations, mathematical proofs, theorems, numerical analysis, formulas, derivatives, integrals, limits, functions, vectors, matrices, logic, topology", "keywords": "calculus, derivative, integral, equation, math, function, algebra, geometry, series, convergence"}

--- EXAMPLE 4 (Finance) ---
Document: "INVOICE #INV-2024-001. Issued Date: Oct 15, 2024. Due Date: Nov 15, 2024. Bill To: Global Tech Solutions. From: Alpha Consulting LLC. Description of Services: 1. Q3 Financial Audit - Comprehensive review of balance sheets, income statements, and cash flow reports ($2,500.00). 2. Tax Advisory Services - Consultation regarding corporate tax liabilities and deductions ($1,200.00). 3. Payroll Processing - September 2024 ($800.00). Subtotal: $4,500.00. VAT (10%): $450.00. Total Amount Due: $4,950.00. Payment Methods: Bank Transfer (Account: 123-456-789), Credit Card, or Check. Late fees of 5% apply after 30 days. Thank you for your business."
Output: {"folder_label": "Finance", "description": "invoices, receipts, tax documents, bank statements, investment portfolios, budgeting, accounting, audits, financial reports, payroll, expenses, assets, liabilities, billing, economics, markets, stocks, bonds, insurance, bookkeeping", "keywords": "invoice, payment, tax, bill, banking, amount, finance, accounting, audit, budget"}

--- EXAMPLE 5 (English/Literature) ---
Document: "ESSAY: THE ILLUSION OF THE AMERICAN DREAM IN THE GREAT GATSBY. F. Scott Fitzgerald's masterpiece, 'The Great Gatsby', serves as a biting critique of the Jazz Age. The protagonist, Jay Gatsby, embodies the relentless pursuit of wealth and status, symbolized by the green light at the end of Daisy's dock. However, Fitzgerald suggests that this dream is ultimately hollow. The valley of ashes represents the moral decay hidden behind the glittering facade of West Egg. Tom and Daisy Buchanan, careless people who smash up things and creatures, illustrate the corruption of the old money elite. In the end, Gatsby's death reflects the futility of trying to repeat the past. The novel employs rich symbolism, such as the eyes of Dr. T.J. Eckleburg, to convey themes of judgment and loss of spirituality."
Output: {"folder_label": "English", "description": "essays, book reviews, literary analysis, poetry, creative writing, novel summaries, character studies, themes, metaphors, linguistic analysis, grammar, humanities, authors, symbolism, prose, drama, fiction, non-fiction, storytelling, reading comprehension", "keywords": "essay, analysis, theme, novel, book, symbolism, literature, english, fitzgerald, writing"}

--- EXAMPLE 6 (Computer Science) ---
Document: "PYTHON PROJECT: BINARY SEARCH TREE IMPLEMENTATION. class Node: def __init__(self, key): self.left = None, self.right = None, self.val = key. def insert(root, key): if root is None: return Node(key). else: if root.val < key: root.right = insert(root.right, key) else: root.left = insert(root.left, key) return root. Time Complexity Analysis: The average case time complexity for search, insert, and delete operations in a BST is O(log n). However, in the worst case (skewed tree), it degrades to O(n). To optimize this, AVL trees or Red-Black trees can be used to ensure balancing. This module also includes a BFS (Breadth-First Search) traversal method using a queue."
Output: {"folder_label": "Computer Science", "description": "programming, algorithms, data structures, software development, coding, python, java, machine learning, artificial intelligence, database management, cyber security, networking, web development, code, scripting, backend, frontend, api, logic, debugging", "keywords": "code, algorithm, python, function, sorting, programming, development, cs, data structures, complexity"}

--- EXAMPLE 7 (Legal) ---
Document: "NON-DISCLOSURE AGREEMENT (NDA). This Agreement is made between 'Disclosing Party' and 'Receiving Party'. 1. Confidential Information: Shall include all data, materials, products, technology, computer programs, specifications, manuals, business plans, software, marketing plans, business opportunities, financial information, and other information disclosed or submitted, orally, in writing, or by any other media. 2. Obligations: The Receiving Party agrees to hold and maintain the Confidential Information in strictest confidence for the sole and exclusive benefit of the Disclosing Party. 3. Term: This agreement shall remain in effect for a period of 5 years. 4. Governing Law: This Agreement shall be governed by and construed in accordance with the laws of the State of California."
Output: {"folder_label": "Legal", "description": "contracts, agreements, non-disclosure agreements, wills, deeds, court documents, litigation, affidavits, intellectual property, regulations, statutes, legal advice, arbitration, clauses, patents, trademarks, copyrights, terms of service, privacy policy, corporate law", "keywords": "contract, agreement, nda, confidential, parties, legal, law, term, clause, obligation"}

--- EXAMPLE 8 (Medical) ---
Document: "CLINICAL DISCHARGE SUMMARY. Patient: John Doe (DOB: 01/01/1980). Admitted: 11/10/2023. Discharged: 11/14/2023. Diagnosis: Acute Bacterial Pneumonia. History of Present Illness: Patient presented with high fever (39°C), productive cough with rust-colored sputum, and dyspnea. Chest X-ray revealed consolidation in the right lower lobe. Lab results showed elevated WBC count (15,000/uL). Treatment Course: Started on IV Ceftriaxone and Azithromycin. Oxygen saturation improved from 88% to 98% on room air by Day 3. Fever resolved. Discharge Medications: Amoxicillin 500mg PO TID for 5 days. Follow-up: Patient to see PCP in 1 week. Instructions: Encourage fluid intake, rest, and complete full course of antibiotics."
Output: {"folder_label": "Medical", "description": "medical reports, prescriptions, lab results, patient records, diagnosis, treatment plans, insurance claims, vaccinations, clinical notes, health summary, doctor visits, pathology, symptoms, anatomy, physiology, surgery, nursing, pharmacology, diseases, healthcare", "keywords": "patient, diagnosis, prescription, doctor, health, treatment, medical, clinical, hospital, medicine"}

--- EXAMPLE 9 (History) ---
Document: "CHAPTER 5: THE TREATY OF VERSAILLES (1919). The Treaty of Versailles officially ended World War I between the Allied Powers and Germany. Signed in the Hall of Mirrors, the treaty imposed harsh penalties on Germany, often cited as a cause for the rise of Nazism and WWII. Key Provisions: 1. Territorial Losses: Germany lost 13% of its European territory, including Alsace-Lorraine (returned to France) and the Polish Corridor. 2. Military Restrictions: The German army was limited to 100,000 men, and conscription was banned. The Rhineland was demilitarized. 3. War Guilt Clause (Article 231): Germany was forced to accept full responsibility for causing the war. 4. Reparations: Germany was required to pay 132 billion gold marks. The treaty created the League of Nations to prevent future conflicts."
Output: {"folder_label": "History", "description": "historical events, timelines, civilizations, wars, revolutions, biographies, archival documents, primary sources, cultural heritage, anthropology, sociology, treaties, eras, past events, archaeology, politics, geography, monarchs, empires, ancient history", "keywords": "war, treaty, history, event, date, revolution, past, world war, germany, allied"}

--- EXAMPLE 10 (Travel) ---
Document: "TRAVEL ITINERARY: EUROPEAN VACATION. Booking Reference: XJ9-22L. Passenger: Sarah Smith. Flight 1: Delta DL106 - JFK (New York) to LHR (London). Departs: June 10, 18:30. Arrives: June 11, 06:45. Seat: 12A. Hotel 1: The Savoy, London (3 Nights). Check-in: June 11. Check-out: June 14. Train: Eurostar 9024 - London St Pancras to Paris Nord. Departs: June 14, 10:00. Hotel 2: Hotel Ritz, Paris (4 Nights). Flight 2: Air France AF022 - CDG (Paris) to JFK (New York). Departs: June 18, 14:00. Notes: Visa requirements checked. Travel insurance policy #998877 active. Carry-on allowance: 1 bag + 1 personal item."
Output: {"folder_label": "Travel", "description": "itinerary, flight tickets, boarding passes, hotel reservations, visa documents, passport copies, car rental, travel insurance, booking confirmations, vacation planning, tourism, transport, maps, guides, luggage, airlines, accommodation, trips, holidays, exploration", "keywords": "flight, hotel, booking, itinerary, travel, reservation, trip, ticket, tourism, vacation"}

--- EXAMPLE 11 (Recipes/Food) ---
Document: "RECIPE: CLASSIC ITALIAN LASAGNA. Prep time: 30 mins. Cook time: 1 hr. Ingredients: 1 lb ground beef, 1 jar marinara sauce, 1 box lasagna noodles, 15 oz ricotta cheese, 1 egg, 2 cups mozzarella cheese, 1/2 cup parmesan. Instructions: 1. Preheat oven to 375°F (190°C). 2. Boil noodles in salted water until al dente. Drain. 3. In a skillet, brown the beef and season with salt, pepper, and oregano. Add marinara sauce and simmer. 4. In a separate bowl, whisk the egg and mix with ricotta and parmesan. 5. Assemble: Spread sauce on the bottom of a 9x13 dish. Layer noodles, ricotta mixture, meat sauce, and mozzarella. Repeat layers. 6. Cover with foil and bake for 45 minutes. Remove foil and bake 10 more minutes until cheese is bubbly. Let rest before serving."
Output: {"folder_label": "Food", "description": "recipes, ingredients, cooking instructions, meal planning, dietary information, nutrition facts, baking, culinary techniques, grocery lists, menu, dishes, cuisine, gastronomy, restaurant reviews, food science, beverages, desserts, chef, kitchen, dining", "keywords": "recipe, cooking, bake, ingredients, food, kitchen, meal, dish, culinary, lasagna"}

--- EXAMPLE 12 (Career/Resume) ---
Document: "RESUME: JANE DOE. Contact: jane.doe@email.com | 555-0199. Professional Summary: Results-oriented Marketing Manager with 7+ years of experience driving brand growth and digital strategy. Proven track record in SEO, content marketing, and social media campaigns. Experience: Senior Marketing Specialist at TechGrowth Inc (2019-Present). - Led a team of 5 to execute a rebranding campaign that increased web traffic by 40%. - Managed a $50k monthly ad budget across Google and LinkedIn. Marketing Coordinator at Creative Solutions (2016-2019). - Designed email newsletters with a 25% open rate. Education: BA in Marketing, University of California, Berkeley. Skills: Google Analytics, HubSpot, Adobe Creative Suite, Copywriting, Leadership."
Output: {"folder_label": "Career", "description": "resume, cv, curriculum vitae, cover letter, job application, portfolio, reference letters, interview notes, offer letters, employment contracts, professional development, skills, hiring, recruitment, networking, linkedin, qualifications, experience, internships, career planning", "keywords": "resume, experience, skills, job, education, cv, career, employment, application, work"}

--- EXAMPLE 13 (News/Journalism) ---
Document: "BREAKING NEWS: GLOBAL MARKETS RALLY AS INFLATION COOLS. New York - Stock markets surged on Friday following the release of the latest Consumer Price Index (CPI) report, which showed inflation slowing to 3.2% year-over-year. The Dow Jones Industrial Average gained 400 points, while the S&P 500 reached a new record high. Tech stocks led the rally, with major gains in the semiconductor sector. Federal Reserve Chairman Jerome Powell hinted that interest rate hikes may be paused in the coming quarter if the trend continues. 'This is a promising sign for the economy,' said chief economist Maria Gonzalez. However, experts warn that geopolitical tensions in the Middle East could still impact oil prices."
Output: {"folder_label": "News", "description": "news articles, clippings, press releases, journalism, headlines, current events, reports, editorials, op-eds, broadcasts, media, politics, economy, world affairs, local news, updates, bulletins, interviews, commentary, information", "keywords": "news, article, report, journalism, current events, market, economy, headline, update, media"}

--- EXAMPLE 14 (Geography) ---
Document: "GEOGRAPHY 101: THE AMAZON RAINFOREST ECOSYSTEM. The Amazon Biome spans 6.7 million km^2, covering nine nations. It represents over half of the planet's remaining rainforests and comprises the largest and most biodiverse tract of tropical rainforest in the world. Climate: The region experiences a tropical rainforest climate, with high humidity and heavy rainfall averaging 2000-3000 mm annually. Hydrography: The Amazon River is the lifeblood of the forest, discharging more water than the next seven largest rivers combined. Flora and Fauna: Home to 10% of the known species on Earth, including the jaguar, sloth, macaw, and pink river dolphin. Deforestation remains a critical threat, driven by logging, cattle ranching, and agriculture."
Output: {"folder_label": "Geography", "description": "maps, atlas, climate, topography, ecosystems, countries, capitals, continents, demographics, population, geology, landforms, rivers, mountains, environmental science, cartography, earth science, regions, urban planning, meteorology", "keywords": "geography, map, earth, climate, location, region, land, environment, river, country"}

--- EXAMPLE 15 (Psychology) ---
Document: "ABSTRACT: COGNITIVE DISSONANCE AND DECISION MAKING. This study explores the theory of cognitive dissonance, proposed by Leon Festinger, which suggests that individuals experience psychological discomfort when holding conflicting beliefs or behaviors. We conducted a controlled experiment with 100 participants who were asked to perform a boring task. Half were paid $1, and the other half $20, to lie to the next participant that the task was fun. Results showed that the $1 group rated the task as significantly more enjoyable than the $20 group. This supports the hypothesis of 'insufficient justification', where individuals alter their internal attitudes to align with their actions to reduce dissonance. Implications for consumer behavior and persuasion are discussed."
Output: {"folder_label": "Psychology", "description": "research papers, case studies, cognitive science, behavior, mental health, therapy, neuroscience, counseling, development, social psychology, experiments, theories, freud, jung, personality, disorders, treatment, mind, emotions, perception", "keywords": "psychology, mind, behavior, research, study, cognitive, therapy, mental, emotion, theory"}
"""

def generate_folder_label(target_text: str):
    try:
        with open("folder_labels.json", "r", encoding="utf-8") as f:
            existing_labels_content = f.read()
            if not existing_labels_content.strip():
                existing_labels_content = "{}"
    except (FileNotFoundError, json.JSONDecodeError):
        existing_labels_content = "{}"

    prompt = f"""You are an expert file organization system. Analyze the provided document text and generate a classification JSON.

    --- CRITICAL RULE 1: BANNED WORDS (NEGATIVE CONSTRAINTS) ---
    *   **NEVER** include generic document types in `description` or `keywords`.
    *   **BANNED WORDS:** "project", "assignment", "work", "synopsis", "investigatory", "pdf", "file", "document", "class 12", "student", "report", "presentation".
    *   **FOCUS ONLY** on the Subject Matter (e.g., "Optics", "Poetry", "Algebra").
    *   *Reasoning:* If you include "project" in Physics, an English Project will get misclassified as Physics.

    --- CRITICAL RULE 2: EXISTING LABELS ---
    Below is a list of folders that ALREADY EXIST. 
    1. Check if the document fits into one of these existing `folder_labels`.
    2. If it fits a BROAD category (e.g., document is "Fluids", label "Physics" exists), YOU MUST USE THE EXISTING LABEL.
    3. If it is a DISTINCT FIELD (e.g., document is "Literature", only "Physics" exists), generate a NEW LABEL.
    4. If you are able to classify under an academic label (Maths, Physics, Chemistry, English, Computer Science, History, Geography, Psychology), PREFER THAT rather than stories, time travel or more specific label.
    --- CRITICAL RULE 3: BROAD CATEGORIZATION ---
    *   **DO NOT** create specific labels like "Fluid Dynamics". Group under "Physics".
    *   Distinct subjects (Maths vs Physics vs Chemistry vs English) MUST remain separate.

    EXISTING LABELS: 
    {existing_labels_content}

    --- USER DOCUMENT ---
    {target_text}
    """

    try:
        res = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={
                "response_mime_type": "application/json",  
                "response_schema": schema,
                "temperature": 0.5, # Low temperature to enforce strict adherence to existing labels
            }
        )

        response = json.loads(res.text)
        new_label = response.get("folder_label")
        new_desc = response.get("description")
        new_keywords_str = response.get("keywords")
        
        with open("folder_labels.json", "r+", encoding="utf-8") as f:
            try:
                folder_data = json.load(f)
            except json.JSONDecodeError:
                folder_data = {}
            
            if new_label not in folder_data:
                folder_data[new_label] = f"{new_desc} Keywords: {new_keywords_str}"
                print(f"Generated new folder label: {new_label}")
            else:
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

                final_desc = merged_data.get("merged_description", existing_desc)
                final_kws = merged_data.get("merged_keywords", existing_kw_str)

                folder_data[new_label] = f"{final_desc} Keywords: {final_kws}"
                # if " Keywords: " in existing_full_text:
                #     existing_desc, existing_kw_str = existing_full_text.split(" Keywords: ", 1)
                # else:
                #     existing_desc = existing_full_text
                #     existing_kw_str = ""

                # # Merge Keywords (Set to remove duplicates)
                # old_kws = set([k.strip().lower() for k in existing_kw_str.split(',') if k.strip()])
                # incoming_kws = [k.strip().lower() for k in new_keywords_str.split(',') if k.strip()]
                # old_kws.update(incoming_kws)
                
                # # Merge Description Terms (Set to remove duplicates)
                # old_desc_terms = set([d.strip().lower() for d in existing_desc.split(',') if d.strip()])
                # incoming_desc_terms = [d.strip().lower() for d in new_desc.split(',') if d.strip()]
                # old_desc_terms.update(incoming_desc_terms)

                # merged_kw_str = ", ".join(sorted(list(old_kws))) 
                # merged_desc_str = ", ".join(sorted(list(old_desc_terms)))

                # folder_data[new_label] = f"{merged_desc_str} Keywords: {merged_kw_str}"

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