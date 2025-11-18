from google import genai
from google.genai.errors import APIError
import json

from dotenv import load_dotenv
import os
load_dotenv()
client = genai.Client(api_key=os.getenv("API_KEY"))

schema = {
    "type": "object",
    "properties": {
        "folder_label": {
            "type": "string",
            "description": "A concise and descriptive folder label, limited to 5 words max inspired from examples."
        },
        "description": {
            "type": "string",
            "description": "A brief but concise and clear explanation of the folder label generated with proper description for the folder so that future files can be easily searched and categorised"
        },
        "keywords": {
            "type": "string",
            "description": "A list of relevant keywords associated with the folder label to help in searching and categorization."
        }
    },
    "required": [
        "folder_label",
        "description",
        "keywords"
    ]
}

examples = """
15 examples of label generation are given below
--- EXAMPLE 1 ---
Document: Abstract: Are you curious about what makes your favorite diet drinks sweet yet calorie-free? Look no further! This project dives deep into the fascinating world of artificial sweeteners, the hidden stars behind the sweetness in Diet Coke, Red Bull Sugarfree, Moster Ultra Black and Sting energy. These sweeteners, Aspartame and Acesulfame Potassium (Ace-K), are designed to provide sweetness without the added sugar, offering a healthier alternative for those who can't resist their fizzy favorites. Artificial sweeteners like Aspartame and Ace-K are unique compounds with distinctive properties. Aspartame is a low-calorie sweetener with a slightly neutral nature, while Ace-K offers stability under heat and acidic conditions. Through this project, we unravel the properties and behaviors of these sweeteners using chemical methods such as paper chromatography, pH testing, solubility testing, and acid-base titration.
output = {"folder_label": "Chemistry", "description": "Practical records, lab reports, and handwritten notes about physical, organic, and inorganic chemistry. Includes titration, molarity, concentration, chemical equations, rate of reaction, qualitative analysis of salts, and experiments with acids, bases, or indicators. Keywords: titration, molarity, acid-base, kinetics, organic, inorganic", "keywords": "titration, molarity, acid-base, kinetics, organic, inorganic"}

--- EXAMPLE 2 ---
Document: This is to certify that Jane Doe has successfully completed the "Project Management Professional (PMP)" certification course offered by the Project Management Institute. The course covered key knowledge areas including scope, time, cost, quality, risk, and stakeholder management. This certificate was awarded on October 28, 2023, and is valid for three years. Certificate ID: 84629PMP.
output = {"folder_label": "Certificates", "description": "Digital and scanned copies of academic, professional, and vocational certificates. Includes course completion certificates, workshop attendance, training programs, and other official recognitions of achievement or qualification from various fields. Keywords: certificate, certification, course, training, award, degree, diploma", "keywords": "certificate, certification, course, training, award, degree"}

--- EXAMPLE 3 ---
Document: UNIVERSITY OF OXFORD, Lecture Transcript: Philosophy 101 - Dr. Alan Finch. Good morning. In today's lecture, we will delve into Plato's Theory of Forms. The central idea is that the physical world is not the 'real' world; instead, ultimate reality exists beyond our physical world in the realm of Forms or Ideas. For every object or quality in the physical world, there is a corresponding perfect Form. For instance, the Form of 'Beauty' is eternal and unchanging, while a beautiful person or a beautiful painting is merely a shadow or imitation of that perfect Form. We will be analyzing excerpts from 'The Republic' to understand this concept better.
output = {"folder_label": "Transcripts", "description": "Written records of spoken language from lectures, interviews, meetings, or speeches. Includes academic transcripts, verbatim notes from seminars, and dictated content for professional or personal use. Focuses on capturing spoken words in a written format for record-keeping, analysis, or accessibility. Keywords: transcript, lecture, interview, meeting notes, speech, dictation", "keywords": "transcript, lecture, interview, meeting notes, speech"}

--- EXAMPLE 4 ---
Document: Invoice #INV-0078. Bill To: Alpha Corp. Date: November 18, 2023. Due Date: December 18, 2023. Description: Q4 Consulting Services - Market Analysis Report. Quantity: 1. Unit Price: $5,000.00. Subtotal: $5,000.00. Tax (10%): $500.00. Total Amount Due: $5,500.00. Please make payment to the bank account listed below. Thank you for your business.
output = {"folder_label": "Finance", "description": "Documents related to financial management, reporting, and analysis. Includes financial statements, balance sheets, income statements, invoices, receipts, expense reports, investment portfolios, bank statements, and tax documents. Keywords: finance, invoice, receipt, budget, investment, stocks, taxes, banking", "keywords": "finance, invoice, receipt, budget, investment, stocks, taxes"}

--- EXAMPLE 5 ---
Document: Essay Prompt: Discuss the theme of ambition in Shakespeare's 'Macbeth'. Your essay should analyze how Macbeth's ambition, spurred by the witches' prophecy and Lady Macbeth's persuasion, leads to his tragic downfall. Use specific quotes and scenes from the play to support your argument. Consider the psychological and moral consequences of unchecked ambition as portrayed by Shakespeare.
output = {"folder_label": "English", "description": "Essays, literary analysis, book reports, and creative writing pieces. Includes analyses of themes, characters, and symbolism in literature, as well as grammar exercises, vocabulary lists, and course notes on literary periods. Focuses on the study and interpretation of language and literature. Keywords: literature, essay, poetry, novel, grammar, analysis, Shakespeare", "keywords": "literature, essay, poetry, novel, grammar, analysis"}

--- EXAMPLE 6 ---
Document: Problem: Solve the following quadratic equation for x: 2x² - 8x - 10 = 0. Solution Steps: 1. Divide the entire equation by 2 to simplify: x² - 4x - 5 = 0. 2. Factor the quadratic expression: (x - 5)(x + 1) = 0. 3. Set each factor to zero to find the possible values for x. x - 5 = 0 leads to x = 5. x + 1 = 0 leads to x = -1. The solutions are x = 5 and x = -1.
output = {"folder_label": "Maths", "description": "Mathematical problem sets, lecture notes, and textbooks. Covers topics such as algebra, calculus, geometry, statistics, and trigonometry. Includes equations, proofs, graphs, step-by-step solutions, and formulas for various mathematical problems. Keywords: calculus, algebra, geometry, statistics, trigonometry, derivatives, integrals, equation", "keywords": "calculus, algebra, geometry, statistics, trigonometry, derivatives, integrals"}

--- EXAMPLE 7 ---
Document: This LEASE AGREEMENT is made and entered into on this 1st day of January, 2024, by and between John Smith (hereinafter referred to as the "Landlord") and Mary Jane (hereinafter referred to as the "Tenant"). The Landlord agrees to lease the residential property located at 123 Main Street, Anytown, USA to the Tenant for a term of one (1) year, commencing on January 15, 2024, and ending on January 14, 2025.
output = {"folder_label": "Legal Documents", "description": "Official and personal legal documents. Includes contracts, agreements, wills, power of attorney forms, deeds, leases, non-disclosure agreements (NDAs), and court filings. These documents establish legal rights, obligations, and agreements between parties. Keywords: legal, contract, agreement, lease, will, affidavit, court", "keywords": "legal, contract, agreement, lease, will, affidavit"}

--- EXAMPLE 8 ---
Document: Patient Name: David Chen. Date of Visit: 11/17/2023. Physician: Dr. Emily Carter. Chief Complaint: Persistent cough and sore throat for one week. Assessment: Acute bronchitis. Plan: Prescribed Amoxicillin 500mg, to be taken twice daily for 7 days. Advised rest and increased fluid intake. Follow-up appointment scheduled in one week if symptoms do not improve.
output = {"folder_label": "Health & Medical", "description": "Personal health records, medical reports, and insurance information. Includes doctor's notes, lab results, prescription details, vaccination records, hospital discharge summaries, and health insurance claims. Keywords: medical, health, doctor, prescription, lab results, insurance, clinic", "keywords": "medical, health, doctor, prescription, lab results, insurance"}

--- EXAMPLE 9 ---
Document: Hello Team, This is a summary of our project sync-up meeting held on November 15, 2023. Attendees: Alice, Bob, Charlie. Agenda: Review Q4 progress for Project Phoenix. Key Points Discussed: 1. The design phase is 90% complete. 2. Development is on track to start next week. 3. Bob raised a concern about potential budget overruns. Action Items: Alice to revise the budget forecast by EOD Friday. Charlie to finalize the UI mockups. Next meeting is scheduled for November 22.
output = {"folder_label": "Meeting Minutes", "description": "Summaries and formal records of proceedings from business, academic, or organizational meetings. Includes a list of attendees, agenda items, key discussion points, decisions made, and assigned action items with deadlines. Keywords: meeting, minutes, agenda, action items, summary, notes", "keywords": "meeting, minutes, agenda, action items, summary"}

--- EXAMPLE 10 ---
Document: Flight Confirmation: H7G9K2. Passenger: Sarah Wilson. Date: December 20, 2023. Departure: New York (JFK) at 8:00 AM, United Airlines Flight UA456. Arrival: Los Angeles (LAX) at 11:30 AM. Hotel Booking: The Grand Hotel, Los Angeles. Check-in: December 20, 2023. Check-out: December 25, 2023. Room Type: King Bed, Non-Smoking. Confirmation #: 998271. Your itinerary is confirmed.
output = {"folder_label": "Travel Itinerary", "description": "Documents related to travel planning and booking. Includes flight confirmations, hotel reservations, car rental agreements, train tickets, cruise details, and trip schedules. Contains key information like booking numbers, dates, times, and locations. Keywords: travel, flight, hotel, booking, itinerary, reservation, ticket", "keywords": "travel, flight, hotel, booking, itinerary, reservation"}

--- EXAMPLE 11 ---
Document: Lasagna al Forno. Ingredients: 1 lb ground beef, 1 jar of marinara sauce, 15 oz ricotta cheese, 1 egg, 1/2 cup grated Parmesan cheese, 1 lb mozzarella cheese (shredded), 1 box of lasagna noodles. Instructions: 1. Preheat oven to 375°F (190°C). 2. In a skillet, brown the ground beef. Drain fat and stir in the marinara sauce. 3. In a bowl, mix ricotta, egg, and Parmesan cheese. 4. Cook noodles according to package directions. 5. Layer sauce, noodles, ricotta mixture, and mozzarella cheese in a baking dish. Repeat layers. 6. Bake for 45 minutes until bubbly.
output = {"folder_label": "Recipes", "description": "Collections of culinary recipes and cooking instructions. Includes lists of ingredients, step-by-step preparation methods, cooking times, and serving suggestions for various dishes, desserts, and beverages. Keywords: recipe, cooking, food, ingredients, baking, kitchen, dish", "keywords": "recipe, cooking, food, ingredients, baking"}

--- EXAMPLE 12 ---
Document: Michael Johnson, (123) 456-7890, michael.j@email.com. Professional Experience: Senior Software Engineer, Tech Solutions Inc., San Francisco, CA (2018 - Present). Led a team of 5 engineers in developing and maintaining a scalable cloud-based SaaS platform using Python, Django, and AWS. Improved application performance by 30% through code optimization and database query refactoring.
output = {"folder_label": "Resume & CV", "description": "Professional and academic resumes or curriculum vitae (CVs). Details an individual's work experience, educational background, skills, qualifications, and accomplishments for the purpose of job applications or professional networking. Keywords: resume, CV, curriculum vitae, career, jobs, experience, skills", "keywords": "resume, CV, career, jobs, experience"}

--- EXAMPLE 13 ---
Document: Washington D.C. – A new report from the Department of Labor released today shows that the national unemployment rate fell to 3.5% in the last quarter, the lowest it has been in two years. The report cites robust job growth in the technology and healthcare sectors as the primary drivers of this positive trend. Economists are optimistic that this signals a strong economic recovery, but caution that inflation remains a key concern for the coming months.
output = {"folder_label": "News Articles", "description": "Clippings, saved web pages, and transcripts of news reports from various sources. Covers current events, politics, business, technology, sports, and culture. Includes articles from newspapers, magazines, and online news outlets. Keywords: news, article, report, journalism, current events, headlines", "keywords": "news, article, report, journalism, current events"}

--- EXAMPLE 14 ---
Document: The Amazon Rainforest, located in South America, is the world's largest tropical rainforest, famed for its immense biodiversity. It spans across nine countries, with the majority contained within Brazil. The Amazon River, the lifeblood of the forest, is the largest river by discharge volume of water in the world. This ecosystem plays a crucial role in regulating the global climate and is home to millions of species of insects, plants, fish, and other forms of life.
output = {"folder_label": "Geography", "description": "Notes, articles, and maps related to the study of Earth's lands, features, inhabitants, and phenomena. Includes descriptions of continents, countries, cities, landforms like mountains and rivers, as well as concepts like climate and population distribution. Keywords: geography, country, city, map, climate, geology, continent", "keywords": "geography, country, city, map, climate, geology"}

--- EXAMPLE 15 ---
Document: Confirmation bias is the tendency of people to favor information that confirms their existing beliefs or hypotheses. This cognitive bias results in individuals selectively gathering and interpreting evidence in a way that supports their preconceptions, while ignoring or devaluing evidence that contradicts them. For example, a person who believes that left-handed people are more creative will tend to notice and remember instances of creative left-handed people more readily than instances of non-creative ones.
output = {"folder_label": "Psychology", "description": "Research papers, lecture notes, and summaries on the study of mind and behavior. Covers topics like cognitive biases, developmental psychology, social behavior, and mental health. Includes theories, case studies, and experimental findings. Keywords: psychology, cognitive, behavior, therapy, mind, social, study", "keywords": "psychology, cognitive, behavior, therapy, mind"}
"""



