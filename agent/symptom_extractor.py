import re

# SYMPTOMS + SYNONYMS + VARIATIONS
SYMPTOM_MAP = {
    "fever": ["fever", "high temperature", "temperature high"],
    "cough": ["cough", "coughing"],
    "cold": ["cold", "common cold"],
    "headache": ["headache", "head pain"],
    "fatigue": ["fatigue", "tired", "tiredness", "exhausted"],
    "vomiting": ["vomit", "vomiting", "throwing up"],
    "diarrhea": ["diarrhea", "loose motion", "loose motions"],
    "body pain": ["body pain", "body ache"],
    "joint pain": ["joint pain", "joint ache"],
    "dizziness": ["dizzy", "dizziness", "lightheaded"],
    "rash": ["rash", "rashes"],
    "itching": ["itching", "itchy"],
    "sneezing": ["sneeze", "sneezing"],
    "running nose": ["runny nose", "running nose"],
    "abdominal pain": ["abdominal pain", "stomach pain", "belly pain"],
    "constipation": ["constipation"],
    "sweating": ["sweating", "excess sweat"],
    "weakness": ["weakness", "weak"],
    "heartburn": ["heartburn", "acidity", "acid reflux"],
    "chills": ["chills", "shivering"],
    "loss of appetite": ["loss of appetite", "not eating", "no appetite"],

    # HIGH BP variations
    "high bp": [
        "high bp", "bp high", "high blood pressure", "hypertension"
    ],

    # LOW BP variations
    "low bp": [
        "low bp", "bp low", "low blood pressure", "hypotension"
    ],

    # CHEST PAIN variations
    "chest pain": [
        "chest pain", "pain in chest", "chest discomfort"
    ],

    # BREATHLESSNESS variations
    "breathlessness": [
        "breathlessness", "shortness of breath", "difficulty breathing"
    ]
}

def extract_symptoms(user_text):
    text = user_text.lower()
    detected = []

    for symptom, keywords in SYMPTOM_MAP.items():
        for word in keywords:
            if word in text:
                detected.append(symptom)

    return list(set(detected))  # unique symptoms
