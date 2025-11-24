# agent/doctor_engine.py

# ------------------------------
# 19 SPECIALIZATIONS — 19 DOCTORS
# ------------------------------

DOCTOR_DB = [
    {"name": "Dr. Anjali Rao", "speciality": "General Physician", "rating": 4.7, "experience": 8, "hospital": "City Care Clinic"},
    {"name": "Dr. Karan Mehta", "speciality": "Cardiologist", "rating": 4.9, "experience": 12, "hospital": "Metro Heart Institute"},
    {"name": "Dr. Neha Kulkarni", "speciality": "Pulmonologist", "rating": 4.6, "experience": 7, "hospital": "Lifeline Hospital"},
    {"name": "Dr. Ravi Sharma", "speciality": "Gastroenterologist", "rating": 4.5, "experience": 10, "hospital": "Global Gastro Centre"},
    {"name": "Dr. Priya Nair", "speciality": "Dermatologist", "rating": 4.4, "experience": 6, "hospital": "Skin & Glow Clinic"},
    {"name": "Dr. Vivek Iyer", "speciality": "Neurologist", "rating": 4.8, "experience": 11, "hospital": "Brain & Spine Institute"},
    {"name": "Dr. Ramesh Kotian", "speciality": "ENT Specialist", "rating": 4.3, "experience": 13, "hospital": "ENT Care Centre"},
    {"name": "Dr. Meera Chandran", "speciality": "Orthopedic Surgeon", "rating": 4.6, "experience": 9, "hospital": "Bone & Joint Institute"},
    {"name": "Dr. Arvind Joshi", "speciality": "Endocrinologist", "rating": 4.7, "experience": 14, "hospital": "Diabetes & Hormone Clinic"},
    {"name": "Dr. Kavita Suresh", "speciality": "Nephrologist", "rating": 4.8, "experience": 10, "hospital": "Kidney Care Centre"},
    {"name": "Dr. Sneha Arora", "speciality": "Ophthalmologist", "rating": 4.5, "experience": 8, "hospital": "Vision Plus Eye Hospital"},
    {"name": "Dr. Pooja Jain", "speciality": "Psychiatrist", "rating": 4.6, "experience": 7, "hospital": "Mind Wellness Centre"},
    {"name": "Dr. Anitha Raj", "speciality": "Gynecologist", "rating": 4.7, "experience": 12, "hospital": "Womens Care Clinic"},
    {"name": "Dr. Rohit Menon", "speciality": "Pediatrician", "rating": 4.9, "experience": 11, "hospital": "Child Health Hospital"},
    {"name": "Dr. Harsha V", "speciality": "Rheumatologist", "rating": 4.6, "experience": 9, "hospital": "Joint Immuno Centre"},
    {"name": "Dr. Aditya Varma", "speciality": "Hematologist", "rating": 4.8, "experience": 10, "hospital": "Blood & Cancer Institute"},
    {"name": "Dr. Mohan Shetty", "speciality": "Urologist", "rating": 4.5, "experience": 8, "hospital": "UroLife Hospital"},
    {"name": "Dr. Shahid Ali", "speciality": "Oncologist", "rating": 4.7, "experience": 15, "hospital": "Cancer Care Institute"},
    {"name": "Dr. Devika Krishnan", "speciality": "Immunologist", "rating": 4.6, "experience": 6, "hospital": "Allergy & Immunity Centre"},
]

# ---------------------------------------------------
# DISEASE → SPECIALIST MAPPING (19 SPECIALIZATIONS)
# ---------------------------------------------------

DISEASE_TO_SPECIALITY = {
    # Cardiovascular
    "Hypertension (High BP)": ["Cardiologist", "General Physician"],
    "Hypotension (Low BP)": ["General Physician"],
    "Chest Pain": ["Cardiologist"],

    # Respiratory
    "Asthma": ["Pulmonologist"],
    "Breathing Issue": ["Pulmonologist", "General Physician"],

    # Fever / Viral
    "Viral Fever": ["General Physician"],
    "Dengue": ["General Physician"],
    "Malaria": ["General Physician"],
    "COVID": ["Pulmonologist", "General Physician"],

    # Digestive
    "Stomach Infection": ["Gastroenterologist"],
    "Acid Reflux / Gastritis": ["Gastroenterologist"],
    "Food Poisoning": ["Gastroenterologist"],

    # Skin
    "Allergic Reaction": ["Dermatologist"],
    "Skin Rash": ["Dermatologist"],

    # Brain / Nerves
    "Migraine": ["Neurologist"],
    "Severe Headache": ["Neurologist"],

    # ENT
    "Throat Infection": ["ENT Specialist"],
    "Ear Infection": ["ENT Specialist"],

    # Orthopedic
    "Joint Pain": ["Orthopedic Surgeon"],
    "Back Pain": ["Orthopedic Surgeon"],

    # Hormonal
    "Diabetes": ["Endocrinologist"],
    "Thyroid Disorder": ["Endocrinologist"],

    # Kidney
    "UTI": ["Urologist"],
    "Kidney Infection": ["Nephrologist"],

    # Eye
    "Eye Redness": ["Ophthalmologist"],
    "Blurry Vision": ["Ophthalmologist"],

    # Mental Health
    "Anxiety": ["Psychiatrist"],
    "Depression": ["Psychiatrist"],

    # Women's Health
    "Menstrual Pain": ["Gynecologist"],
    "White Discharge": ["Gynecologist"],

    # Children
    "Child Fever": ["Pediatrician"],
    "Pediatric Cold": ["Pediatrician"],

    # Joint/Autoimmune
    "Arthritis": ["Rheumatologist"],
    "Autoimmune Reaction": ["Immunologist"],

    # Blood-related
    "Anemia": ["Hematologist"],
    "Low Hemoglobin": ["Hematologist"],

    # Oncology
    "Suspected Tumor": ["Oncologist"],
}


# ---------------------------------------------------
# SPECIALIST PICKER
# ---------------------------------------------------

def suggest_specialities(diseases_ranked):
    if not diseases_ranked:
        return None, ["General Physician"]

    top = diseases_ranked[0]["disease"]
    specs = DISEASE_TO_SPECIALITY.get(top, ["General Physician"])
    return top, specs


# ---------------------------------------------------
# DOCTOR RANKING ENGINE
# ---------------------------------------------------

def rank_doctors(preferred_specialities, top_n=3):
    scored = []
    for doc in DOCTOR_DB:
        score = doc["rating"] * 2 + doc["experience"] * 0.5
        if doc["speciality"] in preferred_specialities:
            score += 3
        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:top_n]]