def generate_folder_label(target_text: str):
    prompt = f"""You are an intelligent file organization system. Your task is to analyze a document and classify it by generating a single, valid JSON object.

    JSON Output Structure:

    Your output must contain these three keys:

    folder_label: A concise, one-or-two-word category that best represents the document's general subject matter (e.g., "Finance", "Chemistry", "Legal Documents").

    description: A 40-60 word paragraph describing the general purpose of a folder with this label. The description must be broad, covering the types of documents and sub-topics one might find in this folder, not just the provided document.

    keywords: A comma-separated string of 6-7 relevant keywords that summarize the folder's category. These keywords must be general to the folder's topic, not specific to the single document.

    Rules:

    Try not to generate folder labels that already exist in folder_labels.json nor similar ones to already existing. If similar folder labels exists in folders_json, use the same label and modify descriptions and keywords accordingly. folders_json will be provided below.
    folders_json: {open("folder_labels.json", "r", encoding="utf-8").read()}

    Try to weight the title if title exists in the text document when generating label and description.
    Your output must be only the JSON object.

    Do not include any text, explanations, or markdown formatting (like ```json) before or after the JSON object.

    The classification must be based on the general category suggested by the document, not limited to the document's specific contents.

    --- EXAMPLES ---
    {examples}

    --- USER DOCUMENT ---
    {target_text}"""
    try:
        res = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config={
                "response_mime_type": "application/json",  
                "response_schema": schema,
                "temperature": 0.8, 
                "system_instruction": "You are an expert document organization system. Your task is to analyze the document text and generate a concise, descriptive and genral folder label that is no more than 3 words. Do not include any explanations or extra text and rely on examples but make appropriate and general folder labels, you can create your own labels do not only choose from examples. And last should be the keywords relevant to the folder label for easy searching and categorization.",
            }
        )

        response = json.loads(res.text)
        folder_label = response.get("folder_label")
        description = response.get("description")
        keywords = response.get("keywords")
        with open("folder_labels.json", "r+", encoding="utf-8") as f:
            folder_data = json.load(f)
            if folder_label not in folder_data:
                folder_data[folder_label] = description + " Keywords: " + keywords
                f.seek(0)
                json.dump(folder_data, f, indent=2)
                f.truncate()
                print(f"Generated new folder label: {folder_label}")
            else:
                print(f"Folder label '{folder_label}' already exists. Skipping addition.")
        
        return response
    except APIError as e:
        print(f"An API error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

