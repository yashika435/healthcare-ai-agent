# agent/disease_engine.py

# ------------------------------
# DISEASE KNOWLEDGE BASE (Step 3)
# ------------------------------
DISEASE_KB = {
    "Viral Fever": ["fever", "headache", "body pain", "fatigue", "chills"],
    "Dengue": ["fever", "severe body pain", "vomiting", "headache", "fatigue", "rash"],
    "Malaria": ["fever", "chills", "headache", "sweating", "body pain"],
    "COVID": ["fever", "dry cough", "breathlessness", "fatigue", "loss of appetite"],
    "Food Poisoning": ["vomiting", "diarrhea", "abdominal pain", "fever"],
    "Acidity / GERD": ["heartburn", "chest pain", "vomiting"],
    "Hypertension (High BP)": ["high bp", "headache", "dizziness"],  
    "Hypotension (Low BP)": ["low bp", "weakness", "dizziness"],
    "Common Cold": ["cold", "sneezing", "running nose", "headache"],
    "Asthma": ["breathlessness", "chest tightness", "dry cough"],
}

# Symptom → Explanation (for education)
SYMPTOM_EXPLANATION = {
    "fever": "Often indicates infection or viral illness.",
    "high bp": "Indicates hypertension. Monitor immediately.",
    "low bp": "May indicate dehydration or weakness.",
    "vomiting": "Common in gastritis or food poisoning.",
    "diarrhea": "Often caused by infection.",
    "headache": "Stress, migraine, or fever may cause this.",
    "body pain": "Common with viral fever or fatigue.",
    "fatigue": "Can indicate infection or anemia.",
    "breathlessness": "Could indicate asthma or heart issue.",
    "chest pain": "Serious — check immediately if severe.",
}

# ----------------------------------------------------------------------
# MATCHING LOGIC
# ----------------------------------------------------------------------
def match_disease(extracted_symptoms):

    matches = []

    for disease, req_symptoms in DISEASE_KB.items():
        score = sum(1 for s in extracted_symptoms if s.lower() in [x.lower() for x in req_symptoms])

        if score > 0:
            matches.append({
                "disease": disease,
                "score": score,
                "required": req_symptoms,
                "matched": [s for s in extracted_symptoms if s in req_symptoms]
            })

    # Sort by highest match score
    matches = sorted(matches, key=lambda x: x["score"], reverse=True)

    return matches


# ----------------------------------------------------------------------
# SYMPTOM EXPLANATION
# ----------------------------------------------------------------------
def explain_symptoms(extracted_symptoms):
    explanations = []

    for sym in extracted_symptoms:
        if sym in SYMPTOM_EXPLANATION:
            explanations.append(f"{sym}: {SYMPTOM_EXPLANATION[sym]}")
    
    return explanations
