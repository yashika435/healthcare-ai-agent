def analyze_vitals(bp, heart_rate, temp):
    issues = []
    risk = 0

    # Blood Pressure
    try:
        systolic, diastolic = map(int, bp.split("/"))
        if systolic > 140 or diastolic > 90:
            issues.append("High blood pressure detected")
            risk += 3
        elif systolic < 90 or diastolic < 60:
            issues.append("Low blood pressure detected")
            risk += 2
        else:
            issues.append("Blood pressure normal")
            risk += 1
    except:
        issues.append("Invalid BP format")
        risk += 1

    # Heart rate
    try:
        hr = int(heart_rate)
        if hr > 100:
            issues.append("High heart rate (tachycardia)")
            risk += 3
        elif hr < 60:
            issues.append("Low heart rate (bradycardia)")
            risk += 2
        else:
            issues.append("Normal heart rate")
            risk += 1
    except:
        issues.append("Invalid heart rate value")
        risk += 1

    # Temperature
    try:
        t = float(temp)
        if t > 38:
            issues.append("High fever detected")
            risk += 3
        elif t > 37:
            issues.append("Mild fever")
            risk += 2
        else:
            issues.append("Normal temperature")
            risk += 1
    except:
        issues.append("Invalid temperature value")
        risk += 1

    # Risk Level
    if risk <= 4:
        return "Low", issues
    elif risk <= 7:
        return "Moderate", issues
    else:
        return "High", issues


def match_disease(symptoms):
    s = symptoms.lower()
    possible = []

    if any(x in s for x in ["fever", "chills", "headache"]):
        possible.append("Viral Infection / Flu")

    if any(x in s for x in ["vomit", "nausea", "diarrhea"]):
        possible.append("Food Poisoning")

    if any(x in s for x in ["cough", "breath", "wheezing"]):
        possible.append("Respiratory Infection / Asthma")

    if any(x in s for x in ["chest pain", "pressure", "tightness"]):
        possible.append("Possible Heart Issue (Seek urgent care)")

    if any(x in s for x in ["fatigue", "weakness"]):
        possible.append("Anemia / Thyroid / Vitamin Deficiency")

    if not possible:
        possible.append("No match — needs more detailed symptoms")

    return possible
