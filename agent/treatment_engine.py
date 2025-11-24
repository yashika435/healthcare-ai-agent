# agent/treatment_engine.py

def get_care_tips(extracted_symptoms, top_disease_name=None):
    tips = []

    if "fever" in extracted_symptoms:
        tips.append("Drink plenty of water and rest in a cool, comfortable room.")
        tips.append("Use a clean cloth dipped in cool water on the forehead if needed.")

    if "cough" in extracted_symptoms:
        tips.append("Avoid cold drinks and ice cream.")
        tips.append("You may try warm water and steam inhalation.")

    if "vomiting" in extracted_symptoms or "diarrhea" in extracted_symptoms:
        tips.append("Take frequent small sips of ORS or electrolyte solution.")
        tips.append("Avoid oily, spicy and outside food.")

    if "headache" in extracted_symptoms:
        tips.append("Rest in a quiet, dark room and avoid screen time.")
    
    if "chest pain" in extracted_symptoms or "breathlessness" in extracted_symptoms:
        tips.append("Avoid physical exertion and sit upright.")
        tips.append("Seek urgent medical attention if symptoms worsen.")

    # Disease-specific general advice (non-prescriptive, general lifestyle only)
    if top_disease_name:
        if "Hypertension" in top_disease_name:
            tips.append("Reduce salt intake and avoid stress where possible.")
        if "Stomach Infection" in top_disease_name or "Gastritis" in top_disease_name:
            tips.append("Avoid street food and drink only clean, safe water.")
        if "Allergic" in top_disease_name:
            tips.append("Try to identify and avoid known triggers like dust or certain foods.")

    # Fallback if nothing was added
    if not tips:
        tips.append("Maintain good hydration and take adequate rest.")
        tips.append("If symptoms worsen or do not improve, consult a doctor.")

    return tips
