# agent/disease_matcher.py

"""
Disease matcher: takes extracted symptoms and ranks diseases
based on how many symptoms match.
This is like "job requirement matching" but for health.
"""

# Knowledge base: each disease mapped to a list of key symptoms
DISEASE_KB = {
    "Common Cold": [
        "cold", "sneezing", "running nose", "cough", "headache"
    ],
    "Viral Fever": [
        "fever", "chills", "body pain", "headache", "fatigue"
    ],
    "Dengue (suspected)": [
        "fever", "chills", "body pain", "vomiting", "rash"
    ],
    "Hypertension (High BP)": [
        "high bp", "headache", "dizziness", "chest pain"
    ],
    "Hypotension (Low BP)": [
        "low bp", "dizziness", "weakness", "fatigue"
    ],
    "Acid Reflux / Gastritis": [
        "heartburn", "abdominal pain", "vomiting", "nausea"
    ],
    "Asthma / Breathing Issue": [
        "breathlessness", "cough", "chest pain"
    ],
    "Stomach Infection": [
        "vomiting", "diarrhea", "abdominal pain", "fever"
    ],
    "Allergic Reaction": [
        "rash", "itching", "sneezing", "running nose"
    ],
}


def rank_diseases(extracted_symptoms, min_score: int = 1):
    """
    Given a list of normalized symptoms (like 'fever', 'cough'),
    return a list of diseases sorted by how many symptoms match.
    """
    extracted_set = set(extracted_symptoms)
    results = []

    for disease, symptoms in DISEASE_KB.items():
        s_set = set(symptoms)
        score = len(extracted_set & s_set)  # how many symptoms overlapped

        if score >= min_score:
            coverage = score / len(s_set)
            results.append({
                "disease": disease,
                "score": score,
                "coverage": coverage,
                "matched_symptoms": list(extracted_set & s_set),
            })

    # Sort: highest score first, then better coverage
    results.sort(key=lambda x: (x["score"], x["coverage"]), reverse=True)
    return results
