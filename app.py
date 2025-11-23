import streamlit as st
import sqlite3

# --------- Database Setup ----------
def init_db():
    conn = sqlite3.connect("healthcare.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            symptoms TEXT,
            bp TEXT,
            heart_rate TEXT,
            temperature TEXT,
            risk_score TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --------- Health Risk Calculation ----------
def calculate_risk(bp, heart_rate, temp):
    risk = 0

    # BP
    try:
        systolic, diastolic = map(int, bp.split("/"))
        if systolic > 140 or diastolic > 90:
            risk += 3
        elif systolic > 120:
            risk += 2
        else:
            risk += 1
    except:
        risk += 1

    # Heart Rate
    hr = int(heart_rate)
    if hr > 100 or hr < 60:
        risk += 3
    else:
        risk += 1

    # Temperature
    t = float(temp)
    if t > 38:
        risk += 3
    elif t > 37:
        risk += 2
    else:
        risk += 1

    if risk <= 3:
        return "Low"
    elif risk <= 6:
        return "Moderate"
    else:
        return "High"


# ---------- UI ------------
st.markdown("<h1 style='text-align: center; color:#4A4A4A;'>🩺 Healthcare Monitoring AI Agent</h1>", unsafe_allow_html=True)
st.write("<p style='text-align: center;'>A simple and intelligent system to analyze symptoms & vital signs.</p>", unsafe_allow_html=True)

st.write("Enter your symptoms and vitals to check your health status.")

name = st.text_input("Full Name")
age = st.number_input("Age", min_value=1, max_value=120)
symptoms = st.text_area("Describe your symptoms")
bp = st.text_input("Blood Pressure (e.g., 120/80)")
heart_rate = st.text_input("Heart Rate (bpm)")
temperature = st.text_input("Body Temperature (°C)")

# ---------- Analyze Button ----------
if st.button("Analyze Health"):

    if name and symptoms and bp and heart_rate and temperature:

        risk = calculate_risk(bp, heart_rate, temperature)

        st.subheader("🧪 Health Analysis Result")

        if risk == "Low":
            st.success("🟢 Risk Level: LOW — You seem stable, but monitor symptoms.")
        elif risk == "Moderate":
            st.warning("🟡 Risk Level: MODERATE — Some values are concerning. Keep an eye on changes.")
        else:
            st.error("🔴 Risk Level: HIGH — Consider consulting a doctor.")

        # Save to database
        conn = sqlite3.connect("healthcare.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO patients (name, age, symptoms, bp, heart_rate, temperature, risk_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, age, symptoms, bp, heart_rate, temperature, risk)
        )
        conn.commit()
        conn.close()

        st.success("✔ Health data stored and analyzed successfully!")

    else:
        st.error("Please fill all fields.")


# ---------- Symptom Helper ----------
st.markdown("---")
st.header("🤖 AI Symptom Helper (Basic Version)")

user_question = st.text_input("Ask about a symptom (e.g., headache, fever, cough):")

basic_medical_facts = {
    "fever": "A fever is a temporary rise in body temperature. Usually indicates infection.",
    "cough": "A cough helps clear your airways. Persistent cough may indicate infection.",
    "headache": "Headaches can be caused by stress, dehydration, or lack of sleep.",
    "cold": "Common cold includes runny nose, sneezing, sore throat.",
    "stomach pain": "Can be due to gas, acidity, or infection."
}

if st.button("Get Explanation"):
    found = False
    for key in basic_medical_facts:
        if key in user_question.lower():
            st.success(basic_medical_facts[key])
            found = True
            break

    if not found:
        st.info("No specific information found. Please try another symptom.")


# ---------- View Stored Records ----------
st.markdown("---")
st.header("📋 View Stored Health Records")

if st.button("Load Patient Records"):
    conn = sqlite3.connect("healthcare.db")
    c = conn.cursor()
    c.execute("SELECT name, age, symptoms, bp, heart_rate, temperature, risk_score FROM patients")
    rows = c.fetchall()
    conn.close()

    if len(rows) == 0:
        st.info("No patient records found yet.")
    else:
        for row in rows:
            st.write(f"**Name:** {row[0]}")
            st.write(f"**Age:** {row[1]}")
            st.write(f"**Symptoms:** {row[2]}")
            st.write(f"**BP:** {row[3]}")
            st.write(f"**Heart Rate:** {row[4]}")
            st.write(f"**Temperature:** {row[5]}")
            st.write(f"**Risk Level:** {row[6]}")
            st.markdown("---")
